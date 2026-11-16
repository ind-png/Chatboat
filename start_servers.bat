@echo off
cd /d "%~dp0"
echo ==============================================
echo     STARTING CHATBOAT SERVERS (24x7)
echo ==============================================
echo.

pm2 start ecosystem.config.js
pm2 save

echo.
echo ==============================================
echo     SERVER STATUS:
echo ==============================================
pm2 status
echo.
pause

