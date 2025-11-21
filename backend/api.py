"""FastAPI backend replacing the Streamlit UI."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from auth_manager import AuthManager
from backend.alert_service import move_to_verified_alerts
from backend.live_detection import LiveDetectionWorker, get_worker, get_worker_dual_1, get_worker_dual_2

app = FastAPI(title="CCTV Crime Detection API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_manager = AuthManager()
SESSIONS: Dict[str, Dict[str, Any]] = {}
SESSION_TTL = timedelta(hours=12)

# Support for dual camera streams
USE_DUAL_CAMERAS = False  # Set to True to enable 2-camera mode


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = Field("normal", pattern="^(admin|normal)$")


class LiveSettings(BaseModel):
    fps_target: int = 15
    crime_threshold: float = 0.35
    show_boxes: bool = True
    show_weapons: bool = True


class VerifyRequest(BaseModel):
    verified_by: str
    is_valid: int = 1


class LiveControl(BaseModel):
    active: bool


def create_session(username: str, role: str) -> str:
    token = uuid.uuid4().hex
    SESSIONS[token] = {
        "username": username,
        "role": role,
        "expires": datetime.utcnow() + SESSION_TTL,
    }
    return token


def resolve_user(authorization: Optional[str] = Header(default=None)) -> Dict[str, str]:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = authorization.replace("Bearer", "").strip()
    session = SESSIONS.get(token)
    if not session or session["expires"] < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    return {"username": session["username"], "role": session["role"], "token": token}


def resolve_admin(user=Depends(resolve_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return user


@app.get("/health")
def health() -> Dict[str, Any]:
    worker = get_worker()
    return {
        "status": "ok",
        "worker_running": worker.running,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/auth/login")
def login(payload: LoginRequest):
    success, username, role = auth_manager.login(payload.username, payload.password)
    if not success or not username or not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_session(username, role)
    return {"token": token, "username": username, "role": role}


@app.post("/auth/register")
def register(payload: RegisterRequest, user=Depends(resolve_admin)):
    success, message = auth_manager.register_user(payload.username, payload.password, role=payload.role)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {"message": message}


@app.get("/live/stats")
def live_stats():
    worker = get_worker()
    return worker.get_state()


@app.get("/live/frame")
def live_frame():
    worker = get_worker()
    frame = worker.get_frame_base64()
    # Return empty string instead of 404 to avoid frontend errors during initialization
    return {"frame": frame or ""}


@app.post("/live/settings")
def update_settings(settings: LiveSettings, user=Depends(resolve_admin)):
    worker = get_worker()
    worker.update_settings(
        fps_target=settings.fps_target,
        crime_threshold=settings.crime_threshold,
        show_boxes=settings.show_boxes,
        show_weapons=settings.show_weapons,
    )
    return {"message": "Settings updated"}


@app.post("/live/control")
def control_worker(control: LiveControl, user=Depends(resolve_admin)):
    worker = get_worker()
    if control.active and not worker.running:
        worker.start()
    elif not control.active and worker.running:
        worker.stop()
    return {"running": worker.running}


@app.get("/alerts/recent")
def recent_alerts(limit: int = 20):
    return _load_alerts(Path("alerts/metadata"), limit)


@app.get("/alerts/verified")
def verified_alerts(limit: int = 20):
    return _load_alerts(Path("verified_alerts/metadata"), limit)


@app.post("/alerts/{alert_id}/verify")
def verify_alert(alert_id: str, body: VerifyRequest, user=Depends(resolve_admin)):
    success = move_to_verified_alerts(alert_id, verified_by=body.verified_by or user["username"])
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Alert assets missing")
    auth_manager.verify_alert(alert_id, verified_by=body.verified_by or user["username"], is_valid=body.is_valid)
    return {"alert_id": alert_id, "status": "verified"}


@app.get("/alerts/live")
def live_alert_queue():
    worker = get_worker()
    return {"alerts": worker.flush_alerts()}


# ============ DUAL CAMERA ENDPOINTS ============

@app.get("/live/dual/stats")
def live_dual_stats():
    """Get stats from both cameras."""
    worker1 = get_worker_dual_1()
    worker2 = get_worker_dual_2()
    return {
        "camera_1": worker1.get_state(),
        "camera_2": worker2.get_state(),
    }


@app.get("/live/dual/frame/{camera_id}")
def live_dual_frame(camera_id: int):
    """Get frame from specific camera (1 or 2)."""
    if camera_id == 1:
        worker = get_worker_dual_1()
    elif camera_id == 2:
        worker = get_worker_dual_2()
    else:
        raise HTTPException(status_code=400, detail="camera_id must be 1 or 2")
    
    frame = worker.get_frame_base64()
    return {"frame": frame or "", "camera_id": camera_id}


@app.post("/live/dual/control/{camera_id}")
def control_dual_worker(camera_id: int, control: LiveControl, user=Depends(resolve_admin)):
    """Start/stop specific camera."""
    if camera_id == 1:
        worker = get_worker_dual_1()
    elif camera_id == 2:
        worker = get_worker_dual_2()
    else:
        raise HTTPException(status_code=400, detail="camera_id must be 1 or 2")
    
    if control.active and not worker.running:
        worker.start()
    elif not control.active and worker.running:
        worker.stop()
    
    return {"camera_id": camera_id, "running": worker.running}


@app.post("/live/dual/settings/{camera_id}")
def update_dual_settings(camera_id: int, settings: LiveSettings, user=Depends(resolve_admin)):
    """Update settings for specific camera."""
    if camera_id == 1:
        worker = get_worker_dual_1()
    elif camera_id == 2:
        worker = get_worker_dual_2()
    else:
        raise HTTPException(status_code=400, detail="camera_id must be 1 or 2")
    
    worker.update_settings(
        fps_target=settings.fps_target,
        crime_threshold=settings.crime_threshold,
        show_boxes=settings.show_boxes,
        show_weapons=settings.show_weapons,
    )
    return {"message": f"Settings updated for camera {camera_id}"}


@app.get("/alerts/live/dual/{camera_id}")
def live_dual_alerts(camera_id: int):
    """Get live alerts from specific camera."""
    if camera_id == 1:
        worker = get_worker_dual_1()
    elif camera_id == 2:
        worker = get_worker_dual_2()
    else:
        raise HTTPException(status_code=400, detail="camera_id must be 1 or 2")
    
    return {"alerts": worker.flush_alerts(), "camera_id": camera_id}


def _load_alerts(metadata_dir: Path, limit: int) -> Dict[str, List[Dict[str, Any]]]:  # type: ignore[type-arg]
    alerts: List[Dict[str, Any]] = []
    if not metadata_dir.exists():
        return {"alerts": alerts}

    files = sorted(metadata_dir.glob("*.json"), reverse=True)[:limit]
    for file in files:
        try:
            payload = file.read_text(encoding="utf-8")
            alerts.append({"id": file.stem, **json.loads(payload)})
        except Exception:
            continue
    return {"alerts": alerts}
