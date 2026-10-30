"""All agent filesystem effects go to the laptop control-plane over ssh (single source of truth)."""
from __future__ import annotations
import asyncio, json, shlex, subprocess
from . import config

BASE = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", config.SSH_HOST]


async def _exec(cmd: list[str], stdin: str | None, timeout: int) -> subprocess.CompletedProcess:
    return await asyncio.to_thread(subprocess.run, cmd, input=stdin, capture_output=True,
                                   text=True, timeout=timeout)


async def run(remote_cmd: str, timeout: int = 60) -> subprocess.CompletedProcess:
    return await _exec(BASE + [remote_cmd], None, timeout)


def _expand(path: str) -> str:
    import os
    return os.path.expanduser(path)


async def append(path: str, text: str) -> bool:
    q = shlex.quote(_expand(path))
    return (await _exec(BASE + [f"mkdir -p $(dirname {q}) && cat >> {q}"], text, 60)).returncode == 0


async def write(path: str, text: str) -> bool:
    q = shlex.quote(_expand(path))
    return (await _exec(BASE + [f"mkdir -p $(dirname {q}) && cat > {q}"], text, 60)).returncode == 0


async def read(path: str, timeout: int = 30) -> str | None:
    p = await run(f"cat {shlex.quote(_expand(path))} 2>/dev/null", timeout=timeout)
    return p.stdout if p.returncode == 0 else None


async def run_py(script: str, payload: dict, timeout: int = 60) -> dict:
    """Execute python with payload in env PAYLOAD; expect a JSON object on stdout."""
    payload_s = json.dumps(payload)
    lib = "/Users/rig128gb/.rig/live/lib"
    env = ("PAYLOAD=" + shlex.quote(payload_s)
           + " PYTHONPATH=" + shlex.quote(lib))
    p = await _exec(BASE + [f"{env} python3 -"], script, timeout)
    if p.returncode != 0:
        return {"ok": False, "error": (p.stderr or p.stdout)[-500:]}
    try:
        return json.loads(p.stdout)
    except Exception as ex:
        return {"ok": False, "error": f"bad json: {ex} :: {p.stdout[:300]}"}


async def touch(path: str) -> bool:
    q = shlex.quote(_expand(path))
    return (await run(f"mkdir -p $(dirname {q}) && touch {q}")).returncode == 0
