@echo off
echo.
echo ===================================
echo  Publishing Risk App to GitHub
echo ===================================
echo.
echo Step 1: Make sure you've created the repository on GitHub:
echo   - Go to: https://github.com/nonamephysics
echo   - Click "New" to create a new repository
echo   - Name: risk-management-app
echo   - Description: Full-stack document management system with CSV/XLSX upload, unique tagging, non-ASCII validation, user tracking, and authentication. Built with FastAPI, React, and MongoDB.
echo   - Set to PUBLIC
echo   - DO NOT initialize with README, .gitignore, or license
echo.
echo Step 2: After creating the repository, press any key to push the code...
pause
echo.
echo Pushing code to GitHub...
git push -u origin main
echo.
if %errorlevel% equ 0 (
    echo ✅ Success! Your Risk Management App is now published at:
    echo    https://github.com/nonamephysics/risk-management-app
    echo.
    echo Don't forget to:
    echo - Add topics/tags: fastapi, react, mongodb, docker, document-management
    echo - Star your own repository ⭐
    echo - Share it with others!
) else (
    echo ❌ Push failed. Please ensure:
    echo - Repository exists on GitHub
    echo - You have push permissions
    echo - Internet connection is working
)
echo.
pause