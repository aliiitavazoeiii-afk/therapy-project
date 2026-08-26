from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Therapy Project", version="0.1.0")
WEB = Path(__file__).resolve().parents[2] / "web"

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "therapy-project"}

@app.get("/api/bootstrap")
def bootstrap():
    return {
        "phase": "alpha",
        "ai_connected": False,
        "clinical_team": ["therapist", "formulation", "supervisor", "memory", "outcome_progress", "safety"],
        "principle": "present-state first; treatment-state always preserved",
    }

if WEB.exists():
    app.mount("/assets", StaticFiles(directory=WEB / "assets"), name="assets")

@app.get("/{path:path}")
def spa(path: str):
    return FileResponse(WEB / "index.html")
