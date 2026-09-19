@echo off
setlocal
cd /d "%~dp0"

set "ISCC=%ProgramFiles%\Inno Setup 7\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe"

if not exist "%ISCC%" (
  echo Inno Setup 7 ISCC.exe was not found.
  echo Install Inno Setup 7 and run this script again.
  exit /b 1
)

if not exist "dist\Nova AI Media Player\Nova AI Media Player.exe" (
  echo PyInstaller build not found.
  echo Run build_windows.bat first.
  exit /b 1
)

"%ISCC%" "Nova_AI_Media_Player_V01.iss"
if errorlevel 1 exit /b 1

echo Installer build complete.
echo Check the installer folder for Nova_AI_Media_Player_V01_Setup.exe
endlocal
