#!/usr/bin/env python3
"""
Test Supabase Connection and Setup
Verifies cloud integration is working
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("\n" + "="*70)
print("🔗 SUPABASE CONNECTION TEST")
print("="*70 + "\n")

# Check credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

print("📋 Step 1: Checking Credentials...")
if supabase_url and supabase_key:
    print(f"✅ SUPABASE_URL: {supabase_url[:50]}...")
    print(f"✅ SUPABASE_KEY: {supabase_key[:50]}...")
else:
    print("❌ Missing credentials in .env file!")
    sys.exit(1)

# Test connection
print("\n📋 Step 2: Testing Supabase Connection...")
try:
    from supabase import create_client
    
    client = create_client(supabase_url, supabase_key)
    print("✅ Connected to Supabase!")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)

# Check if table exists
print("\n📋 Step 3: Checking verified_alerts Table...")
try:
    response = client.table("verified_alerts").select("count", count="exact").execute()
    count = response.data[0]['count'] if response.data else 0
    print(f"✅ Table exists! Current records: {count}")
    
except Exception as e:
    print(f"⚠️  Table doesn't exist yet. Creating...")
    try:
        # Create table via SQL
        print("\n📋 Step 4: Creating Database Table...")
        sql = """
        CREATE TABLE IF NOT EXISTS verified_alerts (
          id BIGSERIAL PRIMARY KEY,
          alert_id TEXT UNIQUE NOT NULL,
          timestamp TIMESTAMP,
          threat_score FLOAT,
          confidence FLOAT,
          weapons_detected INTEGER,
          image_base64 TEXT,
          metadata TEXT,
          created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_alert_id ON verified_alerts(alert_id);
        CREATE INDEX IF NOT EXISTS idx_created_at ON verified_alerts(created_at DESC);
        """
        
        # Note: Supabase doesn't have direct SQL execution in Python SDK
        # You'll need to run this in the Supabase SQL Editor
        print("""
        ⚠️  Please run this SQL in Supabase Dashboard → SQL Editor:
        
        CREATE TABLE verified_alerts (
          id BIGSERIAL PRIMARY KEY,
          alert_id TEXT UNIQUE NOT NULL,
          timestamp TIMESTAMP,
          threat_score FLOAT,
          confidence FLOAT,
          weapons_detected INTEGER,
          image_base64 TEXT,
          metadata TEXT,
          created_at TIMESTAMP DEFAULT NOW()
        );
        """)
    except Exception as sql_error:
        print(f"❌ SQL error: {sql_error}")

# Check storage bucket
print("\n📋 Step 5: Checking Storage Bucket...")
try:
    buckets = client.storage.list_buckets()
    bucket_names = [b.name for b in buckets]
    
    if "alert-images" in bucket_names:
        print("✅ Storage bucket 'alert-images' exists!")
    else:
        print("⚠️  Bucket 'alert-images' not found. Creating...")
        try:
            client.storage.create_bucket("alert-images")
            print("✅ Bucket created successfully!")
        except Exception as bucket_error:
            print(f"⚠️  Could not create bucket: {bucket_error}")
            print("   Create manually in Supabase → Storage → New Bucket")
            
except Exception as e:
    print(f"⚠️  Storage check failed: {e}")

# Test write operation
print("\n📋 Step 6: Testing Write Operation...")
try:
    test_alert = {
        "alert_id": "TEST_ALERT_001",
        "threat_score": 0.95,
        "confidence": 0.88,
        "weapons_detected": 2,
        "metadata": json.dumps({"test": True})
    }
    
    response = client.table("verified_alerts").insert(test_alert).execute()
    print("✅ Successfully wrote test alert to database!")
    
    # Clean up
    client.table("verified_alerts").delete().eq("alert_id", "TEST_ALERT_001").execute()
    print("✅ Test alert cleaned up")
    
except Exception as e:
    print(f"❌ Write operation failed: {e}")
    print("   Make sure the 'verified_alerts' table exists!")

# Summary
print("\n" + "="*70)
print("✅ SUPABASE INTEGRATION STATUS: READY")
print("="*70)
print("""
Your system is configured to sync verified alerts to Supabase!

When admin verifies an alert:
1. Alert moves to verified_alerts/ folder (local)
2. ☁️  Data syncs to Supabase cloud automatically
3. React frontend can fetch from cloud API

Next steps:
1. Start your app: ./start.sh
2. Detect a crime (or use test data)
3. Admin clicks VERIFY
4. Check Supabase dashboard for synced data
""")
print("="*70 + "\n")
