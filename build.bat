@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

set "DO_ZIP=0"
if /i "%~1"=="release" set "DO_ZIP=1"

echo ========================================
echo   LineageBossVisualization Build
echo ========================================
echo.

echo [1/3] Cleaning old dist (antivirus may delay file release)...
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist\*.zip" del /q "dist\*.zip" 2>nul
call :clean_dist
if errorlevel 1 (
    echo.
    echo ERROR: Cannot delete dist\LineageBossVisualization after retries.
    echo   Close any Explorer window showing dist\, wait for antivirus scan,
    echo   or reboot if persistent. Then rerun build.bat.
    pause
    exit /b 1
)

echo [2/3] Running PyInstaller...
echo.
call pipenv run python -m PyInstaller --noconfirm LineageBossVisualization.spec
if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)

if "!DO_ZIP!"=="1" (
    echo.
    echo [3/3] Creating release zip...
    for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd"') do set "BUILD_DATE=%%i"
    set "ZIP_NAME=LineageBossVisualization-!BUILD_DATE!.zip"
    pushd dist
    tar -a -c -f "!ZIP_NAME!" LineageBossVisualization
    set "TAR_RC=!errorlevel!"
    popd
    if not "!TAR_RC!"=="0" (
        echo ERROR: zip failed.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   Build complete
echo ========================================
echo.
echo EXE: dist\LineageBossVisualization\LineageBossVisualization.exe
if "!DO_ZIP!"=="1" (
    echo ZIP: dist\!ZIP_NAME!
) else (
    echo Tip: run "build.bat release" to also generate a release zip.
)
echo.
if not "%~2"=="nopause" pause
exit /b 0

:clean_dist
set "RETRIES=0"
:clean_loop
if not exist "dist\LineageBossVisualization" exit /b 0
rmdir /s /q "dist\LineageBossVisualization" 2>nul
if not exist "dist\LineageBossVisualization" exit /b 0
set /a RETRIES+=1
if !RETRIES! geq 10 exit /b 1
echo   ... retry !RETRIES!/10 (waiting 3s for file handles to release)
ping -n 4 127.0.0.1 >nul
goto :clean_loop
