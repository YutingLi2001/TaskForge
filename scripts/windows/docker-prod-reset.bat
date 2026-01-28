@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0docker-prod-reset.ps1"
exit /b %errorlevel%
