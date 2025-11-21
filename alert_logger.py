"""
Alert Logging System for CCTV Crime Detection
Logs crime detection events with images and metadata to organized folders
"""

import os
import json
import cv2
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy/non-standard types"""
    def default(self, obj):
        if isinstance(obj, bool):
            return bool(obj)
        if isinstance(obj, (int, float)):
            return float(obj) if isinstance(obj, float) else int(obj)
        if hasattr(obj, '__float__'):
            return float(obj)
        return super().default(obj)


class AlertLogger:
    """Logs crime detection alerts with images and JSON metadata."""
    
    def __init__(self, alert_dir: str = "alerts", interval_seconds: int = 0):
        """
        Initialize alert logger.
        
        Args:
            alert_dir: Base directory for storing alerts (default: "alerts")
            interval_seconds: Minimum seconds between alert images (default: 0 = always save)
        """
        self.base_dir = Path(alert_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for organized storage
        self.images_dir = self.base_dir / "images"
        self.metadata_dir = self.base_dir / "metadata"
        self.daily_logs_dir = self.base_dir / "daily_logs"
        
        self.images_dir.mkdir(exist_ok=True)
        self.metadata_dir.mkdir(exist_ok=True)
        self.daily_logs_dir.mkdir(exist_ok=True)
        
        # Interval tracking for continuous detection
        self.last_alert_time = 0
        self.interval_seconds = interval_seconds
        
        print(f"✅ Alert logger initialized at: {self.base_dir.absolute()}")
    
    def log_alert(self, frame, detection_results: Dict, alert_type: str = "CRIME") -> Optional[Dict]:
        """
        Log a crime detection alert with image and metadata.
        
        Args:
            frame: OpenCV image (BGR format)
            detection_results: Dict with detection results from cctv_detector.detect_frame()
            alert_type: Type of alert ("CRIME", "WEAPON", "MOTION", "CLUSTER")
            
        Returns:
            Dict with log information or None if logging failed
        """
        try:
            timestamp = datetime.now()
            current_time = timestamp.timestamp()
            
            # Check if enough time has passed since last alert image
            time_since_last = current_time - self.last_alert_time
            should_save_image = time_since_last >= self.interval_seconds
            
            if should_save_image:
                self.last_alert_time = current_time
            
            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
            
            # Create alert ID
            alert_id = f"{alert_type}_{timestamp_str}"
            
            # 1. Save Image (only if interval elapsed)
            image_filename = None
            image_path = None
            if should_save_image:
                image_filename = f"{alert_id}.jpg"
                image_path = self.images_dir / image_filename
                cv2.imwrite(str(image_path), frame)
            
            # 2. Create Metadata JSON
            metadata = {
                "alert_id": alert_id,
                "timestamp": timestamp.isoformat(),
                "datetime_readable": timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "alert_type": alert_type,
                "frame_number": int(detection_results.get('frame_num', 0)),
                "threat_score": float(detection_results.get('smoothed_score', 0)),
                "confidence": float(detection_results.get('confidence', 0)),
                "is_crime": bool(detection_results.get('is_crime', False)),
                "image_saved": should_save_image,  # Track if image was saved
                "detection_details": {
                    "weapons_detected": int(len(detection_results.get('weapons', []))),
                    "motion_score": float(detection_results.get('motion_score', 0)),
                    "cluster_score": float(detection_results.get('cluster_score', 0)),
                    "crime_score": float(detection_results.get('crime_score', 0))
                },
                "weapons": [
                    {
                        "confidence": float(w.get('confidence', 0)),
                        "class": w.get('class', 'weapon'),
                        "box": w.get('box', [])
                    }
                    for w in detection_results.get('weapons', [])
                ],
                "image_file": image_filename,
                "image_path": str(image_path) if image_path else None
            }
            
            # 3. Save Metadata JSON
            metadata_filename = f"{alert_id}.json"
            metadata_path = self.metadata_dir / metadata_filename
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, cls=NumpyEncoder)
            
            # 4. Update Daily Log
            daily_log_file = self.daily_logs_dir / f"{timestamp.strftime('%Y%m%d')}_alerts.json"
            
            daily_alerts = []
            if daily_log_file.exists():
                try:
                    with open(daily_log_file, 'r') as f:
                        daily_alerts = json.load(f)
                except json.JSONDecodeError:
                    # If corrupted, start fresh
                    daily_alerts = []
                    print(f"⚠️ Corrupted daily log, resetting...")
            
            # Add entry to daily log (without image data for file size)
            daily_entry = {
                "alert_id": alert_id,
                "timestamp": timestamp.isoformat(),
                "datetime_readable": timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "alert_type": alert_type,
                "threat_score": float(detection_results.get('smoothed_score', 0)),
                "confidence": float(detection_results.get('confidence', 0)),
                "image_file": image_filename,
                "metadata_file": metadata_filename
            }
            daily_alerts.append(daily_entry)
            
            # Write to temporary file first, then rename (atomic operation)
            temp_log_file = daily_log_file.with_suffix('.tmp')
            try:
                with open(temp_log_file, 'w') as f:
                    json.dump(daily_alerts, f, indent=2, cls=NumpyEncoder)
                # Atomic rename
                temp_log_file.replace(daily_log_file)
            except Exception as e:
                print(f"⚠️ Error writing daily log: {str(e)}")
                if temp_log_file.exists():
                    temp_log_file.unlink()
            
            # 5. Return log info
            log_info = {
                "status": "success",
                "alert_id": alert_id,
                "timestamp": timestamp.isoformat(),
                "image_saved": should_save_image,
                "image_path": str(image_path) if image_path else None,
                "metadata_path": str(metadata_path),
                "daily_log": str(daily_log_file)
            }
            
            # Print status based on whether image was saved
            if should_save_image:
                print(f"📸 Alert logged: {alert_id}")
                print(f"   Image: {image_path}")
                print(f"   Metadata: {metadata_path}")
            else:
                print(f"📝 Alert metadata: {alert_id} (image skipped - interval not elapsed)")
            
            return log_info
            
        except Exception as e:
            print(f"❌ Error logging alert: {str(e)}")
            return None
    
    def get_alert_summary(self, date_str: Optional[str] = None) -> Dict:
        """
        Get summary of alerts for a specific date.
        
        Args:
            date_str: Date string in format "YYYYMMDD" (default: today)
            
        Returns:
            Dict with alert summary
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y%m%d")
        
        daily_log_file = self.daily_logs_dir / f"{date_str}_alerts.json"
        
        if not daily_log_file.exists():
            return {
                "date": date_str,
                "total_alerts": 0,
                "alerts": []
            }
        
        with open(daily_log_file, 'r') as f:
            alerts = json.load(f)
        
        # Calculate statistics
        total_alerts = len(alerts)
        crime_alerts = sum(1 for a in alerts if a.get('alert_type') == 'CRIME')
        avg_threat = sum(a.get('threat_score', 0) for a in alerts) / max(1, total_alerts)
        
        return {
            "date": date_str,
            "total_alerts": total_alerts,
            "crime_alerts": crime_alerts,
            "average_threat_score": round(avg_threat, 3),
            "alerts": alerts
        }
    
    def get_all_alerts(self, limit: int = 100) -> list:
        """
        Get all recent alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of alerts sorted by timestamp (most recent first)
        """
        all_alerts = []
        
        # Read all daily logs
        for daily_log in sorted(self.daily_logs_dir.glob("*.json"), reverse=True):
            with open(daily_log, 'r') as f:
                alerts = json.load(f)
                all_alerts.extend(alerts)
        
        # Sort by timestamp (most recent first)
        all_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return all_alerts[:limit]
    
    def get_high_threat_alerts(self, threshold: float = 0.7, limit: int = 50) -> list:
        """
        Get high-threat alerts.
        
        Args:
            threshold: Threat score threshold (0-1)
            limit: Maximum number to return
            
        Returns:
            List of high-threat alerts
        """
        all_alerts = self.get_all_alerts(limit * 2)
        high_threat = [a for a in all_alerts if a.get('threat_score', 0) >= threshold]
        return high_threat[:limit]
    
    def export_alerts_csv(self, output_file: str = "alerts_export.csv") -> bool:
        """
        Export all alerts to CSV file.
        
        Args:
            output_file: Output CSV filename
            
        Returns:
            True if successful
        """
        try:
            import csv
            
            all_alerts = self.get_all_alerts(limit=10000)
            
            if not all_alerts:
                print("No alerts to export")
                return False
            
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=all_alerts[0].keys())
                writer.writeheader()
                writer.writerows(all_alerts)
            
            print(f"✅ Exported {len(all_alerts)} alerts to {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting CSV: {str(e)}")
            return False
    
    def cleanup_old_alerts(self, days: int = 30) -> int:
        """
        Delete alerts older than specified days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of files deleted
        """
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            # Delete old images
            for image_file in self.images_dir.glob("*.jpg"):
                file_time = datetime.fromtimestamp(image_file.stat().st_mtime)
                if file_time < cutoff_date:
                    image_file.unlink()
                    deleted_count += 1
            
            # Delete old metadata
            for metadata_file in self.metadata_dir.glob("*.json"):
                file_time = datetime.fromtimestamp(metadata_file.stat().st_mtime)
                if file_time < cutoff_date:
                    metadata_file.unlink()
                    deleted_count += 1
            
            print(f"🧹 Cleaned up {deleted_count} old alert files (older than {days} days)")
            return deleted_count
            
        except Exception as e:
            print(f"❌ Error cleaning up alerts: {str(e)}")
            return 0
    
    def get_storage_info(self) -> Dict:
        """
        Get storage information about alerts.
        
        Returns:
            Dict with storage stats
        """
        def get_dir_size(path):
            total = 0
            for f in path.glob("**/*"):
                if f.is_file():
                    total += f.stat().st_size
            return total
        
        images_size = get_dir_size(self.images_dir)
        metadata_size = get_dir_size(self.metadata_dir)
        total_size = images_size + metadata_size
        
        num_images = len(list(self.images_dir.glob("*.jpg")))
        num_metadata = len(list(self.metadata_dir.glob("*.json")))
        
        return {
            "total_alerts": num_images,
            "images_size_mb": round(images_size / (1024 * 1024), 2),
            "metadata_size_mb": round(metadata_size / (1024 * 1024), 2),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "storage_path": str(self.base_dir.absolute())
        }


# Example usage and testing
if __name__ == "__main__":
    print("🔍 Alert Logger Module")
    print("=" * 50)
    
    # Initialize logger
    logger = AlertLogger("alerts")
    
    # Get storage info
    info = logger.get_storage_info()
    print("\n📊 Storage Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Get today's summary
    summary = logger.get_alert_summary()
    print(f"\n📈 Today's Summary:")
    print(f"  Total alerts: {summary['total_alerts']}")
    if summary['total_alerts'] > 0:
        print(f"  Average threat score: {summary['average_threat_score']}")
    
    # Get recent alerts
    recent = logger.get_all_alerts(limit=5)
    if recent:
        print(f"\n📋 Recent Alerts (last 5):")
        for alert in recent:
            print(f"  - {alert['datetime_readable']}: {alert['alert_type']} (Score: {alert['threat_score']})")
