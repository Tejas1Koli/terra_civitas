# 🎯 Dual Camera Configuration - Edit Locations

## Where to Put Your Camera URLs

### File: `backend/live_detection.py`
**Lines 305-322** (at the bottom of the file)

```python
def get_worker_dual_1() -> LiveDetectionWorker:
    """Get or create first worker for dual-camera mode."""
    global worker_dual_1
    if worker_dual_1 is None:
        # 👇 EDIT THIS LINE - Change the video_source to your camera 1 URL
        worker_dual_1 = LiveDetectionWorker(video_source=0)  # ← CHANGE ME
    return worker_dual_1

def get_worker_dual_2() -> LiveDetectionWorker:
    """Get or create second worker for dual-camera mode."""
    global worker_dual_2
    if worker_dual_2 is None:
        # 👇 EDIT THIS LINE - Change the video_source to your camera 2 URL
        worker_dual_2 = LiveDetectionWorker(video_source=0)  # ← CHANGE ME
    return worker_dual_2
```

---

## Examples for Different Camera Types

### Example 1: Two IP Webcams (Phone Cameras)

```python
def get_worker_dual_1() -> LiveDetectionWorker:
    global worker_dual_1
    if worker_dual_1 is None:
        worker_dual_1 = LiveDetectionWorker(
            video_source="http://192.168.1.100:8080/video"  # Phone 1 IP
        )
    return worker_dual_1

def get_worker_dual_2() -> LiveDetectionWorker:
    global worker_dual_2
    if worker_dual_2 is None:
        worker_dual_2 = LiveDetectionWorker(
            video_source="http://192.168.1.101:8080/video"  # Phone 2 IP
        )
    return worker_dual_2
```

### Example 2: Local Webcam + IP Camera

```python
def get_worker_dual_1() -> LiveDetectionWorker:
    global worker_dual_1
    if worker_dual_1 is None:
        worker_dual_1 = LiveDetectionWorker(video_source=0)  # Built-in webcam
    return worker_dual_1

def get_worker_dual_2() -> LiveDetectionWorker:
    global worker_dual_2
    if worker_dual_2 is None:
        worker_dual_2 = LiveDetectionWorker(
            video_source="http://192.168.1.50:8080/video"  # IP Camera
        )
    return worker_dual_2
```

### Example 3: Two RTSP Streams

```python
def get_worker_dual_1() -> LiveDetectionWorker:
    global worker_dual_1
    if worker_dual_1 is None:
        worker_dual_1 = LiveDetectionWorker(
            video_source="rtsp://192.168.1.40:554/stream"  # RTSP Camera 1
        )
    return worker_dual_1

def get_worker_dual_2() -> LiveDetectionWorker:
    global worker_dual_2
    if worker_dual_2 is None:
        worker_dual_2 = LiveDetectionWorker(
            video_source="rtsp://192.168.1.41:554/stream"  # RTSP Camera 2
        )
    return worker_dual_2
```

### Example 4: Video Files

```python
def get_worker_dual_1() -> LiveDetectionWorker:
    global worker_dual_1
    if worker_dual_1 is None:
        worker_dual_1 = LiveDetectionWorker(
            video_source="/Users/tejaskoli/testing yolo1/video1.mp4"
        )
    return worker_dual_1

def get_worker_dual_2() -> LiveDetectionWorker:
    global worker_dual_2
    if worker_dual_2 is None:
        worker_dual_2 = LiveDetectionWorker(
            video_source="/Users/tejaskoli/testing yolo1/video2.mp4"
        )
    return worker_dual_2
```

---

## Finding Your IP Cameras

### For IP Webcam (Phone) 📱

**Camera 1:**
1. Open IP Webcam app on phone 1
2. Tap "Start server"
3. Open Settings → WiFi → Connected network
4. Note the IP address (e.g., `192.168.1.100`)
5. Use: `http://192.168.1.100:8080/video`

**Camera 2:**
1. Repeat on second phone with different IP
2. Use: `http://192.168.1.101:8080/video`

### For RTSP Cameras 📹

Check your camera manual or admin interface for:
- IP address: e.g., `192.168.1.40`
- Port: usually `554`
- Stream path: usually `/stream` or `/main`

Use: `rtsp://192.168.1.40:554/stream`

### For Local Webcams 💻

- **First webcam**: `0`
- **Second webcam**: `1`

---

## ✅ Configuration Checklist

- [ ] Found Camera 1 URL or device index
- [ ] Found Camera 2 URL or device index
- [ ] Edited `backend/live_detection.py` with both URLs
- [ ] Tested Camera 1 URL works (ping IP or open in browser)
- [ ] Tested Camera 2 URL works
- [ ] Restarted backend: `pkill uvicorn && ./yolo/bin/python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 &`
- [ ] Navigated to `/dual` in frontend
- [ ] Both cameras appear on dashboard
- [ ] Can start/stop each camera independently
- [ ] Can verify alerts for each camera separately

---

## Testing Your URLs Before Using

### For IP Webcams:

**In Terminal:**
```bash
# Ping the IP to verify connectivity
ping 192.168.1.100

# Should show responses like: bytes=32 time=XX ms
```

**In Browser:**
```
Open: http://192.168.1.100:8080/video
Should show live video stream
```

### For RTSP Streams:

**In Terminal:**
```bash
# Using ffprobe (if installed)
ffprobe rtsp://192.168.1.40:554/stream

# Or using OpenCV in Python
python3 -c "import cv2; cap = cv2.VideoCapture('rtsp://192.168.1.40:554/stream'); print('OK' if cap.isOpened() else 'FAILED')"
```

---

## URL Format Reference

| Source Type | Format | Example |
|-----------|--------|---------|
| Local Webcam | `{index}` | `0` or `1` |
| IP Webcam | `http://IP:PORT/PATH` | `http://192.168.1.100:8080/video` |
| RTSP | `rtsp://IP:PORT/PATH` | `rtsp://192.168.1.40:554/stream` |
| HTTP Stream | `http://URL` | `http://camera.local/live` |
| Video File | `/path/to/file` | `/home/user/video.mp4` |

---

## Common Ports by App

| Application | Port |
|-------------|------|
| IP Webcam (Android) | 8080 |
| DroidCam | 4747 |
| Iriun | 8080 |
| RTSP Cameras | 554 |

---

## After Configuration

1. **Restart Backend:**
   ```bash
   pkill uvicorn
   cd /Users/tejaskoli/testing\ yolo1
   ./yolo/bin/python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 &
   ```

2. **Access Frontend:**
   ```
   http://localhost:5174
   ```

3. **Go to Dual Camera Dashboard:**
   ```
   Click "Dual Cameras" in left sidebar
   ```

4. **Start Both Cameras:**
   ```
   Click "Start" button on each camera
   ```

5. **Verify Alerts:**
   ```
   Wait for crime detection
   Separate verify buttons for each camera's alerts
   ```

---

## Troubleshooting

### "Failed to open video source"
- ✅ Check URL is correct
- ✅ Test URL in browser first
- ✅ Verify camera app is running
- ✅ Ensure same WiFi network

### "Connection timeout"
- ✅ Ping the IP address
- ✅ Check firewall settings
- ✅ Verify camera is powered on
- ✅ Try from a wired connection

### "One camera works, other doesn't"
- ✅ Check second camera URL is correct
- ✅ Verify second camera app started
- ✅ Check both have different IPs
- ✅ Test second URL independently

---

## Need Help?

See these files for more info:
- `DUAL_CAMERA_SETUP.md` - Complete setup guide
- `DUAL_CAMERA_IMPLEMENTATION.md` - Implementation details
- `IP_WEBCAM_SETUP.md` - IP camera setup guide

**You're all set! 🎉**
