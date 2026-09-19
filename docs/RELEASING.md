# Release guide

## 1. Update version

Update `APP_VERSION` in `Nova_AI_Media_Player.py`, `VERSION`, the Inno Setup version fields, and `CHANGELOG.md` when preparing a new release.

Use a matching Git tag such as `v1.0.0`.

## 2. Test locally

```bat
python -m compileall Nova_AI_Media_Player.py
build_windows.bat
```

Launch the resulting EXE and exercise playback, subtitles, AI, themes, library, session recovery, and mini-player workflows.

## 3. Build installer

```bat
build_inno.bat
```

## 4. Publish GitHub release

Create a GitHub Release for the tag and attach the generated installer EXE. Do not commit `dist/`, `build/`, or local model/media data to the source repository.

## 5. Third-party review

Before redistributing a bundled build, review the exact licenses/notices for the third-party binaries actually included in the release.
