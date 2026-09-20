@echo off
chcp 65001 >nul
echo =================================================================
echo        SMMM STOK SAYIM VE ENVANTER SİSTEMİ BAŞLATICI
echo =================================================================
echo.
echo Sunucu hazırlanıyor ve başlatılıyor...
echo Port: 8088
echo.
start "" http://localhost:8088
python server.py
pause
