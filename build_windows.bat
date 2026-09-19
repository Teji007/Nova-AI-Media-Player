@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo NOVA AI MEDIA PLAYER - WINDOWS BUILD
echo ============================================================

echo [1/4] Updating build tools...
python -m pip install --upgrade pip
if errorlevel 1 exit /b 1

python -m pip install -r requirements-dev.txt
if errorlevel 1 exit /b 1

echo [2/4] Cleaning previous PyInstaller output...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

 echo [3/4] Building Nova V01 with PyInstaller...
python -m PyInstaller --noconfirm --clean --onedir --windowed ^
 --name "Nova AI Media Player" ^
 --icon "nova_icon.ico" ^
 --add-data "nova_icon.ico;." ^
 --collect-all faster_whisper ^
 --collect-all ctranslate2 ^
 --collect-all pysubs2 ^
 "Nova_AI_Media_Player.py"
if errorlevel 1 exit /b 1

echo [4/4] Build complete.
echo Output: dist\Nova AI Media Player\Nova AI Media Player.exe
endlocal
