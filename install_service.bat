@echo off
setlocal enabledelayedexpansion

REM تثبيت المكتبات المطلوبة
echo ===================================================
echo Installing required libraries...
echo ===================================================

REM الانتقال إلى مجلد السكربت
cd /d "%~dp0"

REM إنشاء مجلد السجلات إذا لم يكن موجوداً
if not exist "%~dp0logs" mkdir "%~dp0logs"



REM إزالة الخدمة القديمة إذا كانت موجودة
echo.
echo ===================================================
echo Removing old service if exists...
echo ===================================================
python "service_runner.py" remove
timeout /t 2

REM تثبيت الخدمة
echo.
echo ===================================================
echo Installing the service...
echo ===================================================
python "service_runner.py" install
python "service_runner.py" start

REM ضبط الإعدادات الافتراضية للخدمة
echo.
echo ===================================================
echo Setting service to start automatically...
echo ===================================================
sc config HR start= auto

REM تشغيل الخدمة
echo.
echo ===================================================
echo Starting the service...
echo ===================================================
net start HR

REM التحقق من حالة الخدمة
sc query HR | findstr "RUNNING" >nul
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================================
    echo SUCCESS: Service is running!
    echo ===================================================
    echo.
    echo You can access the website at:
    echo http://localhost:5000-
    echo.
) else (
    echo.
    echo ===================================================
    echo WARNING: Service may not have started correctly.
    echo Please check the logs in the logs directory.
    echo ===================================================
    echo.
)

echo ===================================================
echo Service installation complete!
echo ===================================================
echo The website will now run automatically:
echo - After logout
echo - After restart
echo - After power failure
echo.
echo You can manage the service in Windows Services (services.msc)
echo.
echo To uninstall the service, run: python service_runner.py remove
echo.
pause