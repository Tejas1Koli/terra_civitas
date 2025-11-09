# 🚨 Alert Logging System - Quick Start Guide

## What's New?

Your CCTV Crime Detection system now **automatically logs all crime alerts** with:
- ✅ Screenshot image (JPEG)
- ✅ Detailed metadata (JSON)
- ✅ Daily aggregated logs

---

## 📂 Where Are Alerts Saved?

All alerts are saved in the `alerts/` folder:

```
alerts/
├── images/      ← Screenshot JPG files
├── metadata/    ← JSON metadata files  
└── daily_logs/  ← Daily summary logs
```

---

## 🎯 How to Use

### Option 1: Via Streamlit UI (Easiest)

1. **Start the app**: `./start.sh`
2. **Go to**: http://localhost:8501
3. **Navigate to**: 📈 Analytics Dashboard
4. **Scroll down to**: 🚨 Alert Logs Viewer
5. **Choose a tab**:
   - 📋 **Recent Alerts** - View all logged alerts
   - 🔥 **High Threat Alerts** - Filter by threat score
   - 📊 **Storage Info** - Check disk usage
   - ⚙️ **Alert Management** - Cleanup, export

### Option 2: Programmatic Access

```python
from alert_logger import AlertLogger

logger = AlertLogger("alerts")

# Get recent alerts
recent = logger.get_all_alerts(limit=10)
for alert in recent:
    print(f"⏰ {alert['datetime_readable']}")
    print(f"🎯 {alert['alert_type']}")
    print(f"📊 Threat: {alert['threat_score']}")

# Get today's summary
today = logger.get_alert_summary()
print(f"Today: {today['total_alerts']} alerts")

# Export to CSV
logger.export_alerts_csv("alerts.csv")

# Clean old files (older than 30 days)
deleted = logger.cleanup_old_alerts(days=30)
```

---

## 📸 What Gets Logged?

Each alert includes:

### 🖼️ **Image** (JPG)
- Screenshot of the frame
- With visual annotations (boxes, labels, scores)

### 📋 **Metadata** (JSON)
```json
{
  "alert_id": "CRIME_20250109_153245_123",
  "timestamp": "2025-01-09T15:32:45.123",
  "datetime_readable": "2025-01-09 15:32:45.123",
  "threat_score": 0.78,           ← Main threat level
  "confidence": 0.85,              ← Detection confidence
  "weapons_detected": 1,           ← # of weapons found
  "motion_score": 0.6,             ← Motion component
  "cluster_score": 0.2,            ← Clustering component
  "image_file": "CRIME_.._.jpg"
}
```

### 📅 **Daily Log** (JSON Array)
Aggregated list of all alerts for that day

---

## 💾 Storage Usage

| Scenario | Storage | Files |
|----------|---------|-------|
| 10 alerts/day × 30 days | ~50-60 MB | 600 files |
| 100 alerts/day × 30 days | ~500-600 MB | 6000 files |

---

## 🔧 Key Features

| Feature | Where to Use | Benefit |
|---------|-------------|---------|
| **Auto-logging** | Live Webcam & Video Upload | Never miss an alert |
| **High-threat filter** | Analytics → High Threat Tab | Focus on serious incidents |
| **Export to CSV** | Analytics → Management Tab | Analyze in Excel/Python |
| **Auto-cleanup** | Analytics → Management Tab | Free up disk space |
| **Daily summary** | Analytics → Storage Info Tab | Daily incident review |

---

## ⚡ Real-Time Flow

```
Detection Loop
    ↓
Crime Detected (Score ≥ threshold)
    ↓
Log Alert
    ├→ Save image: alerts/images/CRIME_*.jpg
    ├→ Save metadata: alerts/metadata/CRIME_*.json
    └→ Update daily log: alerts/daily_logs/YYYYMMDD_alerts.json
    ↓
Continue Detection
```

---

## 🎯 Typical Use Cases

### Case 1: Review Today's Incidents
```python
from alert_logger import AlertLogger

logger = AlertLogger("alerts")
today = logger.get_alert_summary()
print(f"Today: {today['total_alerts']} incidents detected")
```

### Case 2: Find High-Severity Events
```python
serious = logger.get_high_threat_alerts(threshold=0.8)
print(f"Found {len(serious)} serious incidents (score ≥ 0.8)")
```

### Case 3: Export for Investigation
```python
# Export suspicious period
logger.export_alerts_csv("investigation.csv")
# Use in Excel for analysis
```

### Case 4: Disk Cleanup
```python
# Keep only last 7 days
deleted = logger.cleanup_old_alerts(days=7)
print(f"Freed up space: deleted {deleted} old files")
```

---

## 📊 Analytics Dashboard Integration

The alerts viewer is built into the Analytics Dashboard with 4 tabs:

### Tab 1: Recent Alerts 📋
- Sortable list of all alerts
- Click to view full JSON details
- Adjustable limit (5-100)

### Tab 2: High Threat Alerts 🔥
- Filter by threat score
- Shows only serious incidents
- Quick review of critical events

### Tab 3: Storage Info 📊
- Total alerts logged
- Disk usage (images + metadata)
- Today's summary stats

### Tab 4: Alert Management ⚙️
- **Cleanup**: Delete old alerts
- **Export**: Download as CSV
- **Info**: Folder structure guide

---

## ✅ Success Indicators

When alerts are working correctly, you should see:

✓ Console message: `✅ Alert logger initialized at: ...`
✓ Files created in `alerts/` directory
✓ Daily logs in `alerts/daily_logs/`
✓ Images in `alerts/images/`
✓ Metadata in `alerts/metadata/`

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| No alerts logging | Check crime threshold (should be ≤ 0.35 by default) |
| Can't find alerts | Check that detection is running (see threat score in UI) |
| Disk full | Run cleanup: `logger.cleanup_old_alerts(days=7)` |
| CSV export fails | Check file permissions in current directory |

---

## 📞 Support

For issues or questions about alert logging:
1. Check `ALERT_LOGGING_README.md` for detailed docs
2. Review alert files in `alerts/` directory
3. Check console output for error messages

---

**System Status**: ✅ **PRODUCTION READY**

All alerts are automatically captured and stored. No configuration needed!

**Version**: 1.0 | **Date**: November 9, 2025
