#!/bin/sh
# Wire the rig-capabilities MCP server into all five harnesses.
# Defaults to dry-run; pass --apply or --verify. Requires python3 (3.9+).
exec python3 "$(dirname "$0")/wire/wire.py" "$@"
