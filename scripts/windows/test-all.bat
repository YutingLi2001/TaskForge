@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0test-all.ps1"
exit /b %errorlevel%
