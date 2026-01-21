@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-localhost-reset.ps1"
exit /b %errorlevel%
