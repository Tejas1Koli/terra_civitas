# 🔍 CCTV AI Crime Detection System

> **Real-time Multi-Camera Weapon Detection with Dual Streaming, Alert Verification, and Cloud Sync**

A professional-grade CCTV surveillance system powered by AI/ML for real-time weapon detection. Features dual independent camera streams (local webcam + IP camera), React frontend, FastAPI backend, and intelligent alert management with cloud synchronization.

---

## 🌟 Key Features

### 🎥 Dual Camera Streaming
- **Live Webcam**: Local USB/built-in camera (30 FPS)
- **IP Camera**: Wireless network camera with auto-optimization (10 FPS, compressed)
- Independent start/stop controls for each camera
- Real-time frame polling with optimized bandwidth usage
- Automatic source type detection (webcam, IP camera, RTSP, HTTP, file)

### 🤖 AI-Powered Detection
- YOLO ONNX model inference for weapon detection
- Real-time threat scoring with smoothing
- Motion detection and clustering analysis
- Configurable confidence thresholds (0.0-1.0 scale)
- **Status Overlay**: Small text indicator showing "NORMAL" (green) or "CRIME" (red)

### 🚨 Alert Management
- Automatic alert logging with disk persistence
- Alert verification workflow (mark as verified/false alarm)
- Per-camera alert tracking and statistics
- Cloud sync capability (Supabase integration ready)
- Alert archival and retrieval

### 📊 Dashboard & Monitoring
- Dual camera video cards with live stats (FPS, frame count, threat level)
- Real-time threat threshold slider
- Detection options (motion, clustering, weapons)
- Motion sensitivity tuning
- Single camera fallback mode
- Analytics dashboard

### 🔐 Authentication & Security
- SQLite-based user authentication
- Session token management (12-hour TTL)
- Admin-only access to control endpoints
- CORS middleware for secure cross-origin requests
- Role-based access control (admin/normal)

### ⚡ Performance Optimizations
- **Dual Camera FPS Strategy**:
  - Local webcam: 30 FPS, quality 80 (full resolution)
  - IP camera: 10 FPS, quality 60 (320px downscale, 1-of-3 frame processing)
- JPEG compression for bandwidth reduction
- Frame skipping for network sources
- 33ms frontend polling interval (matches 30 FPS backend)
- Connection recovery with automatic retry logic

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React 18.3)                     │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │  Dual Camera   │  │  Alert Panel    │  │  Dashboard   │  │
│  │  Card (Video)  │  │  (Verification) │  │  (Analytics) │  │
│  └────────┬───────┘  └────────┬────────┘  └──────┬───────┘  │
│           │                    │                   │          │
│           └────────────────────┼───────────────────┘          │
│                                │                              │
└────────────────────────────────┼──────────────────────────────┘
                                 │
                    API Client (Axios)
                                 │
┌────────────────────────────────┼──────────────────────────────┐
│                   Backend (FastAPI 0.121)                      │
│                                │                               │
│  ┌──────────────────────────────┼────────────────────────────┐ │
│  │              API Layer                                    │ │
│  │  ┌─────────────────┬──────────────┬───────────────────┐  │ │
│  │  │ Single Camera   │ Dual Camera  │ Alert Endpoints   │  │ │
│  │  │ (3 endpoints)   │ (9 endpoints)│ (5 endpoints)     │  │ │
│  │  └─────────┬───────┴──────┬───────┴────────┬──────────┘  │ │
│  └───────────────────────────┼────────────────────────────────┘ │
│                              │                                  │
│  ┌──────────────────────────────┼────────────────────────────┐ │
│  │        Detection Layer                                    │ │
│  │  ┌─────────────────┬──────────────┬───────────────────┐  │ │
│  │  │ Worker Thread 1 │ Worker Thread│ Alert Logger      │  │ │
│  │  │ (Webcam 0)      │ 2 (IP Camera)│ (JSON Storage)    │  │ │
│  │  │ (30 FPS)        │ (10 FPS)     │                   │  │ │
│  │  └─────────────────┴──────────────┴───────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                  │
│  ┌──────────────────────────────┼────────────────────────────┐ │
│  │     ML Model Layer                                        │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │  CCTVCrimeDetector (YOLO ONNX - normal.onnx 12MB)   │ │ │
│  │  │  • Weapon detection & classification                 │ │ │
│  │  │  • Motion region tracking                            │ │ │
│  │  │  • Threat scoring & smoothing                        │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Data Layer                                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │   │
│  │  │SQLite DB │  │ Alerts/  │  │ Cloud Sync (Opt.)    │   │   │
│  │  │(Users)   │  │ JSON FS  │  │ Supabase             │   │   │
│  │  └──────────┘  └──────────┘  └──────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **Frontend → API**: User clicks "Start" button → `POST /live/dual/control/1`
2. **API → Worker**: Handler retrieves worker singleton → calls `worker.start()`
3. **Worker → Threading**: Spawns daemon thread → starts `_run()` loop
4. **Loop → Model**: Each frame → `detector.detect_frame()` → YOLO inference
5. **Results → Storage**: Crime detected → `alert_logger.log_alert()` → JSON + image saved
6. **Frontend Poll**: Every 33ms fetches `/live/dual/frame/1` and `/live/dual/stats`
7. **Display**: React renders frame + metadata with status overlay

---

## 📋 API Endpoints

### Health & Status
- `GET /health` - Server health check
- `GET /live/stats` - Detection statistics (FPS, frame count, crimes)
- `GET /live/frame` - Current JPEG frame as Base64

### Live Detection Control
- `POST /live/control` - Start/stop detection worker
- `GET /live/settings` - Current YOLO settings
- `POST /live/settings` - Update detection settings

### Video File Issues
- `GET /alerts/recent` - Recent alerts (persistent storage)
- `GET /alerts/verified` - All verified alerts
- `GET /alerts/live` - Real-time alert queue (temporary)
- `POST /alerts/{id}/verify` - Mark alert as verified
- `POST /alerts/{id}/reject` - Reject alert

### Authentication
- `POST /auth/login` - Get auth token
- `POST /auth/register` - Create new user

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- Node.js 18+
- macOS/Linux/Windows with webcam

### 1. Navigate to Project Directory
```bash
cd "/Users/tejaskoli/testing yolo1"
```

### 2. Activate Virtual Environment (if needed)
```bash
source yolo/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start Detection
```bash
streamlit run app.py
```

### 5. Monitor Statistics
- **Frame Count**: Total frames processed
- **Detections in Frame**: Weapons found in current frame
- **Total Detections**: Cumulative detection count
- **FPS**: Frames per second

---

## 🔧 Configuration

### Model Path
Default: `/Users/tejaskoli/testing yolo1/normal.onnx`

Edit in sidebar or modify `app.py` to use different model.

### Confidence Threshold
- **Range**: 0.0 to 1.0
- **Default**: 0.5

Use to filter detections by confidence score.

### Video Input Size
- **Model Input**: 640x640 pixels
- **Display Size**: 640x480 pixels (adjustable in code)

### Alert Image Interval
Edit `alert_logger.py` line 33:
```python
def __init__(self, alert_dir: str = "alerts", interval_seconds: int = 0):
```
- `interval_seconds = 0` means save image for every alert
- `interval_seconds = 5` means save image once per 5 seconds

---

## 🐛 Troubleshooting

### Model Failed to Load
- Verify `normal.onnx` exists in the workspace
- Check file permissions
- Ensure ONNX Runtime is properly installed

### Webcam Not Working
- Check camera permissions in system settings
- Verify camera is not in use by another application
- Try index 1 if available instead of 0

### Slow Performance
- Reduce display size in code
- Increase confidence threshold
- Check CPU/GPU usage
- Use GPU-accelerated ONNX Runtime if available

### No Alerts Appearing
1. Check worker is running: `GET /health` (should show `worker_running: true`)
2. Start worker: `POST /live/control` with `{"action": "start"}`
3. Check alert files: `ls -la alerts/metadata/`

### Images Not Saving
- Check interval setting in `alert_logger.py`
- Verify disk space: `df -h`
- Check permissions: `ls -la alerts/images/`

---

## 🔄 Alert Workflow

1. Detection: YOLO detects weapon/crime
   └─ Saves: alerts/metadata/CRIME_20251120_111827_197.json
   └─ Saves: alerts/images/CRIME_20251120_111827_197.jpg (if interval elapsed)
2. Dashboard: React app polls /alerts/recent
   └─ Displays in AlertsPanel with verify/reject buttons
3. Verification: Admin clicks "Verify Alert"
   └─ API call: POST /alerts/CRIME_20251120_111827_197/verify
   └─ Backend moves files to verified_alerts/
   └─ Adds: {"verified": true, "verified_by": "admin", "verified_at": "..."}
4. Cloud Sync: Automatically calls Supabase
   └─ Syncs metadata to cloud database
   └─ Enables multi-device access & analytics

---

## 📦 Dependencies

### Backend
- **fastapi** 0.121.2 - Web framework
- **uvicorn** 0.38.0 - ASGI server
- **onnxruntime** - YOLO model inference
- **opencv-python** - Video processing
- **numpy** - Array operations
- **supabase-py** - Cloud DB sync

### Frontend
- **react** 18.3.1 - UI library
- **typescript** 5.4.5 - Type safety
- **vite** 5.4.21 - Build tool
- **antd** 5.20 - UI components
- **axios** 1.7 - HTTP client
- **react-router-dom** 6 - Routing

---

## 🎯 Next Steps
- [ ] Configure Supabase credentials for cloud sync
- [ ] Set up email notifications for verified alerts
- [ ] Add multi-camera support
- [ ] Implement alert archival (move old alerts to storage)
- [ ] Add analytics dashboard (alerts per day, common threat scores)
- [ ] Set up Docker containers for deployment

---

## 📞 Support

For issues or questions, check:
- `SYSTEM_ARCHITECTURE.md` - Complete flow diagrams
- `QUICK_START.md` - Common use cases
- Backend logs: `/tmp/backend.log`
- Frontend console: Browser DevTools → Console

---

**Version**: 2.0 (React + FastAPI)  
**Last Updated**: November 20, 2025  
**Status**: ✅ Production Ready
