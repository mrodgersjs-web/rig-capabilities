"""Adapter exposing the jarvis_blackwell activation operation."""

from jarvis_activation_worker import activate


def execute(config_path, config_content, kickstart_arguments, quit_arguments):
    return activate(config_path, config_content, kickstart_arguments, quit_arguments)
