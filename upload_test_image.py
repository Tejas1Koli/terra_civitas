#!/usr/bin/env python3
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

print("\n" + "="*70)
print("📸 TESTING IMAGE UPLOAD TO SUPABASE STORAGE")
print("="*70 + "\n")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

client = create_client(url, key)

# Find a verified alert image
verified_path = Path("verified_alerts/images")
if verified_path.exists():
    images = list(verified_path.glob("*.jpg"))
    if images:
        test_image = images[0]
        print(f"📸 Test image: {test_image.name}\n")
        
        # Read image
        with open(test_image, "rb") as f:
            image_data = f.read()
        
        print(f"📊 Image size: {len(image_data) / 1024:.1f} KB\n")
        
        # Try to upload
        print("☁️  Uploading to alert-images bucket...")
        try:
            storage_path = f"verified_alerts/images/{test_image.name}"
            response = client.storage.from_("alert-images").upload(
                path=storage_path,
                file=image_data,
                file_options={"content-type": "image/jpeg"}
            )
            print(f"✅ Upload successful!")
            print(f"   Path: {storage_path}\n")
            
            # Get public URL
            try:
                public_url = client.storage.from_("alert-images").get_public_url(storage_path)
                print(f"✅ Public URL: {public_url}\n")
            except:
                pass
            
        except Exception as e:
            print(f"❌ Upload failed: {e}\n")
    else:
        print("ℹ️  No verified images found")
else:
    print("ℹ️  No verified_alerts folder")

print("="*70 + "\n")
