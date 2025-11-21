# 🎬 Multi-Source Video Capture Guide

## Overview

The updated `live_detection.py` now supports multiple video sources:
- ✅ **Webcam** (default)
- ✅ **IP Cameras** (RTSP/RTMP streams)
- ✅ **HTTP Video Streams**
- ✅ **Video Files** (MP4, AVI, MOV, MKV, FLV, WMV)
- ✅ **Multiple webcams** (by device index)

## 📝 Configuration

### 1. In Code (Backend Initialization)

```python
from backend.live_detection import LiveDetectionWorker

# Webcam (default)
worker = LiveDetectionWorker()

# Specific webcam by index
worker = LiveDetectionWorker(video_source=1)

# IP Camera (RTSP)
worker = LiveDetectionWorker(
    video_source="rtsp://192.168.1.100:554/stream"
)

# HTTP Stream
worker = LiveDetectionWorker(
    video_source="http://192.168.1.100:8080/stream"
)

# Video File
worker = LiveDetectionWorker(
    video_source="/path/to/video.mp4"
)

# Video File with custom FPS
worker = LiveDetectionWorker(
    video_source="/path/to/video.mp4",
    fps_target=30
)
```

### 2. Via API Endpoint

The backend will support dynamic source switching (add this to `api.py`):

```bash
# Change to IP camera
curl -X POST http://localhost:8000/live/source \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source": "rtsp://192.168.1.100:554/stream"}'

# Change to webcam
curl -X POST http://localhost:8000/live/source \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source": 0}'

# Change to video file
curl -X POST http://localhost:8000/live/source \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source": "/path/to/video.mp4"}'
```

## 🔗 Supported Video Source Formats

### Webcam
```python
# Primary webcam
video_source=0

# Secondary webcam
video_source=1

# USB camera
video_source="/dev/video0"  # Linux
video_source="camera:0"      # Windows
```

### IP Cameras (RTSP)
```python
# Generic RTSP stream
video_source="rtsp://192.168.1.100:554/stream"

# Hikvision IP Camera
video_source="rtsp://admin:password@192.168.1.100:554/H264/ch1/main/av_stream"

# Dahua IP Camera
video_source="rtsp://admin:password@192.168.1.100/cam/realmonitor?channel=0&subtype=0"

# Axis Camera
video_source="rtsp://admin:password@192.168.1.100/axis-media/media.amp?videocodec=h264"
```

### HTTP Streams
```python
# Generic HTTP stream
video_source="http://192.168.1.100:8080/stream"

# Streaming service
video_source="http://example.com/live/stream.m3u8"
```

### Video Files
```python
# Local file path
video_source="/path/to/video.mp4"
video_source="./videos/sample.avi"
video_source="~/Downloads/footage.mov"

# Supported formats
# .mp4, .avi, .mov, .mkv, .flv, .wmv
```

## 🔍 Auto-Detection

The system automatically detects source type:

```python
video_source = "rtsp://..."  # Detected as: rtsp
video_source = "http://..."  # Detected as: http
video_source = "file.mp4"    # Detected as: file
video_source = 0             # Detected as: webcam
```

## 🛠️ Usage Examples

### Example 1: Switch Between Multiple Cameras

```python
worker = LiveDetectionWorker(video_source=0)
worker.start()

# Monitor camera 0 for 30 seconds
time.sleep(30)

# Switch to camera 1
worker.change_video_source(1)

# Monitor camera 1 for 30 seconds
time.sleep(30)

# Switch to IP camera
worker.change_video_source("rtsp://192.168.1.100:554/stream")

worker.stop()
```

### Example 2: Analyze Video File

```python
worker = LiveDetectionWorker(
    video_source="/data/security_footage.mp4",
    fps_target=30
)
worker.start()

# Processing happens automatically
# Check stats periodically
while worker.running:
    stats = worker.get_state()
    print(f"Frame: {stats['frame_count']}, Crimes: {stats['crime_count']}")
    time.sleep(1)

worker.stop()
```

### Example 3: Monitor Multiple Cameras Sequentially

```python
cameras = [
    0,  # Webcam
    1,  # Second USB camera
    "rtsp://192.168.1.100:554/stream",  # IP camera 1
    "rtsp://192.168.1.101:554/stream",  # IP camera 2
]

worker = LiveDetectionWorker()

for camera in cameras:
    print(f"Monitoring {camera}...")
    worker.change_video_source(camera)
    worker.start()
    
    # Monitor for 5 minutes
    for _ in range(300):
        time.sleep(1)
        if not worker.running:
            break
    
    worker.stop()
```

## 📊 Response Format

When getting state, the response now includes source information:

```json
{
  "frame_count": 150,
  "crime_count": 2,
  "fps": 14.8,
  "running": true,
  "video_source": "rtsp://192.168.1.100:554/stream",
  "source_type": "rtsp",
  "connection_errors": 0,
  "latest_results": {
    "smoothed_score": 0.35,
    "confidence": 0.42,
    "weapons_count": 0,
    "is_crime": true,
    "source": "rtsp"
  }
}
```

## 🐛 Troubleshooting

### Webcam Not Connecting
```bash
# Linux: Check available cameras
ls /dev/video*

# Try specific device
video_source = "/dev/video0"

# List all cameras
v4l2-ctl --list-devices
```

### RTSP Stream Connection Failed
```python
# Verify credentials
rtsp_url = "rtsp://username:password@192.168.1.100:554/stream"

# Check port
rtsp_url = "rtsp://192.168.1.100:554/stream"  # Standard port
rtsp_url = "rtsp://192.168.1.100:8554/stream"  # Alternative port

# Enable verbose logging to see connection errors
worker.start()
```

### Video File Not Found
```python
# Check file path exists
import os
assert os.path.exists(video_file), f"File not found: {video_file}"

# Check file format supported
supported = [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"]
assert any(video_file.endswith(ext) for ext in supported)
```

### High Latency with IP Camera
```python
# Reduce buffer size (done automatically, but verify)
# Increase FPS target
worker = LiveDetectionWorker(
    video_source="rtsp://...",
    fps_target=30  # Higher FPS can improve responsiveness
)

# Set lower resolution on camera if possible
```

## 🚀 Performance Tips

### For Webcams
- Default settings work well
- Buffer size automatically set to 1 for low latency

### For IP Cameras
- Use low-resolution streams if available
- Verify network bandwidth (typical RTSP: 2-5 Mbps)
- Consider using hardware-accelerated decoding

### For Video Files
- FPS adjusts automatically
- Use faster codec (H.264 preferred)
- Reduce resolution if CPU usage high

## 📋 Common IP Camera URLs

### Hikvision
```
rtsp://admin:admin@192.168.1.100:554/H264/ch1/main/av_stream
rtsp://admin:admin@192.168.1.100:554/H265/ch1/main/av_stream
```

### Dahua
```
rtsp://admin:admin@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0
rtsp://admin:admin@192.168.1.100:554/cam/realmonitor?channel=1&subtype=1
```

### Axis
```
rtsp://admin:admin@192.168.1.100/axis-media/media.amp?videocodec=h264&resolution=320x240
```

### Bosch
```
rtsp://admin:admin@192.168.1.100:554/rtsp_tunnel
```

### Reolink
```
rtsp://admin:admin@192.168.1.100:554/stream0
rtsp://admin:admin@192.168.1.100:554/stream1
```

## 🔄 Source Detection Logic

```python
def _detect_source_type(self, source: str | int) -> str:
    if isinstance(source, int):
        return "webcam"
    
    source_lower = source.lower()
    
    if "rtsp://" in source_lower or "rtmp://" in source_lower:
        return "rtsp"
    
    if "http://" in source_lower or "https://" in source_lower:
        return "http"
    
    if any(source_lower.endswith(ext) for ext in 
           [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"]):
        return "file"
    
    return "unknown"
```

## 📝 Implementation Notes

- **Automatic Reconnection**: RTSP streams auto-reconnect on failure (up to 5 retries)
- **Source Indicator**: Current source displayed on video frame
- **Error Tracking**: Connection errors logged in state
- **Dynamic Switching**: Can change sources without restarting backend
- **Performance**: Each source type optimized for latency

---

**Version**: 2.1 (Multi-Source Support)  
**Last Updated**: November 20, 2025  
**Status**: ✅ Production Ready
