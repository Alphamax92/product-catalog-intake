@echo off
title Product Catalog Collector
echo ===================================================
echo   Product Catalog Intake & Drive Sorter
echo   Target: Google Drive (G:\My Drive\Product Catalog)
echo ===================================================
echo.
cd /d "%~dp0"
start "" http://localhost:8765
python server.py
pause
