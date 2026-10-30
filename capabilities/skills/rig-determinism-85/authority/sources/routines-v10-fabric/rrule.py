"""RRULE subset expander for Aside routine schedules.

Supports the grammar actually in use in ~/.aside/u/0/state.db:
  FREQ=MINUTELY|HOURLY|DAILY|WEEKLY|MONTHLY, INTERVAL, BYMINUTE, BYHOUR,
  BYDAY (weekday names, MO-FR ranges, nth-weekday like 1MO/-1FR),
  BYMONTHDAY, BYMONTH, COUNT, UNTIL (UTC Z form). WKST is ignored (MO).
DTSTART may be `DTSTART;TZID=America/Denver:YYYYMMDDTHHMMSS` or bare-UTC
`DTSTART:YYYYMMDDTHHMMSSZ`. Returned datetimes are tz-aware; America/Denver
wall-clock expansion (zoneinfo handles DST).
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Denver")
UTC = timezone.utc
WD = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
WDN = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]

_DT_RE = re.compile(
    r"DTSTART(?P<tz>;TZID=(?P<zone>[A-Za-z_/+]+))?:(?P<stamp>\d{8}T\d{6})(?P<z>Z)?"
)
_RR_RE = re.compile(r"RRULE:(.+)")
_UNTIL_RE = re.compile(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z?")


class RuleError(ValueError):
    pass


def parse(text: str):
    """Return (dtstart_aware, parts dict)."""
    dm = _DT_RE.search(text)
    if not dm:
        raise RuleError(f"no DTSTART in {text!r}")
    stamp = dm.group("stamp")
    y, mo, d = int(stamp[0:4]), int(stamp[4:6]), int(stamp[6:8])
    h, mi, s = int(stamp[9:11]), int(stamp[11:13]), int(stamp[13:15])
    dtstart = datetime(y, mo, d, h, mi, s, tzinfo=UTC if dm.group("z") else TZ)
    rm = _RR_RE.search(text)
    if not rm:
        raise RuleError(f"no RRULE in {text!r}")
    parts = {}
    for kv in rm.group(1).strip().split(";"):
        if "=" in kv:
            k, v = kv.split("=", 1)
            parts[k.strip()] = v.strip()
    return dtstart, parts


def _ints(v):
    return [int(x) for x in v.split(",") if x != ""]


def _byday(v):
    """'MO,WE,FR' | 'MO-FR' | '1MO,-1FR' -> [(nth_or_None, weekday_int), ...]"""
    out = []
    for tok in v.split(","):
        tok = tok.strip()
        if not tok:
            continue
        if re.fullmatch(r"[A-Z]{2}-[A-Z]{2}", tok):
            a, b = tok.split("-")
            k, j = WD[a], WD[b]
            while True:
                out.append((None, k))
                if k == j:
                    break
                k = (k + 1) % 7
            continue
        m = re.fullmatch(r"([+-]?\d+)?([A-Z]{2})", tok)
        if not m or m.group(2) not in WD:
            raise RuleError(f"bad BYDAY token {tok!r}")
        nth = int(m.group(1)) if m.group(1) else None
        out.append((nth, WD[m.group(2)]))
    return out


def _month_len(y: int, m: int) -> int:
    nxt = datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)
    return (nxt - datetime(y, m, 1)).days


def _month_nth_weekday(y: int, m: int, nth: int, wd: int):
    ml = _month_len(y, m)
    if nth > 0:
        delta = (wd - datetime(y, m, 1).weekday()) % 7
        day = 1 + delta + (nth - 1) * 7
        return day if day <= ml else None
    delta = (datetime(y, m, ml).weekday() - wd) % 7
    day = ml - delta + (nth + 1) * 7
    return day if day >= 1 else None


def _incremental(text: str, hard_limit: int = 2_000_000):
    """Yield occurrences (tz-aware) lazily in schedule order."""
    dtstart, parts = parse(text)
    freq = parts.get("FREQ")
    interval = int(parts.get("INTERVAL", "1") or 1)
    if interval < 1:
        raise RuleError(f"bad INTERVAL in {text!r}")
    count = int(parts["COUNT"]) if "COUNT" in parts else None
    until = None
    if "UNTIL" in parts:
        um = _UNTIL_RE.fullmatch(parts["UNTIL"])
        if not um:
            raise RuleError(f"bad UNTIL {parts['UNTIL']!r}")
        until = datetime(*(int(x) for x in um.groups()), tzinfo=UTC)
    byminute = _ints(parts["BYMINUTE"]) if "BYMINUTE" in parts else None
    byhour = _ints(parts["BYHOUR"]) if "BYHOUR" in parts else None
    bymonthday = _ints(parts["BYMONTHDAY"]) if "BYMONTHDAY" in parts else None
    bymonth = _ints(parts["BYMONTH"]) if "BYMONTH" in parts else None
    byday = _byday(parts["BYDAY"]) if "BYDAY" in parts else None
    minutes = byminute if byminute is not None else [dtstart.minute]
    hours = byhour if byhour is not None else [dtstart.hour]
    tod = sorted((h, m) for h in hours for m in minutes)

    emitted = 0
    produced = 0

    def sink(t: datetime):
        """Return the datetime to emit, 'stop' to end, or None to skip."""
        nonlocal emitted, produced
        if t < dtstart:
            return None
        if until is not None and t.astimezone(UTC) > until:
            return "stop"
        if bymonth is not None and t.month not in bymonth:
            return None
        emitted += 1
        if count is not None and emitted > count:
            return "stop"
        produced += 1
        if produced > hard_limit:
            raise RuleError(f"expansion cap exceeded for {text!r}")
        return t

    if freq == "MINUTELY":
        k = 0
        while True:
            t = dtstart + timedelta(minutes=interval * k)
            k += 1
            if byminute is not None and t.minute not in byminute:
                continue
            if byhour is not None and t.hour not in byhour:
                continue
            if byday is not None and (None, t.weekday()) not in byday:
                continue
            r = sink(t)
            if r == "stop":
                return
            if r is not None:
                yield r
    elif freq == "HOURLY":
        k = 0
        while True:
            h = dtstart + timedelta(hours=interval * k)
            k += 1
            if byhour is not None and h.hour not in byhour:
                continue
            if byday is not None and (None, h.weekday()) not in byday:
                continue
            for m in minutes:
                r = sink(h.replace(minute=m, second=dtstart.second, microsecond=0))
                if r == "stop":
                    return
                if r is not None:
                    yield r
    elif freq == "DAILY":
        k = 0
        while True:
            day = dtstart + timedelta(days=interval * k)
            k += 1
            if byday is not None and (None, day.weekday()) not in byday:
                continue
            for h, m in tod:
                r = sink(day.replace(hour=h, minute=m, second=dtstart.second, microsecond=0))
                if r == "stop":
                    return
                if r is not None:
                    yield r
    elif freq == "WEEKLY":
        week_start = dtstart.date() - timedelta(days=dtstart.weekday())
        wdays = sorted(set(w for _, w in (byday if byday is not None else [(None, dtstart.weekday())])))
        k = 0
        while True:
            ws = week_start + timedelta(weeks=interval * k)
            k += 1
            for w in wdays:
                day = ws + timedelta(days=w)
                for h, m in tod:
                    r = sink(datetime(day.year, day.month, day.day, h, m,
                                      dtstart.second, tzinfo=dtstart.tzinfo))
                    if r == "stop":
                        return
                    if r is not None:
                        yield r
    elif freq == "MONTHLY":
        y, mo = dtstart.year, dtstart.month
        k = 0
        while True:
            mm = mo + interval * k
            yy = y + (mm - 1) // 12
            mm = (mm - 1) % 12 + 1
            k += 1
            ml = _month_len(yy, mm)
            days = set()
            if bymonthday is not None:
                for d in bymonthday:
                    dd = d if d > 0 else ml + 1 + d
                    if 1 <= dd <= ml:
                        days.add(dd)
            elif byday is not None:
                for nth, w in byday:
                    if nth is None:
                        days.update(d for d in range(1, ml + 1)
                                    if datetime(yy, mm, d).weekday() == w)
                    else:
                        dd = _month_nth_weekday(yy, mm, nth, w)
                        if dd:
                            days.add(dd)
            elif dtstart.day <= ml:
                days.add(dtstart.day)
            for d in sorted(days):
                for h, m in tod:
                    r = sink(datetime(yy, mm, d, h, m, dtstart.second,
                                      tzinfo=dtstart.tzinfo))
                    if r == "stop":
                        return
                    if r is not None:
                        yield r
    else:
        raise RuleError(f"unsupported FREQ {freq!r}")


def occurrences(text: str, hard_limit: int = 2_000_000):
    """Yield every occurrence (tz-aware) in schedule order."""
    yield from _incremental(text, hard_limit=hard_limit)


def next_fire(text: str, now: datetime | None = None) -> datetime | None:
    """First occurrence strictly after `now` (default now, America/Denver)."""
    now = (now if now is not None else datetime.now(TZ)).astimezone(TZ)
    for t in occurrences(text):
        if t > now:
            return t
    return None


def between(text: str, start: datetime, end: datetime):
    """Occurrences in [start, end)."""
    start = start.astimezone(TZ)
    end = end.astimezone(TZ)
    for t in occurrences(text):
        if t >= end:
            return
        if t >= start:
            yield t


def to_iso_utc(t: datetime) -> str:
    """Format like the daemon's next_run_at: 2026-10-24T06:30:00.000Z"""
    return t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def from_iso_utc(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)


def shift(text: str, delta_minutes: int) -> str:
    """Shift the rule's minute-of-hour timeslot by delta minutes.

    Only valid when every resulting minute stays within [0, 59] (no wrap), so
    BYHOUR bindings keep their meaning. Raises RuleError on wrap.
    """
    if delta_minutes == 0:
        return text
    out = []
    for line in text.split("\n"):
        if line.startswith("RRULE:") and "BYMINUTE=" in line:
            def repl(m):
                vals = [int(x) for x in m.group(1).split(",")]
                nv = [v + delta_minutes for v in vals]
                if any(v > 59 or v < 0 for v in nv):
                    raise RuleError(f"shift {delta_minutes} would wrap BYMINUTE {vals}")
                return "BYMINUTE=" + ",".join(str(v) for v in nv)
            line = re.sub(r"BYMINUTE=([0-9,]+)", repl, line)
        elif line.startswith("DTSTART"):
            dm = _DT_RE.search(line)
            if not dm:
                raise RuleError(f"bad DTSTART line {line!r}")
            stamp = dm.group("stamp")
            y, mo, d = int(stamp[0:4]), int(stamp[4:6]), int(stamp[6:8])
            h, mi, s = int(stamp[9:11]), int(stamp[11:13]), int(stamp[13:15])
            base = datetime(y, mo, d, h, mi, s, tzinfo=UTC if dm.group("z") else TZ)
            shifted = base + timedelta(minutes=delta_minutes)
            if dm.group("z"):
                line = "DTSTART:" + shifted.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
            else:
                line = f"DTSTART;TZID={dm.group('zone')}:" + shifted.strftime("%Y%m%dT%H%M%S")
        out.append(line)
    return "\n".join(out)
