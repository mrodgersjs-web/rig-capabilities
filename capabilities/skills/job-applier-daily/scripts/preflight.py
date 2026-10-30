#!/usr/bin/env python3
"""Read-only tool discovery. Never starts Aside inference, a browser task or a schedule."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


def help_text(executable):
    """Aside truncates help with a zero-width pipe; use a bounded terminal width."""
    import fcntl
    import pty
    import select
    import struct
    import termios
    master,slave=pty.openpty()
    process=None
    output=[]
    try:
        fcntl.ioctl(slave,termios.TIOCSWINSZ,struct.pack('HHHH',40,120,0,0))
        process=subprocess.Popen([executable,'--help'],stdin=subprocess.DEVNULL,stdout=slave,stderr=slave)
        os.close(slave)
        slave=None
        deadline=time.monotonic()+15
        while time.monotonic()<deadline:
            ready,_,_=select.select([master],[],[],0.1)
            if ready:
                try:
                    chunk=os.read(master,65536)
                except OSError:
                    break
                if not chunk:break
                output.append(chunk)
            elif process.poll() is not None:break
        process.wait(timeout=max(.1,deadline-time.monotonic()))
        return process.returncode,b''.join(output).decode(errors='replace')
    finally:
        if process is not None and process.poll() is None:
            process.kill();process.wait()
        if slave is not None:os.close(slave)
        os.close(master)


def probe():
    aside=shutil.which('aside')
    result={'schema':'job-applier.preflight.v1','python_supported':sys.version_info >= (3,9),
            'aside_executable_found':bool(aside),'aside_help_verified':False,
            'jev_environment_key_present':bool(os.environ.get('TYPESAFE_API_KEY')),
            'jev_live_request_verified':False,'jev_image_live_request_verified':False,
            'airtable_live_schema_verified':False,'native_grokbot_import_verified':False,
            'scheduler_activated':False,'authorizes_submission':False}
    if aside:
        try:
            # A bare `aside help` is an inference prompt. Only --help is safe here.
            code,output=help_text(aside)
            result['aside_help_verified']=code==0 and 'exec' in output and '--help' in output
            result['aside_help_exit_code']=code
        except (ImportError,OSError,subprocess.TimeoutExpired):
            result['aside_help_error']='unavailable_or_timeout'
    result['render_tools']={name:bool(shutil.which(name)) for name in ('soffice','pdftoppm','pdfinfo')}
    result['libreoffice_app_present']=Path('/Applications/LibreOffice.app/Contents/MacOS/soffice').is_file()
    result['status']='DISCOVERY_ONLY'
    result['next_step']='Authenticate actual provider/account access and run a supervised preparation-only packet. Presence is not execution proof.'
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(probe(),indent=2))
