"""Adapter exposing the jarvis_blackwell activation operation (v6)."""

from jarvis_activation_worker import activate


def execute(transaction_arguments):
    return activate(transaction_arguments)
