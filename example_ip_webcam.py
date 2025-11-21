#!/usr/bin/env python3
"""
Simple example: How to use IP Webcam URL

Usage:
    python example_ip_webcam.py
"""

from backend.live_detection import LiveDetectionWorker
import time

# ========================================
# 🎯 STEP 1: PUT YOUR PHONE'S IP HERE
# ========================================
PHONE_IP = "192.168.1.100"  # ← CHANGE THIS TO YOUR PHONE'S IP

# ========================================
# 🎯 STEP 2: CHOOSE YOUR APP
# ========================================
# DroidCam uses port 4747
# IP Webcam uses port 8080
# Iriun uses port 8080

APP_PORT = "8080"  # Change to "4747" if using DroidCam

# ========================================
# 🎯 STEP 3: BUILD THE URL
# ========================================
IP_WEBCAM_URL = f"http://{PHONE_IP}:{APP_PORT}/video"

print("=" * 60)
print("📱 IP WEBCAM EXAMPLE")
print("=" * 60)
print(f"Phone IP: {PHONE_IP}")
print(f"App Port: {APP_PORT}")
print(f"Full URL: {IP_WEBCAM_URL}")
print("=" * 60)

# ========================================
# 🎯 STEP 4: CREATE WORKER WITH URL
# ========================================
try:
    print("\n🚀 Starting video capture...")
    worker = LiveDetectionWorker(video_source=IP_WEBCAM_URL)
    worker.start()
    
    # ========================================
    # 🎯 STEP 5: MONITOR STATUS
    # ========================================
    print("⏳ Waiting for connection...")
    time.sleep(3)
    
    status = worker.get_state()
    
    print("\n" + "=" * 60)
    print("✅ STATUS:")
    print("=" * 60)
    print(f"Running: {status['running']}")
    print(f"Source Type: {status['source_type']}")
    print(f"Video Source: {status['video_source']}")
    print(f"Connection Errors: {status['connection_errors']}")
    print(f"Frames Captured: {status['frame_count']}")
    print(f"FPS: {status['fps']}")
    print("=" * 60)
    
    if status['running']:
        print("\n🎉 SUCCESS! IP Webcam is working!")
        print("\nMonitoring video stream (press Ctrl+C to stop)...")
        
        try:
            while worker.running:
                time.sleep(1)
                stats = worker.get_state()
                print(f"Frame: {stats['frame_count']} | Crimes: {stats.get('latest_results', {}).get('is_crime', False)} | FPS: {stats['fps']}")
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping...")
            worker.stop()
            print("✅ Stopped!")
    else:
        print("\n❌ FAILED TO CONNECT")
        print(f"Connection errors: {status['connection_errors']}")
        print("\nTroubleshooting:")
        print("1. Verify phone IP is correct")
        print("2. Check phone is on same WiFi")
        print("3. Verify IP Webcam app is running")
        print("4. Test URL in browser: " + IP_WEBCAM_URL)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Check phone IP address")
    print("2. Verify WiFi connection")
    print("3. Test URL directly in browser")
    print("4. Make sure IP Webcam app is running")
