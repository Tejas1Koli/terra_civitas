#!/bin/bash
# Quick Start Checklist for Cloud Integration
# Run this to guide you through the setup

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  🚀 CCTV Cloud Integration - Quick Start Checklist     ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check 1: Supabase Account
echo "📋 Step 1: Supabase Account"
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
    SUPABASE_URL=$(grep "SUPABASE_URL" .env | cut -d'=' -f2)
    if [ -z "$SUPABASE_URL" ] || [ "$SUPABASE_URL" = "your_url_here" ]; then
        echo "   ⚠️  SUPABASE_URL not configured"
        echo "   → Follow SUPABASE_SETUP.md and update .env"
    else
        echo "   ✅ SUPABASE_URL configured: ${SUPABASE_URL:0:40}..."
    fi
else
    echo "   ❌ .env file not found"
    echo "   → Copy from .env.example: cp .env.example .env"
    echo "   → Update with your Supabase credentials"
fi
echo ""

# Check 2: Python Dependencies
echo "📦 Step 2: Python Dependencies"
python3 -c "import supabase" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ supabase package installed"
else
    echo "   ❌ supabase package not installed"
    echo "   → Run: pip install supabase"
fi

python3 -c "import dotenv" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ python-dotenv package installed"
else
    echo "   ❌ python-dotenv package not installed"
    echo "   → Run: pip install python-dotenv"
fi
echo ""

# Check 3: Alert Directories
echo "📁 Step 3: Alert Directories"
for dir in "alerts" "alerts/images" "alerts/metadata" "verified_alerts" "verified_alerts/images" "verified_alerts/metadata"; do
    if [ -d "$dir" ]; then
        echo "   ✅ $dir"
    else
        echo "   ❌ $dir (will be created when alerts detected)"
    fi
done
echo ""

# Check 4: Configuration Files
echo "⚙️  Step 4: Configuration Files"
files=("supabase_sync.py" "cctv_app_admin.py" "verify_setup.py")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (missing!)"
    fi
done
echo ""

# Check 5: Documentation
echo "📚 Step 5: Documentation"
docs=("SUPABASE_SETUP.md" "REACT_FRONTEND_GUIDE.md" "CLOUD_INTEGRATION_README.md" ".env.example")
for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "   ✅ $doc"
    else
        echo "   ⚠️  $doc (missing)"
    fi
done
echo ""

# Summary
echo "════════════════════════════════════════════════════════"
echo ""
echo "🎯 NEXT STEPS:"
echo ""
echo "1️⃣  Setup Supabase (5 minutes)"
echo "   → Go to https://supabase.com"
echo "   → Create account and project"
echo "   → Follow SUPABASE_SETUP.md"
echo ""
echo "2️⃣  Configure Environment"
echo "   → Copy .env.example to .env"
echo "   → Add your Supabase credentials"
echo ""
echo "3️⃣  Verify Setup"
echo "   → Run: python verify_setup.py"
echo ""
echo "4️⃣  Start Application"
echo "   → Run: ./start.sh"
echo ""
echo "5️⃣  Test Cloud Sync"
echo "   → Detect crime"
echo "   → Verify alert"
echo "   → Check Supabase dashboard"
echo ""
echo "6️⃣  Build React Frontend"
echo "   → Follow REACT_FRONTEND_GUIDE.md"
echo ""
echo "════════════════════════════════════════════════════════"
echo ""
echo "📖 Read these files for detailed instructions:"
echo "   - SUPABASE_SETUP.md: Step-by-step cloud setup"
echo "   - SETUP_COMPLETE.md: Full overview"
echo "   - REACT_FRONTEND_GUIDE.md: React integration"
echo ""
echo "🎉 Once configured, your alerts will auto-sync to cloud!"
echo ""
