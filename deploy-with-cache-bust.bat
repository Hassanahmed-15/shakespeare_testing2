@echo off
echo 🔄 Deploying with cache-busting...

REM Add timestamp to force cache refresh
echo %date% %time% > deploy-timestamp.txt

REM Commit all changes
git add .
git commit -m "Deploy with macbeth_notes_integration_play.json and cache-busting - %date% %time%"

REM Push to trigger deployment
git push origin main

echo ✅ Deployment triggered with cache-busting!
echo 🌐 Your changes should appear within 2-3 minutes
echo 💡 If changes still don't appear, try hard refresh (Ctrl+F5) in your browser
