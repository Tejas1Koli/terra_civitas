# Quick Reference - Authentication System

## Running the App

```bash
cd /Users/tejaskoli/testing yolo1

# Start with authentication
./yolo/bin/python -m streamlit run cctv_app_with_auth.py
```

## First Time Setup

1. **Register** as first user (any username/password)
2. **Login** with your credentials
3. **Error**: "You need admin permissions" - Expected!
4. Create a new admin user:
   ```
   Edit auth.py line 17:
   Change: self.db_path = db_path
   To: self._create_default_admin()
   ```
   OR manually modify the database

5. Login as admin

## Admin Features

### 🎯 Alert Verification (MAIN FEATURE)
When crime detected during Live Webcam:
- A box appears: "🚨 CRIME DETECTED - Verify to save alert"
- 3 buttons:
  - ✅ **Verify & Save** → Saves image + metadata + admin username
  - ⏭️ **Skip** → Continues detection
  - ❌ **False Alarm** → Marks as false alarm

### 👥 User Management
- View all users
- Create new users
- Change roles: normal ↔ admin
- See last login times

### ✅ Verify Alerts
- Batch review of pending alerts
- See alert images and metadata
- Filter: All / Verified / Pending
- Verify or reject with one click

### 📊 Video Upload & Analysis
- Upload videos for analysis
- Generate threat reports
- Export statistics

### 📈 Analytics Dashboard
- View all verified alerts
- Statistics and charts
- Search and filter

## Normal User Features

### 📹 Live Webcam (Read-Only)
- Detection runs automatically
- Shows: "⏳ Alert pending admin verification"
- Cannot verify or save

### 📊 Video Analysis (Available)
- Upload and analyze videos
- Same features as admins

### 📈 Analytics Dashboard (Verified Only)
- View only verified alerts
- Cannot see pending alerts

### ❌ Disabled Features
- Cannot access User Management
- Cannot verify alerts
- Cannot see unverified alerts

## Database

### auth.db (SQLite)
- Auto-created on first run
- Two tables: `users`, `verified_alerts`
- Located: `/Users/tejaskoli/testing yolo1/auth.db`

### Users Table
```
| username | password_hash | user_type | created_at | last_login |
```

### Verified Alerts Table
```
| alert_filename | alert_type | verified_by | verified_at | is_verified |
```

## File Structure

```
testing yolo1/
├── auth.py                        ← Authentication module (NEW)
├── cctv_app_with_auth.py         ← Main app with auth (NEW)
├── cctv_app_analytics.py         ← Old app (still works)
├── cctv_detector.py              ← Detection engine
├── alert_logger.py               ← Alert logging
├── auth.db                        ← Database (auto-created)
├── AUTH_SETUP.md                 ← Full setup guide
└── AUTH_IMPLEMENTATION_SUMMARY.md ← This file
```

## Key Changes from Original App

### What's Different in cctv_app_with_auth.py?

1. **Login Page** - Before accessing app
2. **Sidebar** - Shows username and logout button
3. **Admin-Only Tabs** - "User Management" and "Verify Alerts"
4. **Verification Workflow** - When crime detected
5. **Role-Based Access** - Different features for admin/normal
6. **Database Tracking** - Verified alerts linked to users

### What's the Same?

- Detection engine (unchanged)
- Alert logging (unchanged)
- Video analysis (unchanged)
- Dashboard (works, but respects user roles)

## Code Examples

### Check if User is Admin
```python
from auth import AuthManager
auth = AuthManager()
if auth.is_admin():
    st.write("Admin features")
```

### Verify an Alert
```python
auth_manager.db.verify_alert(
    alert_filename="CRIME_20251110_120000_000",
    verified_by="admin_username",
    is_verified=1
)
```

### Get Verified Alerts
```python
alerts = auth_manager.db.get_verified_alerts()
for alert in alerts:
    print(f"{alert[0]} verified by {alert[1]}")
```

## Testing

### Create Test Users
```sql
sqlite3 auth.db
INSERT INTO users VALUES (1, 'admin', 'hash', 'admin', datetime(), NULL);
INSERT INTO users VALUES (2, 'user1', 'hash', 'normal', datetime(), NULL);
.exit
```

### View Database
```bash
cd /Users/tejaskoli/testing yolo1
sqlite3 auth.db
.tables
SELECT * FROM users;
SELECT * FROM verified_alerts;
.exit
```

## Troubleshooting

**Q: "Invalid username or password"**
A: Make sure you're using correct credentials

**Q: "You need admin permissions"**
A: User is not admin. Use another admin to change role, or recreate database

**Q: Database locked**
A: Close all Streamlit sessions and try again

**Q: Can't find auth.db**
A: Run app once to auto-create. It should be in the working directory

## Next Steps

1. ✅ Run the app: `./yolo/bin/python -m streamlit run cctv_app_with_auth.py`
2. ✅ Register first user
3. ✅ Make that user admin
4. ✅ Test alert verification workflow
5. ✅ Create normal user for testing
6. ✅ Test role-based access

## Support

For issues or questions:
1. Check `AUTH_SETUP.md` for detailed documentation
2. Check `AUTH_IMPLEMENTATION_SUMMARY.md` for architecture
3. Review `auth.py` for code implementation
4. Check logs in terminal output
