@echo off
REM MySQL 8.4 Fix - Run as Administrator
REM Using batch file for more reliable admin execution

echo === Stopping MySQL ===
net stop MySQL84
timeout /t 3 /nobreak >nul

echo === Taking ownership of data dir ===
takeown /F "C:\ProgramData\MySQL\MySQL Server 8.4\Data" /R /D Y >nul 2>&1
icacls "C:\ProgramData\MySQL\MySQL Server 8.4\Data" /grant Administrators:F /T >nul 2>&1

echo === Removing data directory ===
rmdir /s /q "C:\ProgramData\MySQL\MySQL Server 8.4\Data"
timeout /t 2 /nobreak >nul

if exist "C:\ProgramData\MySQL\MySQL Server 8.4\Data" (
    echo ERROR: Data dir still exists!
    echo Trying alternate...
    rd /s /q "C:\ProgramData\MySQL\MySQL Server 8.4\Data"
    timeout /t 2 /nobreak >nul
)

if not exist "C:\ProgramData\MySQL\MySQL Server 8.4\Data" (
    echo Data directory removed successfully!
) else (
    echo FAILED to remove data directory.
    pause
    exit /b 1
)

echo === Reinitializing MySQL ===
"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqld.exe" --defaults-file="C:\ProgramData\MySQL\MySQL Server 8.4\my.ini" --initialize-insecure --console
timeout /t 3 /nobreak >nul

echo === Starting MySQL ===
net start MySQL84
timeout /t 5 /nobreak >nul

echo === Setting root password ===
"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -u root --skip-password -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;"

echo === Final test ===
"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -u root -proot -e "SELECT 'CONNECTION SUCCESSFUL!' AS result; SELECT user, host, plugin FROM mysql.user WHERE user='root';"

if %ERRORLEVEL% == 0 (
    echo.
    echo *** SUCCESS! MySQL is working! ***
    echo Username: root ^| Password: root
) else (
    echo.
    echo *** Check errors above ***
)

pause
