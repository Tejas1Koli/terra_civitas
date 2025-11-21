#!/usr/bin/env python3
"""
Cloud Setup Verification Script
Checks if Supabase integration is properly configured
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_env_variables():
    """Check if Supabase environment variables are set."""
    print("\n📋 Checking Environment Variables...")
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if url and key:
        print(f"✅ SUPABASE_URL: {url[:30]}...")
        print(f"✅ SUPABASE_KEY: {key[:30]}...")
        return True
    else:
        print("❌ Missing environment variables!")
        print("   Create .env file with:")
        print("   SUPABASE_URL=your_url")
        print("   SUPABASE_KEY=your_key")
        return False

def check_python_packages():
    """Check if required Python packages are installed."""
    print("\n📦 Checking Python Packages...")
    
    required = ['supabase', 'streamlit', 'cv2', 'ultralytics']
    missing = []
    
    for package in required:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'ultralytics':
                import ultralytics
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            missing.append(package)
    
    if missing:
        print(f"\n🔧 Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        return False
    return True

def check_supabase_connection():
    """Test Supabase connection."""
    print("\n🔗 Testing Supabase Connection...")
    
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ Supabase credentials not set")
            return False
        
        client = create_client(url, key)
        print("✅ Connected to Supabase")
        
        # Try to query the verified_alerts table
        try:
            response = client.table("verified_alerts").select("count", count="exact").execute()
            print(f"✅ verified_alerts table exists")
            return True
        except Exception as e:
            print(f"⚠️  Could not access verified_alerts table: {e}")
            print("   Create the table using SUPABASE_SETUP.md instructions")
            return False
    
    except ImportError:
        print("❌ supabase package not installed")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def check_alert_directories():
    """Check if alert directories exist."""
    print("\n📁 Checking Alert Directories...")
    
    dirs = [
        Path("alerts"),
        Path("alerts/images"),
        Path("alerts/metadata"),
        Path("verified_alerts"),
        Path("verified_alerts/images"),
        Path("verified_alerts/metadata"),
    ]
    
    all_exist = True
    for dir_path in dirs:
        if dir_path.exists():
            # Count files if it's an image/metadata directory
            if "images" in dir_path.name or "metadata" in dir_path.name:
                count = len(list(dir_path.glob("*")))
                print(f"✅ {dir_path} ({count} files)")
            else:
                print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - missing")
            all_exist = False
    
    return all_exist

def check_config_files():
    """Check if required config files exist."""
    print("\n⚙️  Checking Configuration Files...")
    
    files = [
        ("supabase_sync.py", "Cloud sync module"),
        ("cctv_app_admin.py", "Admin app with cloud integration"),
        (".env", "Environment variables"),
    ]
    
    all_exist = True
    for filename, description in files:
        path = Path(filename)
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {filename} ({size} bytes) - {description}")
        else:
            if filename != ".env":  # .env is optional initially
                print(f"❌ {filename} - missing")
                all_exist = False
            else:
                print(f"⚠️  {filename} - not configured")
    
    return all_exist

def main():
    """Run all checks."""
    print("=" * 60)
    print("🚀 CCTV Alert System - Cloud Setup Verification")
    print("=" * 60)
    
    results = {
        "Environment Variables": check_env_variables(),
        "Python Packages": check_python_packages(),
        "Alert Directories": check_alert_directories(),
        "Config Files": check_config_files(),
        "Supabase Connection": check_supabase_connection(),
    }
    
    print("\n" + "=" * 60)
    print("📊 SETUP SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! System is ready to sync alerts to cloud.")
        print("\nNext steps:")
        print("1. Start your app: ./start.sh")
        print("2. Admin detects and verifies crimes")
        print("3. Alerts automatically sync to Supabase")
        print("4. Build React frontend using REACT_FRONTEND_GUIDE.md")
        return 0
    else:
        print("\n⚠️  Some checks failed. See details above.")
        print("\nFor help, see:")
        print("- SUPABASE_SETUP.md - Cloud setup instructions")
        print("- REACT_FRONTEND_GUIDE.md - Frontend integration")
        return 1

if __name__ == "__main__":
    sys.exit(main())
