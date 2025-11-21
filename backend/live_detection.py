
"""Background worker that powers live detection endpoints."""

from __future__ import annotations

import base64
import threading
import time
import queue
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import cv2

from alert_logger import AlertLogger
from cctv_detector import CCTVCrimeDetector


class LiveDetectionWorker:
    """Continuously captures frames from multiple sources, runs detection, and exposes stats."""

    def __init__(
        self,
        fps_target: int = 30,
        crime_threshold: float = 0.35,
        show_boxes: bool = True,
        show_weapons: bool = True,
        video_source: str | int = 0,  # 0 = webcam, or URL/file path
    ) -> None:
        self.fps_target = fps_target
        self.crime_threshold = crime_threshold
        self.show_boxes = show_boxes
        self.show_weapons = show_weapons
        self.video_source = video_source  # Webcam index, file path, RTSP URL, etc.

        self.source_type = self._detect_source_type(video_source)

        self.detector = CCTVCrimeDetector()
        self.alert_logger = AlertLogger("alerts")

        self.capture: Optional[cv2.VideoCapture] = None
        self.thread: Optional[threading.Thread] = None

        self.latest_frame_bytes: Optional[bytes] = None
        self.latest_results: Optional[Dict[str, Any]] = None
        self.frame_count = 0
        self.crime_count = 0
        self.frame_times: deque[float] = deque(maxlen=120)
        self.connection_error_count = 0

        self._alerts_queue: "queue.Queue[Dict[str, Any]]" = queue.Queue()
        self._lock = threading.Lock()
        self._running = False

    def _detect_source_type(self, source: str | int) -> str:
        """Detect the type of video source."""
        if isinstance(source, int):
            return "webcam"
        elif isinstance(source, str):
            source_lower = source.lower()
            if source_lower.startswith("rtsp://") or source_lower.startswith("rtmp://"):
                return "rtsp"
            elif source_lower.startswith("http://") or source_lower.startswith("https://"):
                # Check if it's an IP webcam URL (common patterns)
                if any(pattern in source_lower for pattern in [
                    "/video", "/stream", "/mjpeg", "/mjpegstream",
                    "/axis-media", "/cam/", "/snapshot",
                    "ipwebcam", "192.168", "10.0", "172.16"
                ]):
                    return "ip_webcam"
                return "http"
            elif source_lower.endswith((".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv")):
                return "file"
            else:
                return "unknown"
        return "unknown"

    def start(self) -> None:
        """Start video capture from the configured source."""
        if self._running:
            return

        try:
            print(f"🎬 Starting {self.source_type} capture from: {self.video_source}")
            
            # Convert source based on type
            if isinstance(self.video_source, int):
                # Webcam by index
                cap_source = self.video_source
            else:
                # File, RTSP, HTTP, or other URL
                cap_source = self.video_source
            
            self.capture = cv2.VideoCapture(cap_source)
            
            # Verify capture opened successfully
            if not self.capture.isOpened():
                raise RuntimeError(f"Failed to open video source: {self.video_source}")
            
            # Configure capture based on source type
            if self.source_type == "webcam":
                self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                self.capture.set(cv2.CAP_PROP_FPS, self.fps_target)
                self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for webcam
            elif self.source_type in ["rtsp", "http", "file"]:
                # For streams and files, set buffer size to 1 to reduce latency
                self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                # Try to set FPS if available
                try:
                    self.capture.set(cv2.CAP_PROP_FPS, self.fps_target)
                except:
                    pass

            print(f"✅ Video source opened successfully: {self.source_type}")
            self._running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            
        except Exception as e:
            print(f"❌ Error starting video capture: {e}")
            if self.capture:
                self.capture.release()
                self.capture = None
            raise

    def stop(self) -> None:
        self._running = False
        time.sleep(0.1)  # Give thread time to exit cleanly
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        if self.capture:
            self.capture.release()
            self.capture = None
        print(f"✅ Video capture stopped: {self.source_type}")

    def update_settings(
        self,
        fps_target: int,
        crime_threshold: float,
        show_boxes: bool,
        show_weapons: bool,
    ) -> None:
        with self._lock:
            self.fps_target = fps_target
            self.crime_threshold = crime_threshold
            self.show_boxes = show_boxes
            self.show_weapons = show_weapons

    def change_video_source(self, new_source: str | int) -> bool:
        """Change video source dynamically (restart capture)."""
        try:
            print(f"🔄 Changing video source from {self.video_source} to {new_source}")
            
            # Stop current capture
            was_running = self._running
            self.stop()
            
            # Update source
            self.video_source = new_source
            self.source_type = self._detect_source_type(new_source)
            
            # Reset stats
            self.frame_count = 0
            self.crime_count = 0
            self.frame_times.clear()
            self.connection_error_count = 0
            
            # Restart if it was running
            if was_running:
                self.start()
            
            print(f"✅ Video source changed to: {self.source_type} ({new_source})")
            return True
            
        except Exception as e:
            print(f"❌ Error changing video source: {e}")
            return False

    def _run(self) -> None:
        """Main detection loop with error recovery."""
        consecutive_failures = 0
        max_consecutive_failures = 5
        frame_skip_counter = 0
        
        # Adaptive settings based on source type
        is_network_source = self.source_type in ["ip_webcam", "rtsp", "http"]
        fps_target_local = 30
        fps_target_network = 10  # Reduced FPS for wireless IP streams
        effective_fps = fps_target_network if is_network_source else fps_target_local
        
        # Compression settings
        quality_local = 80
        quality_network = 60  # Higher compression for wireless
        effective_quality = quality_network if is_network_source else quality_local
        
        print(f"🎥 Network source detected: {is_network_source} | FPS: {effective_fps} | Quality: {effective_quality}")
        
        while self._running:
            if not self.capture:
                time.sleep(0.1)
                continue

            ret, frame = self.capture.read()
            
            # Handle read failures (network issues, EOF, etc.)
            if not ret:
                consecutive_failures += 1
                if consecutive_failures > max_consecutive_failures:
                    print(f"⚠️ Too many consecutive read failures. Stopping capture.")
                    self._running = False
                    break
                
                # Log read failure for streams
                if self.source_type in ["rtsp", "http", "ip_webcam"]:
                    print(f"⚠️ Read failure ({consecutive_failures}/{max_consecutive_failures}) - retrying...")
                
                time.sleep(0.1)
                continue
            
            # Reset failure counter on successful read
            consecutive_failures = 0
            self.connection_error_count = 0

            # Skip frames for network sources to reduce processing
            if is_network_source:
                frame_skip_counter += 1
                if frame_skip_counter < 3:  # Process 1 out of every 3 frames from IP webcam
                    time.sleep(0.03)
                    continue
                frame_skip_counter = 0

            # Get dynamic settings
            with self._lock:
                crime_threshold = self.crime_threshold

            self.frame_count += 1
            
            # Reduce resolution for network sources before detection
            if is_network_source:
                h, w = frame.shape[:2]
                if w > 320:  # Reduce resolution
                    scale = 320 / w
                    frame = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LINEAR)
            
            results = self.detector.detect_frame(frame)
            
            # Use original frame with small status overlay
            display_frame = frame.copy()

            is_crime = results["smoothed_score"] >= crime_threshold
            
            # Add small status text in top-right corner
            status_text = "CRIME" if is_crime else "NORMAL"
            status_color = (0, 0, 255) if is_crime else (0, 255, 0)  # Red for crime, Green for normal
            cv2.putText(display_frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.8, status_color, 2)
            if is_crime:
                self.crime_count += 1
                log_info = self.alert_logger.log_alert(frame=frame, detection_results=results, alert_type="CRIME")
                if log_info and log_info.get("image_saved", False):
                    alert_payload = {
                        "alert_id": log_info.get("alert_id"),
                        "threat_score": results["smoothed_score"],
                        "confidence": results["confidence"],
                        "timestamp": datetime.now().isoformat(),
                        "weapons_count": len(results.get("weapons", [])),
                        "source": self.source_type,
                    }
                    self._alerts_queue.put(alert_payload)

            ret, buffer = cv2.imencode(".jpg", display_frame, [cv2.IMWRITE_JPEG_QUALITY, effective_quality])
            if ret:
                with self._lock:
                    self.latest_frame_bytes = buffer.tobytes()
                    self.latest_results = {
                        "smoothed_score": results["smoothed_score"],
                        "confidence": results["confidence"],
                        "weapons_count": len(results.get("weapons", [])),
                        "is_crime": is_crime,
                        "source": self.source_type,
                    }
                    self.frame_times.append(time.time())

            sleep_interval = max(0.0, (1.0 / max(1.0, effective_fps)) - 0.005)
            time.sleep(sleep_interval)

    def get_frame_base64(self) -> Optional[str]:
        with self._lock:
            if not self.latest_frame_bytes:
                return None
            encoded = base64.b64encode(self.latest_frame_bytes).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded}"

    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            fps = 0.0
            if len(self.frame_times) > 1:
                fps = len(self.frame_times) / (self.frame_times[-1] - self.frame_times[0])

            return {
                "frame_count": self.frame_count,
                "crime_count": self.crime_count,
                "fps": round(fps, 2),
                "latest_results": self.latest_results or {},
                "running": self._running,
                "video_source": str(self.video_source),
                "source_type": self.source_type,
                "connection_errors": self.connection_error_count,
            }

    def flush_alerts(self) -> List[Dict[str, Any]]:
        drained: List[Dict[str, Any]] = []
        while not self._alerts_queue.empty():
            try:
                drained.append(self._alerts_queue.get_nowait())
            except queue.Empty:  # pragma: no cover - race condition guard
                break
        return drained

    @property
    def running(self) -> bool:
        return self._running


worker_singleton: Optional[LiveDetectionWorker] = None
worker_dual_1: Optional[LiveDetectionWorker] = None
worker_dual_2: Optional[LiveDetectionWorker] = None

DUAL_CAMERA_1_SOURCE: str | int = 0  # First webcam
DUAL_CAMERA_2_SOURCE: str | int = "http://100.76.107.130:8080/video"  # IP webcam URL

def get_worker() -> LiveDetectionWorker:
    global worker_singleton
    if worker_singleton is None:
        worker_singleton = LiveDetectionWorker(
            video_source=0  # Default to webcam 0; change to URL/file when you want a different source
        )
        # Don't auto-start; let the client explicitly start via /live/control
    return worker_singleton

def get_worker_dual_1() -> LiveDetectionWorker:
    """Get or create first worker for dual-camera mode."""
    global worker_dual_1
    if worker_dual_1 is None:
        worker_dual_1 = LiveDetectionWorker(video_source=DUAL_CAMERA_1_SOURCE)
    return worker_dual_1

def get_worker_dual_2() -> LiveDetectionWorker:
    """Get or create second worker for dual-camera mode."""
    global worker_dual_2
    if worker_dual_2 is None:
        worker_dual_2 = LiveDetectionWorker(video_source=DUAL_CAMERA_2_SOURCE)
    return worker_dual_2
