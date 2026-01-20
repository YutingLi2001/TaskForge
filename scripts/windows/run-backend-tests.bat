@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-backend-tests.ps1"
exit /b %errorlevel%
