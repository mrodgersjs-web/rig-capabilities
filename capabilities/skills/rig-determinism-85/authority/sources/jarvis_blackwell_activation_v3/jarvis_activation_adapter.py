"""Adapter exposing the jarvis_blackwell activation operation (v3)."""

from jarvis_activation_worker import activate


def execute(transaction_arguments, quit_arguments):
    return activate(transaction_arguments, quit_arguments)
