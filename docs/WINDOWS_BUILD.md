# Windows build guide

## Prerequisites

- Windows 10/11 x64
- Python 3.10+
- PyInstaller
- FFmpeg/FFprobe in PATH or next to the application if you want those tools available locally
- Inno Setup 7 if you want to build the installer

## PyInstaller

From the repository root:

```bat
build_windows.bat
```

This builds a one-folder application under `dist\Nova AI Media Player\` and includes the Nova icon as runtime data.

## Manual PyInstaller command

```bat
python -m PyInstaller --noconfirm --clean --onedir --windowed --name "Nova AI Media Player" --icon "nova_icon.ico" --add-data "nova_icon.ico;." --collect-all faster_whisper --collect-all ctranslate2 --collect-all pysubs2 "Nova_AI_Media_Player.py"
```

## Inno Setup

Once the PyInstaller folder exists:

```bat
build_inno.bat
```

The installer script is `Nova_AI_Media_Player_V01.iss`.
