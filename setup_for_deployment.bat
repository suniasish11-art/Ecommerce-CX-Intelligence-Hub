@echo off
REM Setup script for Netlify + Railway deployment

echo.
echo ========================================
echo Navedas CX Dashboard - Deployment Setup
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "ecommerce_cx_hub_v10 (3).html" (
    echo ERROR: HTML file not found!
    echo Make sure you're in the dashboard folder
    pause
    exit /b 1
)

echo Creating deployment folder structure...
echo.

REM Create folders
if not exist "frontend" mkdir frontend
if not exist "backend" mkdir backend

echo.
echo Step 1: Preparing Frontend files...
REM Copy HTML to frontend
if exist "ecommerce_cx_hub_v10 (3).html" (
    copy "ecommerce_cx_hub_v10 (3).html" "frontend\index.html"
    echo   [OK] HTML copied to frontend/index.html
) else (
    echo   [ERROR] HTML file not found
)

echo.
echo Step 2: Preparing Backend files...
REM Copy backend files
if exist "server.py" (
    copy "server.py" "backend\server.py"
    echo   [OK] server.py copied to backend/
)

if exist "navedas_cx_1000 (1).xlsx" (
    copy "navedas_cx_1000 (1).xlsx" "backend\navedas_cx_1000 (1).xlsx"
    echo   [OK] Excel file copied to backend/
)

if exist "requirements.txt" (
    copy "requirements.txt" "backend\requirements.txt"
    echo   [OK] requirements.txt copied to backend/
)

echo.
echo ========================================
echo READY FOR DEPLOYMENT!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. CREATE GITHUB REPOSITORY
echo    - Go to https://github.com/new
echo    - Create repo: navedas-cx-dashboard
echo    - Get clone URL
echo.
echo 2. INITIALIZE GIT (in this folder)
echo    git init
echo    git remote add origin YOUR_GITHUB_URL
echo    git add .
echo    git commit -m "Initial commit"
echo    git push -u origin main
echo.
echo 3. DEPLOY BACKEND
echo    - Go to https://railway.app
echo    - Create new project from GitHub
echo    - Select backend folder
echo    - Note the Railway URL
echo.
echo 4. UPDATE API URL
echo    - Edit frontend/index.html
echo    - Replace: return 'https://your-backend.railway.app';
echo    - With: return 'https://YOUR-RAILWAY-URL.railway.app';
echo.
echo 5. DEPLOY FRONTEND
echo    - Go to https://app.netlify.com
echo    - Connect GitHub repo
echo    - Set publish directory: frontend
echo    - Deploy!
echo.
echo See DEPLOY_YOURSELF.md for detailed instructions
echo.
pause
