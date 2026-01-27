@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-localhost-prod-reset.ps1"
exit /b %errorlevel%
