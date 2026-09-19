# Nova AI Media Player

![Nova AI Media Player](assets/nova_icon.png)

A modern Windows desktop media player built with Python and PySide6, with local AI-assisted subtitle workflows, media tools, playlist/library features, rich interface layouts, and optional online AI functions.

**Version 01 — 1.0.0**  
**Developer:** Tejinder Pal Singh

> This repository is the source project. The generated `dist/`, `build/`, and installer outputs are intentionally not committed.

## Highlights

### Playback
- Audio and video playback through Qt Multimedia
- Playlist queue, previous/next, seek, playback speed, volume and mute
- Fullscreen, cinema mode, frame stepping and A-B repeat
- Drag-and-drop media opening
- Bookmarks, favorites and saved playback position
- Session/crash recovery and a single-instance Windows workflow

### Media Library
- Library/folder scanning
- Recently played and continue-watching views
- Favorites, video/audio and unwatched filters
- Search and sorting by name, recent activity and progress
- Media information and FFmpeg/FFprobe integration

### Subtitles
- External and sidecar subtitles
- Subtitle editor
- Subtitle timing/delay controls
- Subtitle appearance controls
- Transcript viewer and transcript search
- Translation workflows

### AI
- Local transcription with `faster-whisper`
- CPU and CUDA-aware Whisper selection
- AI subtitle generation
- Transcript-driven AI tools
- Nova Intelligence workspace
- Optional online AI through the configured API settings or `NOVA_OPENAI_API_KEY`

### Interface
- Multiple interface themes with different layouts, not just color swaps
- Theme Center
- Mini Player
- Cinema Mode
- Now Playing workspace
- Command Palette
- Task Center / Activity Center

### Media tools
- Screenshot capture
- Video adjustments
- Audio output selection
- Equalizer
- Playlist manager
- Sleep timer
- FFmpeg conversion/export

## Requirements

- Windows 10/11 x64 is the primary target.
- Python 3.10+ is recommended.
- Runtime packages are listed in [`requirements.txt`](requirements.txt).
- Optional NVIDIA/CUDA packages for GPU Whisper are listed in [`requirements-gpu.txt`](requirements-gpu.txt).
- FFmpeg/FFprobe are optional external tools used by the application for certain media operations.

## Install from source

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python Nova_AI_Media_Player.py
```

For NVIDIA/CUDA Whisper support on a compatible Windows machine:

```powershell
python -m pip install -r requirements-gpu.txt
```

## FFmpeg

The application looks for FFmpeg in `PATH` and common local Windows locations. If you want to bundle FFmpeg with a Windows distribution, obtain a compatible build and review its license obligations before redistribution.

## Build a Windows application

Run:

```bat
build_windows.bat
```

The PyInstaller output will be:

```text
dist\Nova AI Media Player\Nova AI Media Player.exe
```

The build script also includes `nova_icon.ico` as application data because the source loads the icon at runtime.

## Build the installer

After the PyInstaller build succeeds and Inno Setup 7 is installed:

```bat
build_inno.bat
```

The Inno Setup script uses LZMA2 high compression and packages the PyInstaller one-folder build into a single installer executable.

## Repository layout

```text
.
├── Nova_AI_Media_Player.py
├── nova_icon.ico
├── assets/
│   └── nova_icon.png
├── requirements.txt
├── requirements-gpu.txt
├── requirements-dev.txt
├── build_windows.bat
├── build_inno.bat
├── Nova_AI_Media_Player_V01.iss
├── VERSION
├── LICENSE
├── NOTICE.md
├── THIRD_PARTY_NOTICES.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── CHANGELOG.md
├── CITATION.cff
├── .gitignore
├── .gitattributes
├── .github/
│   ├── dependabot.yml
│   ├── pull_request_template.md
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
└── docs/
    ├── WINDOWS_BUILD.md
    ├── RELEASING.md
    └── ARCHITECTURE.md
```

## API key and privacy

Never commit API keys, tokens, passwords, local configuration files, media files, Whisper caches, or generated output to the repository. The application can read `NOVA_OPENAI_API_KEY` from the environment for optional online AI workflows. Keep secrets outside source control.

## License

The Nova-authored source in this repository is released under the MIT License. Third-party dependencies remain under their respective licenses; see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Please include reproducible steps for bugs and keep changes focused.

## Security

See [`SECURITY.md`](SECURITY.md) for reporting guidance.

## Credits and upstream projects

- PySide6 / Qt for Python
- faster-whisper
- CTranslate2
- pysubs2
- FFmpeg / FFprobe (when present)

Upstream licensing information is summarized in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
