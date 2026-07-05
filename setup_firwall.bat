@echo off
REM ========================================
REM ?? ????? ???? ??????? ?????  hr
REM Windows Server - ?????? 5000
REM ????? ????? - ???? ?????
REM ========================================

title HR ERP - Professional Firewall Setup


REM ?????? ?? ??????? ??????
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [?] Running with administrator privileges...
) else (
    echo [?] ERROR: Administrator privileges required!
    echo.
    echo Please right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [??] Configuring Windows Firewall for Port 5000...
echo ========================================

REM ????? ??????? ??????? ??? ???? ??????
echo [??] Removing old firewall rules...
netsh advfirewall firewall delete rule name="HR" >nul 2>&1
netsh advfirewall firewall delete rule name="HR Port 5000" >nul 2>&1
netsh advfirewall firewall delete rule name="HR ERP (Port 5000-IN)" >nul 2>&1
netsh advfirewall firewall delete rule name="HR ERP (Port 5000-OUT)" >nul 2>&1
netsh advfirewall firewall delete rule name="HR ERP (Network Access)" >nul 2>&1
netsh advfirewall firewall delete rule name="Python for HR (Port 5000)" >nul 2>&1

echo [?] Old rules removed

REM ????? ????? ???? ??????? ???????
echo [??] Adding comprehensive firewall rules...

REM ????? ?????? ????????
netsh advfirewall firewall add rule name="HR ERP (Port 5000-IN)" dir=in action=allow protocol=TCP localport=5000 profile=any enable=yes
if %errorLevel% == 0 (
    echo [?] Inbound rule added successfully
) else (
    echo [?] Failed to add inbound rule
)

REM ????? ?????? ????????
netsh advfirewall firewall add rule name="HR ERP (Port 5000-OUT)" dir=out action=allow protocol=TCP localport=5000 profile=any enable=yes
if %errorLevel% == 0 (
    echo [?] Outbound rule added successfully
) else (
    echo [?] Failed to add outbound rule
)

REM ????? ?????? ?? ?????? ???????
netsh advfirewall firewall add rule name="HR ERP (LAN Access)" dir=in action=allow protocol=TCP localport=5000 remoteip=localsubnet profile=private,domain enable=yes
if %errorLevel% == 0 (
    echo [?] LAN access rule added successfully
) else (
    echo [?] Failed to add LAN access rule
)

REM ????? ?????? ????? (????????)
netsh advfirewall firewall add rule name="HR ERP (Public Access)" dir=in action=allow protocol=TCP localport=5000 profile=public enable=yes
if %errorLevel% == 0 (
    echo [?] Public access rule added successfully
) else (
    echo [??] Public access rule failed (this is optional)
)

REM ?????? ??????? Python
echo [??] Adding Python application to firewall exceptions...
for %%i in (python.exe pythonw.exe) do (
    netsh advfirewall firewall add rule name="Python for HR (%%i)" dir=in action=allow program="%%i" profile=any enable=yes >nul 2>&1
    netsh advfirewall firewall add rule name="Python for HR (%%i)" dir=out action=allow program="%%i" profile=any enable=yes >nul 2>&1
)

REM ????? ????? ??????? ???????? (???????? ????????)
echo [??] Adding future-ready rules...
netsh advfirewall firewall add rule name="HR ERP (HTTP-80)" dir=in action=allow protocol=TCP localport=80 profile=any enable=no >nul 2>&1
netsh advfirewall firewall add rule name="HR ERP (HTTPS-443)" dir=in action=allow protocol=TCP localport=443 profile=any enable=no >nul 2>&1

echo.
echo [??] Testing firewall configuration...
netsh advfirewall firewall show rule name="HR ERP (Port 5000-IN)" >nul 2>&1
if %errorLevel% == 0 (
    echo [?] Firewall rules are active and working
) else (
    echo [??] Warning: Could not verify firewall rules
)

REM ??? ??????? ??????
echo.
echo [??] Network Information:
echo ========================================
echo Your server IP addresses:
ipconfig | findstr /C:"IPv4 Address" | findstr /V "127.0.0.1"

echo.
echo ========================================
echo [??] Firewall configuration completed!
echo ========================================
echo.
echo ?? Firewall Status:
echo   ? Port 5000: Open for HR ERP
echo   ? Inbound connections: Allowed
echo   ? Outbound connections: Allowed
echo   ? LAN access: Enabled
echo   ? Public access: Enabled
echo   ? Python applications: Allowed
echo   ? Future ports: Prepared (disabled)
echo.
echo ?? Access URLs:
echo   - Local: http://localhost:5000
echo   - LAN: http://[YOUR-LAN-IP]:5000
echo   - Network: http://[YOUR-SERVER-IP]:5000
echo.
echo ??? Security Profiles:
echo   - Domain profile: ? Enabled
echo   - Private profile: ? Enabled  
echo   - Public profile: ? Enabled
echo.
echo ?? Next Steps:
echo   1. Run install_service.bat to install the service
echo   2. Access the ERP at http://localhost:5000
echo   3. Login with admin/admin123
echo   4. Change the default password immediately
echo   5. Test network access from other devices
echo.
echo ?? Management Commands:
echo   - View rules: netsh advfirewall firewall show rule name=all
echo   - Disable rule: netsh advfirewall firewall set rule name="RULE_NAME" new enable=no
echo   - Enable rule: netsh advfirewall firewall set rule name="RULE_NAME" new enable=yes
echo ========================================

echo.
pause
