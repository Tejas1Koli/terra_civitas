"""
Authentication Manager - Handles user login, registration, and role management
Uses SQLite for local database storage
"""

import sqlite3
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict

class AuthManager:
    def __init__(self, db_path: str = "users.db"):
        """Initialize authentication manager with SQLite database."""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with users table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'normal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Create verified alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verified_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE NOT NULL,
                verified_by TEXT NOT NULL,
                verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_valid INTEGER DEFAULT 1
            )
        ''')
        
        # Seed default admin if no users exist
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute(
                'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                ('admin', self._hash_password('admin123'), 'admin')
            )

        conn.commit()
        conn.close()
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, password: str, role: str = "normal") -> Tuple[bool, str]:
        """
        Register a new user.
        
        Args:
            username: Username
            password: Password
            role: User role - 'admin' or 'normal'
        
        Returns:
            Tuple of (success, message)
        """
        if role not in ["admin", "normal"]:
            return False, "Invalid role. Must be 'admin' or 'normal'"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self._hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            ''', (username, password_hash, role))
            
            conn.commit()
            conn.close()
            return True, f"User '{username}' registered successfully as {role}"
        
        except sqlite3.IntegrityError:
            return False, f"Username '{username}' already exists"
        except Exception as e:
            return False, f"Registration error: {str(e)}"
    
    def login(self, username: str, password: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Authenticate user login.
        
        Args:
            username: Username
            password: Password
        
        Returns:
            Tuple of (success, username, role)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self._hash_password(password)
            cursor.execute('''
                SELECT username, role FROM users 
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            result = cursor.fetchone()
            
            if result:
                username, role = result
                # Update last login
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP 
                    WHERE username = ?
                ''', (username,))
                conn.commit()
                conn.close()
                return True, username, role
            
            conn.close()
            return False, None, None
        
        except Exception as e:
            return False, None, None
    
    def verify_alert(self, alert_id: str, verified_by: str, is_valid: int = 1) -> Tuple[bool, str]:
        """
        Verify an alert (admin only).
        
        Args:
            alert_id: Alert ID to verify
            verified_by: Username of admin verifying
            is_valid: 1 for valid alert, 0 for false alarm
        
        Returns:
            Tuple of (success, message)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO verified_alerts (alert_id, verified_by, is_valid)
                VALUES (?, ?, ?)
            ''', (alert_id, verified_by, is_valid))
            
            conn.commit()
            conn.close()
            return True, f"Alert {alert_id} verified"
        
        except sqlite3.IntegrityError:
            return False, f"Alert {alert_id} already verified"
        except Exception as e:
            return False, f"Verification error: {str(e)}"
    
    def is_alert_verified(self, alert_id: str) -> bool:
        """Check if alert has been verified by admin."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id FROM verified_alerts WHERE alert_id = ? AND is_valid = 1
            ''', (alert_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
        
        except Exception:
            return False
    
    def get_all_users(self) -> list:
        """Get all registered users (admin only)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT username, role, created_at, last_login FROM users')
            users = cursor.fetchall()
            conn.close()
            
            return users
        except Exception:
            return []
    
    def delete_user(self, username: str) -> Tuple[bool, str]:
        """Delete a user (admin only)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM users WHERE username = ?', (username,))
            conn.commit()
            conn.close()
            
            if cursor.rowcount > 0:
                return True, f"User '{username}' deleted"
            else:
                return False, f"User '{username}' not found"
        
        except Exception as e:
            return False, f"Error deleting user: {str(e)}"
