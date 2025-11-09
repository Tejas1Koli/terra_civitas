# 🚨 Alert Logging System - Documentation

## Overview

The alert logging system automatically captures and stores crime detection alerts with images and detailed metadata. Every time the CCTV system detects a crime (threat score ≥ threshold), it saves:

1. **Screenshot Image** - The frame at time of detection
2. **JSON Metadata** - Complete detection details
3. **Daily Log** - Aggregated log of all alerts that day

---

## 📂 Directory Structure

```
alerts/
├── images/              # Screenshot JPG files
│   ├── CRIME_20250109_120530_123.jpg
│   ├── CRIME_20250109_120545_456.jpg
│   └── ...
├── metadata/            # Detailed JSON metadata
│   ├── CRIME_20250109_120530_123.json
│   ├── CRIME_20250109_120545_456.json
│   └── ...
└── daily_logs/          # Daily aggregated logs
    ├── 20250109_alerts.json
    ├── 20250108_alerts.json
    └── ...
```

---

## 📸 Alert File Format

### Image Files
- **Location**: `alerts/images/`
- **Format**: JPEG (.jpg)
- **Naming**: `{ALERT_TYPE}_{YYYYMMDD}_{HHMMSS}_{milliseconds}.jpg`
- **Example**: `CRIME_20250109_120530_123.jpg`

### Metadata JSON Files
- **Location**: `alerts/metadata/`
- **Format**: JSON (.json)
- **Naming**: Same as corresponding image

#### JSON Structure:
```json
{
  "alert_id": "CRIME_20250109_120530_123",
  "timestamp": "2025-01-09T12:05:30.123456",
  "datetime_readable": "2025-01-09 12:05:30.123",
  "alert_type": "CRIME",
  "frame_number": 1254,
  "threat_score": 0.75,
  "confidence": 0.82,
  "is_crime": true,
  "detection_details": {
    "weapons_detected": 1,
    "motion_score": 0.6,
    "cluster_score": 0.2,
    "crime_score": 0.68
  },
  "weapons": [
    {
      "confidence": 0.92,
      "class": "gun",
      "box": [240, 150, 320, 280]
    }
  ],
  "image_file": "CRIME_20250109_120530_123.jpg",
  "image_path": "/Users/tejaskoli/testing yolo1/alerts/images/CRIME_20250109_120530_123.jpg"
}
```

### Daily Log Files
- **Location**: `alerts/daily_logs/`
- **Format**: JSON array (.json)
- **Naming**: `{YYYYMMDD}_alerts.json`
- **Example**: `20250109_alerts.json`

#### Daily Log Structure:
```json
[
  {
    "alert_id": "CRIME_20250109_120530_123",
    "timestamp": "2025-01-09T12:05:30.123456",
    "datetime_readable": "2025-01-09 12:05:30.123",
    "alert_type": "CRIME",
    "threat_score": 0.75,
    "confidence": 0.82,
    "image_file": "CRIME_20250109_120530_123.jpg",
    "metadata_file": "CRIME_20250109_120530_123.json"
  },
  ...
]
```

---

## 🔧 AlertLogger API

### Initialization
```python
from alert_logger import AlertLogger

# Create logger (auto-creates directories)
logger = AlertLogger("alerts")  # Default folder name
```

### Logging an Alert
```python
# Log when crime detected
log_info = logger.log_alert(
    frame=cv2_frame,              # OpenCV BGR image
    detection_results=results,     # From cctv_detector.detect_frame()
    alert_type="CRIME"             # Alert type ("CRIME", "WEAPON", "MOTION", "CLUSTER")
)

if log_info:
    print(f"✅ Logged: {log_info['alert_id']}")
```

### Get Alerts
```python
# Get all recent alerts (sorted by time, most recent first)
recent = logger.get_all_alerts(limit=100)

# Get high-threat alerts only
high_threat = logger.get_high_threat_alerts(threshold=0.7, limit=50)

# Get today's summary
today = logger.get_alert_summary()  # Current day
# OR specific date
sept_1st = logger.get_alert_summary("20250901")
```

### Storage Management
```python
# Get storage information
info = logger.get_storage_info()
print(f"Total alerts: {info['total_alerts']}")
print(f"Storage used: {info['total_size_mb']} MB")

# Clean up old alerts (older than 30 days)
deleted = logger.cleanup_old_alerts(days=30)
print(f"Deleted {deleted} old files")

# Export to CSV
logger.export_alerts_csv("alerts_export.csv")
```

---

## 📊 Integration with CCTV App

The alert logging is **automatically integrated** into `cctv_app_analytics.py`:

### 1. Live Webcam Mode
- Automatically logs alerts when crime detected
- Saves image + metadata in real-time
- No manual action needed

### 2. Video Upload Mode
- Analyzes entire video frame-by-frame
- Logs each frame meeting crime threshold
- Creates daily log after processing

### 3. Analytics Dashboard
- **Recent Alerts Tab**: View all logged alerts
- **High Threat Alerts Tab**: Filter by threat score
- **Storage Info Tab**: Check disk usage
- **Alert Management Tab**: Cleanup old files, export to CSV

---

## 📈 Usage Examples

### Example 1: Access Logged Alerts
```python
from alert_logger import AlertLogger

logger = AlertLogger("alerts")

# Get recent alerts
alerts = logger.get_all_alerts(limit=10)
for alert in alerts:
    print(f"{alert['datetime_readable']}: {alert['alert_type']} (Score: {alert['threat_score']})")
```

### Example 2: High Severity Tracking
```python
# Get only high-severity alerts
serious = logger.get_high_threat_alerts(threshold=0.8)
print(f"Found {len(serious)} high-threat incidents")

# Export for analysis
logger.export_alerts_csv("serious_alerts.csv")
```

### Example 3: Daily Report
```python
# Generate daily report
today = logger.get_alert_summary()
print(f"Today's Incidents: {today['total_alerts']}")
print(f"Crime Classification: {today['crime_alerts']}")
print(f"Average Threat Level: {today['average_threat_score']}")

# Cleanup alerts older than 7 days
deleted = logger.cleanup_old_alerts(days=7)
print(f"Cleaned up {deleted} old alerts")
```

---

## 🎯 Streamlit UI Integration

### Alert Logs Viewer in Analytics Dashboard

#### Tab 1: Recent Alerts
- Lists all logged alerts in reverse chronological order
- Shows: Time, Type, Threat Score, Confidence, Image file
- Click to view full JSON metadata

#### Tab 2: High Threat Alerts
- Filter alerts by threat score threshold (slider)
- Display only serious incidents
- Useful for incident review and analysis

#### Tab 3: Storage Info
- **Total alerts logged**: Number of events captured
- **Images size**: Disk space for screenshots
- **Metadata size**: Storage for JSON files
- **Today's stats**: Current day's summary
- **Storage location**: Full path to alerts folder

#### Tab 4: Alert Management
- **Cleanup Old Alerts**: Remove files older than N days
- **Export to CSV**: Download alerts as CSV for Excel/Analysis
- **Information**: Folder structure explanation

---

## 💾 Disk Usage Estimation

Based on average file sizes:

| Item | Size | 100 Alerts | 1000 Alerts |
|------|------|-----------|-----------|
| Screenshot (JPEG) | ~150-200 KB | 15-20 MB | 150-200 MB |
| Metadata (JSON) | ~2-3 KB | 0.2-0.3 MB | 2-3 MB |
| **Total per Alert** | **~153-203 KB** | **~15.2-20.3 MB** | **~152-203 MB** |

---

## ⚠️ Best Practices

1. **Regular Cleanup**
   - Run cleanup monthly to manage storage
   - Keep only critical incidents long-term
   
2. **Daily Reviews**
   - Use Analytics Dashboard to review daily logs
   - Export suspicious days for detailed analysis

3. **Backup Important Alerts**
   - Export critical incidents to separate storage
   - Keep legal evidence properly archived

4. **Monitoring**
   - Check storage usage regularly
   - Set alerts for high-severity incidents (>0.8 score)

---

## 🔐 Security Notes

- Store alerts in secure location with proper access control
- Backup important alerts regularly
- Consider encryption for sensitive footage
- Comply with local data retention laws

---

## 📝 Troubleshooting

### Alerts not being logged?
1. Check if crime threshold is set correctly
2. Verify `alerts/` directory exists and is writable
3. Check detection sensitivity settings

### CSV export fails?
1. Ensure `csv` module is available
2. Check file write permissions
3. Verify disk space available

### Disk space filling up?
1. Run cleanup on old alerts
2. Adjust retention period
3. Monitor storage usage with Storage Info tab

---

## 🚀 Future Enhancements

- [ ] Email alerts on high-threat detection
- [ ] Database storage backend
- [ ] Cloud backup integration
- [ ] Advanced search/filtering
- [ ] Analytics dashboard integration
- [ ] Alert dashboard with timeline visualization

---

**Last Updated**: November 9, 2025
**Status**: ✅ Fully Integrated and Production-Ready
