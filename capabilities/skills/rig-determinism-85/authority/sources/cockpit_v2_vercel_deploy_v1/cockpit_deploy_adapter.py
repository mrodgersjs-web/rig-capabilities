"""Adapter exposing the cockpit-v2 vercel deploy operation (v1)."""

from cockpit_deploy_worker import deploy


def execute(transaction_arguments):
    return deploy(transaction_arguments)
