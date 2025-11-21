#!/usr/bin/env python3
"""
Test Alert Sync to Supabase
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env file first!
load_dotenv()

from supabase_sync import SupabaseSync

print("\n" + "="*70)
print("🧪 TESTING ALERT SYNC TO SUPABASE")
print("="*70 + "\n")

# Check env vars
print("📋 Checking credentials...")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
print(f"   URL: {url[:40] if url else 'NOT SET'}...")
print(f"   KEY: {key[:40] if key else 'NOT SET'}...\n")

# Initialize sync
print("📋 Connecting to Supabase...")
sync = SupabaseSync()

if not sync.connected:
    print("❌ Could not connect to Supabase!")
    exit(1)

print("✅ Connected!\n")

# Check verified alerts
verified_path = Path("verified_alerts")
if (verified_path / "images").exists():
    verified_images = list((verified_path / "images").glob("*.jpg"))
    print(f"📋 Found {len(verified_images)} verified alerts locally\n")
    
    if len(verified_images) > 0:
        # Get first one
        test_alert = verified_images[0]
        alert_id = test_alert.stem
        print(f"📋 Alert to sync: {alert_id}")
        
        # Get metadata
        metadata_file = verified_path / "metadata" / f"{alert_id}.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                alert_data = json.load(f)
            
            print(f"\n📊 Alert Details:")
            print(f"   Threat Score: {alert_data.get('threat_score', 0)}")
            print(f"   Confidence: {alert_data.get('confidence', 0)}")
            
            print(f"\n☁️  Syncing to Supabase...")
            result = sync.push_alert(alert_id, "verified_alerts")
            
            if result:
                print("✅ Alert synced!")
                synced = sync.get_alert_by_id(alert_id)
                if synced:
                    print(f"✅ Verified in cloud: {synced['alert_id']}")
        else:
            print(f"⚠️  Metadata not found")
    else:
        print("ℹ️  No verified alerts yet")
else:
    print("ℹ️  No verified_alerts folder yet")

print("\n" + "="*70 + "\n")
