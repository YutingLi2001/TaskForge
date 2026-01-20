@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0clean-logs.ps1"
exit /b %errorlevel%
