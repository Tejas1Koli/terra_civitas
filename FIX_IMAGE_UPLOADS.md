# 🔐 Fix: Enable Image Uploads to Supabase Storage

You have a Row Level Security policy blocking uploads. Easy fix!

## Issue
```
❌ Upload failed: new row violates row-level security policy
```

## Solution

Go to **Supabase Dashboard → Storage → alert-images bucket → Policies**

### Option 1: Allow Public Uploads (Simple)
1. Click **New policy**
2. Select **Authenticated users can upload** (or just Allow)
3. Set it to:
   - **Operation**: INSERT
   - **Target Role**: authenticated, anon
   - **Allowed**: YES

### Option 2: Via SQL (Recommended)
Go to **SQL Editor** and run:

```sql
-- Allow public uploads to alert-images bucket
CREATE POLICY "Allow public uploads" ON storage.objects
FOR INSERT
WITH CHECK (
  bucket_id = 'alert-images' AND
  (auth.role() = 'authenticated' OR auth.role() = 'anon')
);

-- Allow public reads
CREATE POLICY "Allow public reads" ON storage.objects
FOR SELECT
USING (bucket_id = 'alert-images');
```

## After Fixing:

Images will automatically upload when you verify alerts! ☁️

Run:
```bash
python upload_test_image.py
```

Should show:
```
✅ Upload successful!
✅ Public URL: https://...
```

---

Then verified alerts will have:
- ✅ Metadata in cloud database
- ✅ Images in cloud storage
- ✅ Public URLs ready for React frontend
