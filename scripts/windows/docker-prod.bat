@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0docker-prod.ps1"
exit /b %errorlevel%
