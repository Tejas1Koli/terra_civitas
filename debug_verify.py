#!/usr/bin/env python3
"""Debug script to test the verify button functionality."""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from cctv_app_admin import move_to_verified_alerts

# Test with a real alert from the alerts folder
alerts_path = Path("alerts/images")
if alerts_path.exists():
    images = list(alerts_path.glob("CRIME_*.jpg"))
    if images:
        # Get the most recent alert
        latest = sorted(images)[-1]
        alert_id = latest.stem
        
        print(f"\n🧪 Testing verify button functionality")
        print(f"   Alert ID: {alert_id}")
        print(f"   Testing move_to_verified_alerts()...\n")
        
        result = move_to_verified_alerts(alert_id)
        
        print(f"\n   Result: {'✅ SUCCESS' if result else '❌ FAILED'}")
        
        # Check files
        verified_img = Path("verified_alerts/images") / f"{alert_id}.jpg"
        verified_meta = Path("verified_alerts/metadata") / f"{alert_id}.json"
        
        print(f"   Image copied: {verified_img.exists()}")
        print(f"   Metadata copied: {verified_meta.exists()}")
    else:
        print("❌ No alerts found in alerts/images/")
else:
    print("❌ alerts/images/ directory not found")
