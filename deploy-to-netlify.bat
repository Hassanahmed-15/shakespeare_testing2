@echo off
echo ========================================
echo Shakespeare Variorum - Deploy to Netlify
echo ========================================
echo.
echo This script will help you deploy to Netlify
echo.

echo 1. Installing dependencies...
npm install

echo.
echo 2. Adding all changes to git...
git add .

echo.
echo 3. Committing changes...
git commit -m "Fix Shakespeare Variorum API integration and Macbeth notes - Fix HTTP 501 error with proper API redirects - Implement different analysis levels (basic, expert, full fathom five) - Integrate Macbeth notes database into analysis - Fix file system access issues for Netlify deployment"

echo.
echo 4. Pushing to main branch...
git push origin main

echo.
echo ========================================
echo DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Your Shakespeare Variorum is now deployed to Netlify!
echo.
echo IMPORTANT: The functions will only work when deployed to Netlify, not locally.
echo.
echo To test locally, open test-api.html in your browser.
echo To test the full system, visit your Netlify site.
echo.
pause
