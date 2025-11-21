# ✅ Dual Camera Feature Implementation Complete!

## What's New? 🎥

Your CCTV system now supports **streaming 2 videos simultaneously** with **independent verify buttons** for each camera.

---

## 📁 Files Created/Modified

### Backend Changes (2 files)
✅ `backend/live_detection.py`
- Added `get_worker_dual_1()` function
- Added `get_worker_dual_2()` function
- Now supports separate worker instances per camera

✅ `backend/api.py`
- Added 5 new dual-camera endpoints:
  - `GET /live/dual/stats` - Stats from both cameras
  - `GET /live/dual/frame/{camera_id}` - Frame from specific camera
  - `POST /live/dual/control/{camera_id}` - Start/stop specific camera
  - `POST /live/dual/settings/{camera_id}` - Update settings per camera
  - `GET /alerts/live/dual/{camera_id}` - Alerts from specific camera

### Frontend Changes (4 files)

✅ `frontend/src/components/DualVideoCard.tsx` (NEW)
- Side-by-side video display for both cameras
- Independent start/stop buttons for each camera
- Real-time FPS, threat score, and detection metrics

✅ `frontend/src/components/DualAlertsPanel.tsx` (NEW)
- Split alert panel showing alerts from both cameras
- **Separate verify/reject buttons for each camera's alerts**
- Independent alert management per camera

✅ `frontend/src/pages/DualCameraDashboard.tsx` (NEW)
- Complete dual-camera dashboard page
- Combines video card and alerts panel
- Accessible at `/dual` route

✅ `frontend/src/App.tsx`
- Added `/dual` route to navigation
- Imported DualCameraDashboard component

✅ `frontend/src/components/AppShell.tsx`
- Updated sidebar menu with "Dual Cameras" option
- Added route detection for /dual

### Documentation (1 file)

✅ `DUAL_CAMERA_SETUP.md` (NEW)
- Complete setup guide
- API endpoint reference
- Configuration examples
- Troubleshooting guide

---

## 🚀 Quick Setup

### 1. Configure Your Cameras

Edit `backend/live_detection.py` (bottom of file):

```python
# Configure Camera 1 (line ~305)
worker_dual_1 = LiveDetectionWorker(
    video_source="http://192.168.1.100:8080/video"  # Your camera 1 URL
)

# Configure Camera 2 (line ~312)
worker_dual_2 = LiveDetectionWorker(
    video_source="http://192.168.1.101:8080/video"  # Your camera 2 URL
)
```

**Supported sources:**
- Webcam: `0`
- IP Webcam (phone): `"http://192.168.1.100:8080/video"`
- RTSP: `"rtsp://camera.local:554/stream"`
- Video file: `"/path/to/video.mp4"`

### 2. Restart Backend

```bash
pkill uvicorn
cd /Users/tejaskoli/testing\ yolo1
./yolo/bin/python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 &
```

### 3. Access Dual Camera Dashboard

1. Go to `http://localhost:5174` (or your frontend URL)
2. Login with credentials
3. Click **"Dual Cameras"** in left sidebar
4. You'll see both cameras with separate controls!

---

## 🎮 How to Use

### Video Streaming
- **Left side**: Camera 1 live feed
- **Right side**: Camera 2 live feed
- Each has independent **Start/Stop** button
- Real-time metrics: FPS, detections, threat level

### Alert Verification
- **Left panel**: Camera 1 alerts
- **Right panel**: Camera 2 alerts
- Each alert has:
  - ✅ **Verify** button (marks as valid threat)
  - ❌ **Reject** button (marks as false positive)

### Camera Control
- Start/Stop each camera independently
- Change settings per camera (FPS, threshold, etc.)
- View separate stats for each camera

---

## 📊 New API Endpoints

All endpoints require `Authorization: Bearer TOKEN` header:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/live/dual/stats` | GET | Get stats from both cameras |
| `/live/dual/frame/1` | GET | Get frame from camera 1 |
| `/live/dual/frame/2` | GET | Get frame from camera 2 |
| `/live/dual/control/1` | POST | Start/stop camera 1 |
| `/live/dual/control/2` | POST | Start/stop camera 2 |
| `/live/dual/settings/1` | POST | Update camera 1 settings |
| `/live/dual/settings/2` | POST | Update camera 2 settings |
| `/alerts/live/dual/1` | GET | Get camera 1 alerts |
| `/alerts/live/dual/2` | GET | Get camera 2 alerts |

---

## 🎯 Key Features

✅ **Dual Streaming**: 2 independent video sources  
✅ **Independent Controls**: Start/stop each camera separately  
✅ **Separate Alerts**: Each camera has its own alert queue  
✅ **Independent Verification**: Verify alerts per camera  
✅ **Real-time Metrics**: FPS, threat score, weapon detection  
✅ **Side-by-side Display**: Compare feeds at once  
✅ **Responsive Design**: Works on desktop and tablet  

---

## 🔄 Architecture Overview

```
┌─────────────────────────────────────────┐
│         Frontend (/dual route)          │
├─────────────────────────────────────────┤
│ DualVideoCard (side-by-side video)      │
│ - Camera 1 | Camera 2                   │
│ - Start/Stop buttons per camera         │
├─────────────────────────────────────────┤
│ DualAlertsPanel (split alerts)          │
│ - Camera 1 alerts | Camera 2 alerts     │
│ - Verify/Reject buttons per camera      │
└─────────────────────────────────────────┘
         ↕ (API calls every 800ms)
┌─────────────────────────────────────────┐
│      Backend (API endpoints)             │
├─────────────────────────────────────────┤
│ /live/dual/stats                        │
│ /live/dual/frame/{camera_id}            │
│ /live/dual/control/{camera_id}          │
│ /live/dual/settings/{camera_id}         │
│ /alerts/live/dual/{camera_id}           │
└─────────────────────────────────────────┘
         ↕ (Independent workers)
┌─────────────────────────────────────────┐
│      Backend Workers (Threading)        │
├─────────────────────────────────────────┤
│ Worker 1                  │ Worker 2    │
│ - Video capture           │ - Video cap │
│ - YOLO detection          │ - Detection │
│ - Alert generation        │ - Alerts    │
│ - Frame encoding          │ - Encoding  │
└─────────────────────────────────────────┘
         ↕ (Independent threads)
┌─────────────────────────────────────────┐
│      Video Sources                      │
├─────────────────────────────────────────┤
│ Camera 1: [IP/Webcam/RTSP/File]        │
│ Camera 2: [IP/Webcam/RTSP/File]        │
└─────────────────────────────────────────┘
```

---

## 💡 Configuration Examples

### Two IP Webcams (phones)
```python
worker_dual_1 = LiveDetectionWorker(video_source="http://192.168.1.100:8080/video")
worker_dual_2 = LiveDetectionWorker(video_source="http://192.168.1.101:8080/video")
```

### Webcam + IP Camera
```python
worker_dual_1 = LiveDetectionWorker(video_source=0)
worker_dual_2 = LiveDetectionWorker(video_source="http://192.168.1.50:8080/video")
```

### Two RTSP Streams
```python
worker_dual_1 = LiveDetectionWorker(video_source="rtsp://cam1.local:554/stream")
worker_dual_2 = LiveDetectionWorker(video_source="rtsp://cam2.local:554/stream")
```

---

## ✨ What's Different From Single Camera?

| Aspect | Single Camera | Dual Camera |
|--------|---------------|------------|
| Route | `/` | `/dual` |
| Component | `LiveVideoCard` | `DualVideoCard` |
| Layout | Single full-width | Side-by-side |
| Controls | Single set | Per-camera controls |
| Alerts | Combined | Split by camera |
| Backend | `get_worker()` | `get_worker_dual_1/2()` |
| API Base | `/live/*` | `/live/dual/*` |
| Workers | 1 instance | 2 instances |

---

## 📝 Next Steps

1. **Configure your cameras** in `backend/live_detection.py`
2. **Restart backend** with the new configuration
3. **Navigate to** `/dual` in your browser
4. **Start both cameras** with the control buttons
5. **Test alert verification** with separate buttons

---

## 🧪 Testing Quick Commands

```bash
# Test both cameras are running
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/live/dual/stats

# Start camera 1
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"active": true}' \
  http://localhost:8000/live/dual/control/1

# Get frame from camera 2
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/live/dual/frame/2
```

---

## 🎉 You're All Set!

Your CCTV system now has:
- ✅ Dual video streaming
- ✅ Independent camera controls
- ✅ Separate alert verification buttons
- ✅ Real-time metrics per camera
- ✅ Professional dashboard UI

**Go to `/dual` and enjoy! 🚀**
