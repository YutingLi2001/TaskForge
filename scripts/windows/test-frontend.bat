@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0test-frontend.ps1"
exit /b %errorlevel%
