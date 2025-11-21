#!/usr/bin/env python3
import os
from dotenv import load_dotenv
load_dotenv()

from supabase_sync import SupabaseSync

print("\n" + "="*70)
print("☁️  CHECKING ALERTS IN SUPABASE CLOUD")
print("="*70 + "\n")

sync = SupabaseSync()

if sync.connected:
    print("✅ Connected to Supabase\n")
    
    # Get all verified alerts
    alerts = sync.get_alerts(limit=10)
    
    print(f"📊 Total Alerts in Cloud: {len(alerts)}\n")
    
    if len(alerts) > 0:
        print("Recent Alerts:")
        print("-" * 70)
        for i, alert in enumerate(alerts[:5], 1):
            print(f"\n{i}. {alert.get('alert_id', 'Unknown')}")
            print(f"   Threat Score: {alert.get('threat_score', 0):.2f}")
            print(f"   Confidence: {alert.get('confidence', 0):.2f}")
            print(f"   Weapons: {alert.get('weapons_detected', 0)}")
            print(f"   Synced: {alert.get('created_at', 'Unknown')}")
        
        print("\n" + "-" * 70)
    else:
        print("ℹ️  No alerts in cloud yet")
else:
    print("❌ Not connected to Supabase")

print("\n" + "="*70 + "\n")
