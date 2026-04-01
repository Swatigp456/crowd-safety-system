@echo off
echo ========================================
echo   Uploading to GitHub...
echo ========================================
echo.
echo Current folder: %cd%
echo.
echo Step 1: Initializing git...
git init
echo.
echo Step 2: Adding all files...
git add .
echo.
echo Step 3: Committing files...
git commit -m "Initial upload of Crowd Safety System"
echo.
echo Step 4: Adding remote repository...
git remote add origin https://github.com/swatigp456/crowd-safety-system.git
echo.
echo Step 5: Pushing to GitHub...
git push -u origin main
echo.
echo ========================================
echo   Done! Check your GitHub repository
echo ========================================
pause