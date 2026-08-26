from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Therapy Project", version="0.1.1")

# In production Docker images the Python package is installed into site-packages,
# while the web bundle is copied to /app/web. Resolve from the process working
# directory first so deployment does not depend on the package installation path.
WEB = Path.cwd() / "web"
INDEX = WEB / "index.html"
ASSETS = WEB / "assets"


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "therapy-project",
        "web_ready": INDEX.is_file(),
    }


@app.get("/api/bootstrap")
def bootstrap():
    return {
        "phase": "alpha",
        "ai_connected": False,
        "clinical_team": [
            "therapist",
            "formulation",
            "supervisor",
            "memory",
            "outcome_progress",
            "safety",
        ],
        "principle": "present-state first; treatment-state always preserved",
    }


if ASSETS.is_dir():
    app.mount("/assets", StaticFiles(directory=ASSETS), name="assets")


@app.get("/{path:path}")
def spa(path: str):
    if not INDEX.is_file():
        return {
            "status": "error",
            "detail": "Web bundle is missing from the application image.",
            "expected_path": str(INDEX),
        }
    return FileResponse(INDEX)
