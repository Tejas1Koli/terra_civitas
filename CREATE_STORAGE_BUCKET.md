# 🔐 Create Storage Bucket in Supabase

Your database is connected! Now create the storage bucket to store alert images.

## Step 1: Go to Supabase Dashboard

1. Visit: https://app.supabase.com
2. Select your project
3. Click **"Storage"** in the left menu

## Step 2: Create Bucket

1. Click **"New Bucket"** button
2. Fill in:
   - **Bucket name**: `alert-images` (exactly this)
   - **Make it public**: Toggle ON ✅
3. Click **"Create Bucket"**

## Step 3: Verify

Once created, you'll see:
```
📁 alert-images (public)
```

---

## Why This Matters

When an admin verifies an alert:
1. ✅ Metadata saved to database
2. ✅ Image **uploaded to storage bucket** ← This is what we just created
3. ✅ Public URL generated so React can display images

---

## Done!

Your Supabase is now fully configured. Run:

```bash
./start.sh
```

When you verify an alert, it will automatically:
- Save metadata to `verified_alerts` table
- Upload image to `alert-images` bucket
- Be accessible from React frontend

Verified alerts syncing to cloud ☁️ ✅
