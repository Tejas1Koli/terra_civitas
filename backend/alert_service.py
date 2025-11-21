"""Alert management helpers for CCTV detection backend."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from supabase_sync import init_supabase


def move_to_verified_alerts(alert_id: str, alerts_dir: str = "alerts", verified_by: str = "admin") -> bool:
    """Move alert image/metadata to verified folder and sync to Supabase.
    
    Returns True if metadata was successfully moved (image is optional).
    Returns False only if metadata cannot be found.
    """
    alerts_path = Path(alerts_dir)
    verified_path = Path("verified_alerts")
    verified_images_dir = verified_path / "images"
    verified_metadata_dir = verified_path / "metadata"

    verified_images_dir.mkdir(parents=True, exist_ok=True)
    verified_metadata_dir.mkdir(parents=True, exist_ok=True)

    images_dir = alerts_path / "images"
    metadata_dir = alerts_path / "metadata"

    # Try to copy image if it exists (optional)
    _copy_image(alert_id, images_dir, verified_images_dir)
    
    # Copy metadata (required)
    metadata_copied = _copy_metadata(alert_id, metadata_dir, verified_metadata_dir, verified_by)

    if not metadata_copied:
        return False

    try:
        sync = init_supabase()
        if sync.connected:
            sync.push_alert(alert_id, "verified_alerts")
    except Exception:
        # Supabase sync failures should not block verification
        pass

    return True


def _copy_image(alert_id: str, src_dir: Path, dest_dir: Path) -> bool:
    candidates = []
    if (src_dir / f"{alert_id}.jpg").exists():
        candidates = [src_dir / f"{alert_id}.jpg"]
    else:
        candidates = list(src_dir.glob(f"{alert_id}*"))

    if not candidates:
        return False

    for img_file in candidates:
        shutil.copy2(img_file, dest_dir / img_file.name)
    return True


def _copy_metadata(alert_id: str, src_dir: Path, dest_dir: Path, verified_by: str) -> bool:
    candidates: list[Path] = []
    exact = src_dir / f"{alert_id}.json"
    if exact.exists():
        candidates = [exact]
    else:
        candidates = list(src_dir.glob(f"{alert_id}*.json"))

    if not candidates:
        return False

    for meta_file in candidates:
        with open(meta_file, "r", encoding="utf-8") as fh:
            metadata = json.load(fh)

        metadata["verified"] = True
        metadata["verified_by"] = verified_by or metadata.get("verified_by", "admin")
        metadata["verified_at"] = datetime.now().isoformat()

        with open(dest_dir / meta_file.name, "w", encoding="utf-8") as out:
            json.dump(metadata, out, indent=2)

    return True
