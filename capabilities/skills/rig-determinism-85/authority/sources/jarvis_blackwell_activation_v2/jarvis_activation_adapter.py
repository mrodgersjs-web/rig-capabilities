"""Adapter exposing the jarvis_blackwell activation operation (v2)."""

from jarvis_activation_worker import activate


def execute(copy_arguments, kickstart_arguments, quit_arguments):
    return activate(copy_arguments, kickstart_arguments, quit_arguments)
