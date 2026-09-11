"""Parameterized activation worker for the jarvis_blackwell process.

All effect payloads (paths, bytes, commands) arrive as positional inputs at
Gate-D execution time; no literals are baked into this module.
"""

import subprocess


def write_config(path, content):
    handle = open(path, "w")
    count = handle.write(content)
    closed = handle.close()
    return (count, closed)


def restart_service(arguments):
    return subprocess.call(arguments)


def quit_app(arguments):
    return subprocess.call(arguments)


def activate(config_path, config_content, kickstart_arguments, quit_arguments):
    written = write_config(config_path, config_content)
    status = restart_service(kickstart_arguments)
    quit_status = quit_app(quit_arguments)
    return (written, status, quit_status)
