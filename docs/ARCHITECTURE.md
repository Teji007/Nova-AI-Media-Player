# Architecture notes

Nova V01 is intentionally delivered as a single Python application file. The source currently groups the application into visual/theme definitions, utilities, worker classes, dialogs, the main player window, and V01 workspace/productivity features.

This structure keeps the first public release simple to build. Future maintenance can split the code into modules without changing the user-facing behavior.

## Major areas

- Qt/PySide6 application shell and Windows single-instance handling
- QMediaPlayer/QAudioOutput/QVideoWidget playback stack
- Local faster-whisper worker and CUDA runtime preparation
- Subtitle/transcript processing
- Library, playlist, history and session state
- Theme/layout system
- AI/workspace dialogs
- PyInstaller + Inno Setup Windows packaging
