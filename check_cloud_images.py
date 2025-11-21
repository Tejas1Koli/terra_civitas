#!/usr/bin/env python3
import os
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

print("\n" + "="*70)
print("📸 CHECKING IMAGES IN SUPABASE STORAGE")
print("="*70 + "\n")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if url and key:
    client = create_client(url, key)
    
    print("✅ Connected to Supabase\n")
    
    # List buckets
    print("📋 Checking Storage Buckets...")
    try:
        buckets = client.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        print(f"Available buckets: {bucket_names}\n")
        
        # Check alert-images bucket
        if "alert-images" in bucket_names:
            print("✅ Found 'alert-images' bucket!\n")
            
            # List files in bucket
            print("📸 Files in alert-images bucket:")
            try:
                files = client.storage.from_("alert-images").list(path="verified_alerts/images")
                if files:
                    print(f"   Found {len(files)} images:\n")
                    for file in files[:5]:
                        print(f"   • {file['name']}")
                        if len(files) > 5:
                            print(f"   ... and {len(files) - 5} more")
                            break
                else:
                    print("   ℹ️  No images found in bucket yet")
            except Exception as e:
                print(f"   ⚠️  Could not list files: {e}")
        else:
            print("⚠️  'alert-images' bucket NOT found!")
            print("   Create it in: Supabase → Storage → New Bucket")
            print("   Name: alert-images")
            print("   Make Public: YES")
    
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ Credentials not found")

print("\n" + "="*70 + "\n")
