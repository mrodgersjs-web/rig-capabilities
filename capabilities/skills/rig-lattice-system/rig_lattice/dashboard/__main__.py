"""Run with: python -m dashboard"""
from rig_lattice.dashboard.app import app  # noqa: F401

if __name__ == "__main__":
    import os
    import uvicorn
    uvicorn.run(
        "dashboard.app:app",
        host=os.environ.get("RIG_DV_DASHBOARD_HOST", "127.0.0.1"),
        port=int(os.environ.get("RIG_DV_DASHBOARD_PORT", "8088")),
        log_level="info",
    )
