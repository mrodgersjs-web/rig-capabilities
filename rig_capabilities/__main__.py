"""`python -m rig_capabilities` — serve the capability MCP over stdio."""
from .server import build_server

if __name__ == "__main__":
    build_server().serve_forever()
