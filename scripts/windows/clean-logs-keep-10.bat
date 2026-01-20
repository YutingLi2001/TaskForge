@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0clean-logs-keep-10.ps1"
exit /b %errorlevel%
