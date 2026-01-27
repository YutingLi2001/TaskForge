@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0logs-clean.ps1"
exit /b %errorlevel%
