@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

set "APP_NAME=LineageBossVisualization"
set "BIN_NAME=lineage_boss_visualization.exe"
set "OUT_DIR=dist\%APP_NAME%"
set "DO_ZIP=0"
if /i "%~1"=="release" set "DO_ZIP=1"

echo ========================================
echo   %APP_NAME% Rust Build
echo ========================================
echo.

echo [1/4] Cleaning old dist...
if exist "%OUT_DIR%" rmdir /s /q "%OUT_DIR%" 2>nul
if exist "dist\*.zip" del /q "dist\*.zip" 2>nul
mkdir "%OUT_DIR%"
if errorlevel 1 (
    echo ERROR: Cannot create %OUT_DIR%.
    pause
    exit /b 1
)

echo [2/4] Running cargo build --release...
cargo build --release
if errorlevel 1 (
    echo.
    echo ERROR: Cargo build failed.
    pause
    exit /b 1
)

echo [3/4] Copying executable and resources...
copy /y "target\release\%BIN_NAME%" "%OUT_DIR%\%APP_NAME%.exe" >nul
if errorlevel 1 (
    echo ERROR: Cannot copy release executable.
    pause
    exit /b 1
)

if exist "pubilc" (
    xcopy /e /i /y "pubilc" "%OUT_DIR%\pubilc" >nul
) else if exist "public" (
    xcopy /e /i /y "public" "%OUT_DIR%\public" >nul
) else (
    echo WARNING: No pubilc or public resource folder found.
)

if "!DO_ZIP!"=="1" (
    echo [4/4] Creating release zip...
    for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd"') do set "BUILD_DATE=%%i"
    set "ZIP_NAME=%APP_NAME%-!BUILD_DATE!.zip"
    pushd dist
    tar -a -c -f "!ZIP_NAME!" "%APP_NAME%"
    set "TAR_RC=!errorlevel!"
    popd
    if not "!TAR_RC!"=="0" (
        echo ERROR: zip failed.
        pause
        exit /b 1
    )
) else (
    echo [4/4] Skipping zip. Run "build.bat release" to create one.
)

echo.
echo ========================================
echo   Build complete
echo ========================================
echo.
echo EXE: %OUT_DIR%\%APP_NAME%.exe
if "!DO_ZIP!"=="1" echo ZIP: dist\!ZIP_NAME!
echo.
if not "%~2"=="nopause" pause
