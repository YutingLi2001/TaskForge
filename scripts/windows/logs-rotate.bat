@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0logs-rotate.ps1"
exit /b %errorlevel%
