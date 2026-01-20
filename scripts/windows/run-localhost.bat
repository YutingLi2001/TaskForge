@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-localhost.ps1"
exit /b %errorlevel%
