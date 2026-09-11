"""Parameterized activation worker for the jarvis_blackwell process (v2).

All effect payloads arrive as positional inputs at Gate-D execution time.
File mutation is a staged-file copy through the pinned subprocess module: the
grammar admits no method calls on locally constructed objects, so open/write/
close is unrepresentable (v1 BLOCK: SOURCE_DYNAMIC_CALL shadowed handle).
"""

import subprocess


def copy_file(arguments):
    return subprocess.call(arguments)


def restart_service(arguments):
    return subprocess.call(arguments)


def quit_app(arguments):
    return subprocess.call(arguments)


def activate(copy_arguments, kickstart_arguments, quit_arguments):
    copied = copy_file(copy_arguments)
    status = restart_service(kickstart_arguments)
    quit_status = quit_app(quit_arguments)
    return (copied, status, quit_status)
