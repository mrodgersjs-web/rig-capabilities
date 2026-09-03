"""Enterprise Notification — Slack webhook + email + Telegram + local-fallback.

Per LinkedIn Studio template Notification subsystem. Routes alerts to the
configured channel based on severity:
  - INFO     → local log only (audits/notifications.jsonl)
  - WARN     → Slack #rig-deviator-warn (if SLACK_WEBHOOK_URL set)
  - CRITICAL → Slack #rig-deviator-critical + email + Telegram

Channel configuration via environment variables:
  - RIG_DV_SLACK_WEBHOOK_URL        — for WARN + CRITICAL
  - RIG_DV_SLACK_WEBHOOK_CRITICAL   — overrides for CRITICAL only
  - RIG_DV_NOTIFY_EMAIL             — destination address(es), comma-sep
  - RIG_DV_NOTIFY_EMAIL_FROM        — from address (defaults to user@host)
  - RIG_DV_SMTP_HOST                — SMTP host (defaults to localhost)
  - RIG_DV_SMTP_PORT                — defaults to 25
  - RIG_DV_SMTP_USER / _PASS        — auth (optional)
  - RIG_DV_TELEGRAM_BOT_TOKEN       — Telegram bot token
  - RIG_DV_TELEGRAM_CHAT_ID         — destination chat

Every notification writes a forensic row to audits/notifications.jsonl even
if all delivery channels fail. The framework never crashes a pipeline run
because a webhook timed out.
"""
from __future__ import annotations
import json
import os
import smtplib
import socket
import time
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any
from urllib import request as ur
from rig_lattice._paths import AUDITS_DIR

ROOT = Path(__file__).parent.parent
NOTIFY_LOG = AUDITS_DIR / "notifications.jsonl"

# Default timeouts
_HTTP_TIMEOUT = int(os.environ.get("RIG_DV_NOTIFY_TIMEOUT", "8"))


@dataclass
class NotifyResult:
    ts_utc: str
    severity: str
    title: str
    message: str
    channels_attempted: list[str]
    channels_delivered: list[str]
    channels_failed: dict[str, str]      # channel → error
    payload_extra: dict[str, Any] | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _log_local(result: NotifyResult) -> None:
    NOTIFY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with NOTIFY_LOG.open("a") as f:
        f.write(json.dumps(result.to_dict(), default=str) + "\n")


# ── Slack webhook ────────────────────────────────────────────────────────
def _slack_webhook_for(severity: str) -> str | None:
    if severity == "critical":
        return (os.environ.get("RIG_DV_SLACK_WEBHOOK_CRITICAL")
                or os.environ.get("RIG_DV_SLACK_WEBHOOK_URL"))
    return os.environ.get("RIG_DV_SLACK_WEBHOOK_URL")


def _send_slack(severity: str, title: str, message: str,
                 extra: dict | None = None) -> tuple[bool, str]:
    webhook = _slack_webhook_for(severity)
    if not webhook:
        return False, "no_webhook_configured"

    sev_emoji = {"info": ":information_source:", "warn": ":warning:",
                  "critical": ":rotating_light:"}.get(severity, ":bell:")
    color = {"info": "#36a64f", "warn": "#FFA500",
              "critical": "#FF0000"}.get(severity, "#888888")

    blocks = [
        {"type": "header", "text": {"type": "plain_text",
                                       "text": f"{sev_emoji} RIG Deviator — {title}"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": message}},
    ]
    if extra:
        fields = [{"type": "mrkdwn", "text": f"*{k}:*\n{v}"} for k, v in extra.items() if v is not None]
        if fields:
            blocks.append({"type": "section", "fields": fields[:10]})
    blocks.append({
        "type": "context",
        "elements": [{"type": "mrkdwn",
                       "text": f"_{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}_  •  host: `{socket.gethostname()}`"}],
    })

    payload = {
        "text": f"[{severity.upper()}] {title} — {message[:200]}",
        "attachments": [{"color": color, "blocks": blocks}],
    }
    try:
        req = ur.Request(webhook,
                         data=json.dumps(payload).encode("utf-8"),
                         headers={"Content-Type": "application/json"},
                         method="POST")
        with ur.urlopen(req, timeout=_HTTP_TIMEOUT) as r:
            body = r.read().decode("utf-8")
        return True, body or "ok"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


# ── Email (SMTP) ─────────────────────────────────────────────────────────
def _send_email(severity: str, title: str, message: str,
                 extra: dict | None = None) -> tuple[bool, str]:
    dests = os.environ.get("RIG_DV_NOTIFY_EMAIL", "")
    if not dests:
        return False, "no_email_configured"
    dest_list = [d.strip() for d in dests.split(",") if d.strip()]
    if not dest_list:
        return False, "no_email_configured"

    sender = (os.environ.get("RIG_DV_NOTIFY_EMAIL_FROM")
               or f"rig-deviator@{socket.gethostname()}")
    host = os.environ.get("RIG_DV_SMTP_HOST", "localhost")
    port = int(os.environ.get("RIG_DV_SMTP_PORT", "25"))
    user = os.environ.get("RIG_DV_SMTP_USER")
    password = os.environ.get("RIG_DV_SMTP_PASS")

    body_lines = [f"Severity: {severity.upper()}", f"Title: {title}", "", message]
    if extra:
        body_lines.extend(["", "Context:"])
        for k, v in extra.items():
            body_lines.append(f"  {k}: {v}")
    body_lines.append("")
    body_lines.append(f"host: {socket.gethostname()}")
    body_lines.append(f"ts:   {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")

    msg = MIMEText("\n".join(body_lines))
    msg["Subject"] = f"[RIG Deviator {severity.upper()}] {title}"
    msg["From"] = sender
    msg["To"] = ", ".join(dest_list)

    try:
        if port == 465:
            client = smtplib.SMTP_SSL(host, port, timeout=_HTTP_TIMEOUT)
        else:
            client = smtplib.SMTP(host, port, timeout=_HTTP_TIMEOUT)
            try:
                client.starttls()
            except Exception:
                pass
        try:
            if user and password:
                client.login(user, password)
            client.sendmail(sender, dest_list, msg.as_string())
        finally:
            client.quit()
        return True, f"sent to {len(dest_list)}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


# ── Telegram ─────────────────────────────────────────────────────────────
def _send_telegram(severity: str, title: str, message: str,
                    extra: dict | None = None) -> tuple[bool, str]:
    token = os.environ.get("RIG_DV_TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("RIG_DV_TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False, "no_telegram_configured"

    text_lines = [f"*[{severity.upper()}]* {title}", "", message]
    if extra:
        text_lines.append("")
        for k, v in extra.items():
            text_lines.append(f"  • *{k}*: {v}")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "\n".join(text_lines)[:3900],   # Telegram 4096 char hard limit
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    try:
        req = ur.Request(url, data=json.dumps(payload).encode("utf-8"),
                         headers={"Content-Type": "application/json"},
                         method="POST")
        with ur.urlopen(req, timeout=_HTTP_TIMEOUT) as r:
            r.read()
        return True, "ok"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


# ── Public API ───────────────────────────────────────────────────────────
def notify(severity: str, title: str, message: str,
            *, extra: dict | None = None,
            force_channels: list[str] | None = None) -> NotifyResult:
    """Send a notification. Returns NotifyResult with per-channel status.

    Routing matrix (default):
      INFO     → local log only
      WARN     → local + Slack
      CRITICAL → local + Slack + email + Telegram

    `force_channels` overrides the default routing — useful for testing or
    when the operator wants to broadcast even an INFO event.
    """
    severity = severity.lower()
    if severity not in ("info", "warn", "critical"):
        severity = "info"

    if force_channels is not None:
        channels = list(force_channels)
    else:
        if severity == "critical":
            channels = ["slack", "email", "telegram"]
        elif severity == "warn":
            channels = ["slack"]
        else:
            channels = []   # local only

    delivered: list[str] = []
    failed: dict[str, str] = {}
    attempted = list(channels)
    senders = {
        "slack":    _send_slack,
        "email":    _send_email,
        "telegram": _send_telegram,
    }
    for ch in channels:
        sender = senders.get(ch)
        if not sender:
            failed[ch] = "unknown_channel"
            continue
        ok, msg = sender(severity, title, message, extra)
        if ok:
            delivered.append(ch)
        else:
            failed[ch] = msg

    result = NotifyResult(
        ts_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        severity=severity,
        title=title,
        message=message,
        channels_attempted=attempted,
        channels_delivered=delivered,
        channels_failed=failed,
        payload_extra=extra,
    )
    _log_local(result)
    return result


def channel_status() -> dict:
    """Diagnostic — show which channels are configured."""
    return {
        "slack_warn":      bool(os.environ.get("RIG_DV_SLACK_WEBHOOK_URL")),
        "slack_critical":  bool(os.environ.get("RIG_DV_SLACK_WEBHOOK_CRITICAL")
                                or os.environ.get("RIG_DV_SLACK_WEBHOOK_URL")),
        "email":           bool(os.environ.get("RIG_DV_NOTIFY_EMAIL")),
        "telegram":        bool(os.environ.get("RIG_DV_TELEGRAM_BOT_TOKEN")
                                and os.environ.get("RIG_DV_TELEGRAM_CHAT_ID")),
        "local_log":       True,
    }


# ── SRE integration ──────────────────────────────────────────────────────
def dispatch_alert(alert) -> NotifyResult:
    """Bridge from enterprise.sre.Alert → notification channels.

    Maps AlertSeverity → notify severity:
      AlertSeverity.INFO     → info     (local only)
      AlertSeverity.WARN     → warn     (Slack)
      AlertSeverity.CRITICAL → critical (Slack + email + Telegram)
    """
    sev_map = {"info": "info", "warn": "warn", "critical": "critical"}
    sev = sev_map.get(getattr(alert, "severity", "info").value
                      if hasattr(alert.severity, "value") else str(alert.severity),
                      "info")
    return notify(
        severity=sev,
        title=alert.name,
        message=alert.message,
        extra={
            "alert_name": alert.name,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                          time.gmtime(alert.timestamp)),
        },
    )
