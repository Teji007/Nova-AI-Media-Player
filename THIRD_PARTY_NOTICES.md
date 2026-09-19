# Third-Party Notices

This repository contains Nova-authored application code plus dependencies obtained from the Python ecosystem. The following is a practical summary, not a replacement for the license files and notices shipped by each upstream project.

| Component | Role | License / notes | Upstream |
|---|---|---|---|
| PySide6 / Qt for Python | GUI, multimedia, networking | PySide6 is available under LGPLv3, GPLv2, GPLv3, or commercial licensing; use the terms applicable to the Qt/PySide6 distribution you ship. | https://doc.qt.io/qtforpython/ |
| faster-whisper | Speech-to-text | MIT | https://github.com/SYSTRAN/faster-whisper |
| CTranslate2 | Whisper inference backend | MIT | https://github.com/OpenNMT/CTranslate2 |
| pysubs2 | Subtitle parsing/editing | MIT | https://github.com/tkarabela/pysubs2 |
| FFmpeg / FFprobe | Media inspection/conversion where installed | Most FFmpeg files are LGPL 2.1+; optional components can be GPL. Exact build configuration matters. | https://ffmpeg.org/legal.html |

## Important redistribution note

The source repository does not include a full FFmpeg distribution by default. If you bundle FFmpeg or other third-party binaries in a public release, keep the corresponding upstream notices/license texts and verify the exact license obligations for those binaries.

Similarly, Python wheels bring transitive dependencies such as PyAV and other packages. Inspect the installed environment used for a release when producing a full third-party software bill of materials.
