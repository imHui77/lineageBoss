@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

set "APP_NAME=LineageBossVisualization"
set "BIN_NAME=lineage_boss_visualization.exe"
set "OBFUSCATE_BIN=target\release\obfuscate.exe"
set "OUT_DIR=dist\%APP_NAME%"
set "DO_ZIP=0"
if /i "%~1"=="release" set "DO_ZIP=1"

echo ========================================
echo   %APP_NAME% Rust Build
echo ========================================
echo.

echo [1/5] Cleaning old dist...
if exist "%OUT_DIR%" rmdir /s /q "%OUT_DIR%" 2>nul
if exist "dist\*.zip" del /q "dist\*.zip" 2>nul
mkdir "%OUT_DIR%"
if errorlevel 1 (
    echo ERROR: Cannot create %OUT_DIR%.
    pause
    exit /b 1
)

echo [2/5] Running cargo build --release...
where cargo >nul 2>&1
if errorlevel 1 (
    if exist "%USERPROFILE%\.cargo\bin\cargo.exe" (
        set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
    ) else (
        echo ERROR: cargo not found. Install Rust via "winget install Rustlang.Rustup".
        pause
        exit /b 1
    )
)
cargo build --release
if errorlevel 1 (
    echo.
    echo ERROR: Cargo build failed.
    pause
    exit /b 1
)

echo [3/5] Copying executable and resources...
copy /y "target\release\%BIN_NAME%" "%OUT_DIR%\%APP_NAME%.exe" >nul
if errorlevel 1 (
    echo ERROR: Cannot copy release executable.
    pause
    exit /b 1
)

set "RES_NAME="
if exist "pubilc" (
    set "RES_NAME=pubilc"
    xcopy /e /i /y "pubilc" "%OUT_DIR%\pubilc" >nul
) else if exist "public" (
    set "RES_NAME=public"
    xcopy /e /i /y "public" "%OUT_DIR%\public" >nul
) else (
    echo WARNING: No pubilc or public resource folder found.
)

echo [4/5] Obfuscating dist resources...
if defined RES_NAME (
    if exist "%OBFUSCATE_BIN%" (
        "%OBFUSCATE_BIN%" "%OUT_DIR%\!RES_NAME!" --apply
        if errorlevel 1 (
            echo ERROR: Obfuscation failed.
            pause
            exit /b 1
        )
    ) else (
        echo WARNING: %OBFUSCATE_BIN% not found, skipping obfuscation.
    )
) else (
    echo WARNING: No resource folder, skipping obfuscation.
)

if "!DO_ZIP!"=="1" (
    echo [5/5] Creating release zip...
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
    echo [5/5] Skipping zip. Run "build.bat release" to create one.
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
