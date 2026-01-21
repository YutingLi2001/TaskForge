@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-frontend-tests.ps1"
exit /b %errorlevel%
