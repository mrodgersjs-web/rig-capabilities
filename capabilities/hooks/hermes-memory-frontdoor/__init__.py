"""RIG_MEMORY_FRONTDOOR_V1. No retrieved text is promoted to system context."""
import json
import subprocess
import sys
sys.path.insert(0,"/Users/rig128gb/Developer/rig-intelligence/platform/knowledge-context-hook")
from task_context.bounded import run as bounded_run
PYTHON = '/Users/rig128gb/Developer/RIG-Memory-OS/.venv/bin/python'
ADAPTER = '/Users/rig128gb/Developer/rig-intelligence/platform/knowledge-context-hook/memory_fleet.py'

def invoke(event, value):
    try:
        result = bounded_run([PYTHON, ADAPTER, '--runtime', 'hermes', '--event', event],
                                input=json.dumps(value), capture_output=True, text=True, timeout=32)
        if result.returncode:
            raise ValueError('adapter failed')
        return json.loads(result.stdout)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return {'status': 'error', 'metadata': 'Memory OS unavailable; retry next turn.',
                'reference_text': 'Memory OS unavailable; retry next turn. No direct backend fallback.'}

def startup(**kwargs):
    result = invoke('startup', {})
    # This hook is an observer. No inference is launched and no body is injected.
    if result.get('status') != 'ok':
        import logging
        logging.getLogger(__name__).warning(result.get('metadata', 'Memory OS startup failed'))

def turn(**kwargs):
    result = invoke('turn', {'user_message': kwargs.get('user_message', '')})
    return {'context': result.get('reference_text') or result.get('metadata')}

def register(ctx):
    ctx.register_hook('on_session_start', startup)
    ctx.register_hook('pre_llm_call', turn)
