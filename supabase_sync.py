"""
Supabase Cloud Sync Module
Syncs verified alerts to Supabase database
"""

import os
import json
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from supabase import create_client, Client
except ImportError:
    print("⚠️ Install supabase: pip install supabase")
    Client = None


class SupabaseSync:
    """Handles all Supabase synchronization for verified alerts"""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize Supabase client
        
        Args:
            supabase_url: Supabase project URL (env: SUPABASE_URL)
            supabase_key: Supabase API key (env: SUPABASE_KEY)
        """
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        self.client: Optional[Client] = None
        self.connected = False
        
        if self.supabase_url and self.supabase_key:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
                self.connected = True
                print("✅ Connected to Supabase")
            except Exception as e:
                print(f"❌ Supabase connection failed: {e}")
                self.connected = False
        else:
            print("⚠️ Supabase credentials not set. Set SUPABASE_URL and SUPABASE_KEY environment variables")
    
    def push_alert(self, alert_id: str, alert_path: str = "verified_alerts") -> bool:
        """
        Push a verified alert to Supabase
        
        Args:
            alert_id: Alert ID (e.g., CRIME_20251115_170300_123)
            alert_path: Path to verified_alerts folder
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            alerts_path = Path(alert_path)
            image_file = alerts_path / "images" / f"{alert_id}.jpg"
            meta_file = alerts_path / "metadata" / f"{alert_id}.json"
            
            if not image_file.exists() or not meta_file.exists():
                print(f"⚠️ Alert files not found: {alert_id}")
                return False
            
            # Load metadata
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
            
            # Read image and encode to base64
            with open(image_file, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Prepare alert data
            alert_data = {
                "alert_id": alert_id,
                "timestamp": metadata.get("timestamp"),
                "threat_score": metadata.get("threat_score"),
                "confidence": metadata.get("confidence"),
                "weapons_detected": metadata.get("detection_details", {}).get("weapons_detected", 0),
                "image_base64": image_data,  # Store image as base64
                "metadata": json.dumps(metadata),  # Store full metadata as JSON string
                "created_at": datetime.now().isoformat()
            }
            
            # Insert into Supabase
            response = self.client.table("verified_alerts").insert(alert_data).execute()
            
            if response.data:
                print(f"✅ Alert pushed to Supabase: {alert_id}")
                return True
            else:
                print(f"❌ Failed to push alert: {alert_id}")
                return False
        
        except Exception as e:
            print(f"❌ Error pushing alert: {e}")
            return False
    
    def get_alerts(self, limit: int = 50, offset: int = 0) -> list:
        """
        Fetch verified alerts from Supabase
        
        Args:
            limit: Number of alerts to fetch
            offset: Pagination offset
        
        Returns:
            List of alert dictionaries
        """
        if not self.connected:
            return []
        
        try:
            response = self.client.table("verified_alerts") \
                .select("*") \
                .order("created_at", desc=True) \
                .range(offset, offset + limit - 1) \
                .execute()
            
            return response.data if response.data else []
        
        except Exception as e:
            print(f"❌ Error fetching alerts: {e}")
            return []
    
    def get_alert_by_id(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific alert by ID
        
        Args:
            alert_id: Alert ID to fetch
        
        Returns:
            Alert dictionary or None
        """
        if not self.connected:
            return None
        
        try:
            response = self.client.table("verified_alerts") \
                .select("*") \
                .eq("alert_id", alert_id) \
                .single() \
                .execute()
            
            return response.data
        
        except Exception as e:
            print(f"⚠️ Alert not found: {alert_id}")
            return None
    
    def update_alert(self, alert_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an alert in Supabase
        
        Args:
            alert_id: Alert ID to update
            updates: Dictionary of fields to update
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            response = self.client.table("verified_alerts") \
                .update(updates) \
                .eq("alert_id", alert_id) \
                .execute()
            
            if response.data:
                print(f"✅ Alert updated: {alert_id}")
                return True
            else:
                return False
        
        except Exception as e:
            print(f"❌ Error updating alert: {e}")
            return False
    
    def delete_alert(self, alert_id: str) -> bool:
        """
        Delete an alert from Supabase
        
        Args:
            alert_id: Alert ID to delete
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            response = self.client.table("verified_alerts") \
                .delete() \
                .eq("alert_id", alert_id) \
                .execute()
            
            print(f"✅ Alert deleted: {alert_id}")
            return True
        
        except Exception as e:
            print(f"❌ Error deleting alert: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about verified alerts
        
        Returns:
            Dictionary with stats
        """
        if not self.connected:
            return {}
        
        try:
            response = self.client.table("verified_alerts").select("*").execute()
            
            alerts = response.data if response.data else []
            
            if not alerts:
                return {
                    "total_alerts": 0,
                    "average_threat_score": 0,
                    "max_threat_score": 0,
                    "weapons_detected": 0
                }
            
            threat_scores = [a.get("threat_score", 0) for a in alerts]
            
            return {
                "total_alerts": len(alerts),
                "average_threat_score": sum(threat_scores) / len(threat_scores),
                "max_threat_score": max(threat_scores),
                "weapons_detected": sum(a.get("weapons_detected", 0) for a in alerts)
            }
        
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {}


# Standalone functions for easy use
def init_supabase(url: str = None, key: str = None) -> SupabaseSync:
    """Initialize Supabase sync instance"""
    return SupabaseSync(url, key)


def push_to_cloud(alert_id: str, sync_instance: SupabaseSync, alert_path: str = "verified_alerts") -> bool:
    """Push alert to cloud"""
    return sync_instance.push_alert(alert_id, alert_path)
