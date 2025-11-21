#!/usr/bin/env python3
"""Test script to verify move_to_verified_alerts() function works correctly."""

import sys
from pathlib import Path

# Import the function
from cctv_app_admin import move_to_verified_alerts

def test_move_function():
    """Test the move_to_verified_alerts function."""
    
    # Get a sample alert ID from the alerts/images directory
    alerts_path = Path("alerts/images")
    
    if not alerts_path.exists():
        print("❌ alerts/images directory not found!")
        return False
    
    # Find first available alert
    image_files = list(alerts_path.glob("CRIME_*.jpg"))
    
    if not image_files:
        print("❌ No alert images found in alerts/images/")
        return False
    
    # Get the first alert ID (without extension)
    first_image = image_files[0]
    alert_id = first_image.stem  # Gets filename without extension
    
    print(f"\n{'='*60}")
    print(f"Testing move_to_verified_alerts() function")
    print(f"{'='*60}")
    print(f"\nTest Alert ID: {alert_id}")
    print(f"Source Image: {first_image.name}")
    
    # Check source files exist
    print(f"\n📂 Checking source files...")
    
    image_file = alerts_path / f"{alert_id}.jpg"
    metadata_file = Path("alerts/metadata") / f"{alert_id}.json"
    
    print(f"   Image exists: {image_file.exists()} - {image_file}")
    print(f"   Metadata exists: {metadata_file.exists()} - {metadata_file}")
    
    if not image_file.exists():
        print("❌ Source image not found!")
        return False
    
    if not metadata_file.exists():
        print("❌ Source metadata not found!")
        return False
    
    # Call the function
    print(f"\n🚀 Calling move_to_verified_alerts('{alert_id}')...")
    result = move_to_verified_alerts(alert_id)
    
    # Verify results
    print(f"\n📂 Checking destination files...")
    
    dest_image = Path("verified_alerts/images") / f"{alert_id}.jpg"
    dest_metadata = Path("verified_alerts/metadata") / f"{alert_id}.json"
    
    image_copied = dest_image.exists()
    metadata_copied = dest_metadata.exists()
    
    print(f"   Image exists: {image_copied} - {dest_image}")
    print(f"   Metadata exists: {metadata_copied} - {dest_metadata}")
    
    # Summary
    print(f"\n{'='*60}")
    if result and image_copied and metadata_copied:
        print("✅ TEST PASSED - Function worked correctly!")
        print(f"   ✅ Image copied to verified_alerts/images/")
        print(f"   ✅ Metadata copied to verified_alerts/metadata/")
        return True
    else:
        print("❌ TEST FAILED")
        if not image_copied:
            print(f"   ❌ Image was not copied")
        if not metadata_copied:
            print(f"   ❌ Metadata was not copied")
        return False
    print(f"{'='*60}\n")

if __name__ == "__main__":
    success = test_move_function()
    sys.exit(0 if success else 1)
