@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0typecheck.ps1"
exit /b %errorlevel%
