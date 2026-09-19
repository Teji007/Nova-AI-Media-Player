# ============================================================
# NOVA AI MEDIA PLAYER - V01
# Modern 2026-style Windows UI
#
# Single-file desktop media player
#
# Install:
#   pip install --upgrade PySide6 faster-whisper pysubs2
#
# FFmpeg:
#   ffmpeg -version
#   ffprobe -version
#
# Optional AI:
#   Set NOVA_OPENAI_API_KEY in Windows environment variables.
#
# ============================================================

import sys
import os
import json
import time
import shutil
import subprocess
import traceback
import tempfile
import uuid
import ctypes
import importlib
import site
import urllib.request
import urllib.error
import re

from pathlib import Path
from datetime import datetime
from bisect import bisect_right

from PySide6.QtCore import (
    Qt,
    QUrl,
    QTimer,
    QObject,
    Signal,
    Slot,
    QThread,
    QPoint,
    QSize,
    QRect,
    QEvent,
    QPropertyAnimation,
    QEasingCurve,
)

from PySide6.QtGui import (
    QAction,
    QFont,
    QKeySequence,
    QColor,
    QCursor,
    QIcon,
    QPixmap,
)

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFormLayout,
    QPushButton,
    QLabel,
    QSlider,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QFileDialog,
    QMessageBox,
    QComboBox,
    QLineEdit,
    QTextEdit,
    QDialog,
    QDialogButtonBox,
    QProgressBar,
    QCheckBox,
    QSpinBox,
    QTabWidget,
    QSplitter,
    QMenu,
    QStackedWidget,
    QScrollArea,
    QGroupBox,
    QDoubleSpinBox,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSpinBox,
    QAbstractItemView,
    QInputDialog,
    QGraphicsDropShadowEffect,
)

from PySide6.QtNetwork import QLocalServer, QLocalSocket

from PySide6.QtMultimedia import (
    QMediaPlayer,
    QAudioOutput,
)

from PySide6.QtMultimediaWidgets import (
    QVideoWidget,
)


# ============================================================
# APP
# ============================================================

APP_NAME = "Nova AI Media Player"
APP_VERSION = "1.0.0"
# Replace this with the exact name you want shown in About.
DEVELOPER_NAME = "Tejinder Pal Singh"

# Application icon (keep nova_icon.ico beside this Python file).
ICON_FILE = Path(__file__).resolve().parent / "nova_icon.ico"
APP_DATA = (
    Path.home()
    / ".nova_ai_media_player"
)

APP_DATA.mkdir(
    parents=True,
    exist_ok=True
)

SESSION_FILE = APP_DATA / "session.json"

CONFIG_FILE = APP_DATA / "config.json"
HISTORY_FILE = APP_DATA / "history.json"
PLAYLIST_FILE = APP_DATA / "playlist.json"
BOOKMARK_FILE = APP_DATA / "bookmarks.json"
LIBRARY_FILE = APP_DATA / "library.json"

SCREENSHOT_DIR = APP_DATA / "screenshots"
SUBTITLE_DIR = APP_DATA / "subtitles"

SCREENSHOT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

SUBTITLE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# MEDIA
# ============================================================

MEDIA_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
    ".flv",
    ".webm",
    ".m4v",
    ".mpg",
    ".mpeg",
    ".ts",
    ".m2ts",
    ".mts",
    ".3gp",
    ".ogv",
    ".mp3",
    ".wav",
    ".flac",
    ".aac",
    ".ogg",
    ".opus",
    ".m4a",
    ".wma",
}

LANGUAGE_MAP = {
    "Auto Detect": None,
    "English": "en",
    "Hindi": "hi",
    "Punjabi": "pa",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Chinese": "zh",
    "Korean": "ko",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Arabic": "ar",
}


# ============================================================
# COLORS
# ============================================================

BG = "#06080d"
BG2 = "#090d15"

CARD = "#0d131f"
CARD2 = "#111a29"
CARD3 = "#172237"

TEXT = "#f4f7ff"
MUTED = "#7f8ca2"

BLUE = "#5b8dff"
PURPLE = "#8b5cff"
CYAN = "#45dcff"
GREEN = "#35d68f"
RED = "#ff5577"
ORANGE = "#ffad5a"


# ============================================================
# STYLE
# ============================================================

STYLE = f"""
QMainWindow {{
    background: {BG};
}}

QWidget {{
    color: {TEXT};
    font-family: "Segoe UI";
    font-size: 14px;
}}

QFrame#Window {{
    background: {BG};
}}

QFrame#TitleBar {{
    background: {BG2};
    border-bottom: 1px solid rgba(255,255,255,18);
}}

QFrame#Sidebar {{
    background: #080c14;
    border-right: 1px solid rgba(255,255,255,18);
}}

QFrame#Card {{
    background: {CARD};
    border: 1px solid rgba(255,255,255,24);
    border-radius: 18px;
}}

QFrame#VideoCard {{
    background: #000000;
    border: 1px solid rgba(255,255,255,20);
    border-radius: 20px;
}}

QLabel#Brand {{
    font-size: 17px;
    font-weight: 800;
}}

QLabel#PageTitle {{
    font-size: 27px;
    font-weight: 800;
}}

QLabel#NowPlaying {{
    color: {MUTED};
    font-size: 13px;
}}

QLabel#Section {{
    color: {MUTED};
    font-size: 11px;
    font-weight: 800;
}}

QLabel#Badge {{
    background: rgba(91,141,255,25);
    color: #c7d5ff;
    border: 1px solid rgba(91,141,255,75);
    border-radius: 8px;
    padding: 4px 9px;
    font-size: 10px;
    font-weight: 800;
}}

QPushButton {{
    background: {CARD2};
    color: {TEXT};
    border: 1px solid rgba(255,255,255,24);
    border-radius: 11px;
    padding: 9px 13px;
}}

QPushButton:hover {{
    background: {CARD3};
    border-color: rgba(91,141,255,115);
}}

QPushButton:pressed {{
    background: #263957;
}}

QPushButton#Nav {{
    background: transparent;
    border: none;
    border-radius: 10px;
    text-align: left;
    padding: 11px 12px;
    color: #a6b0c2;
}}

QPushButton#Nav:hover {{
    background: #131d2e;
    color: white;
}}

QPushButton#NavActive {{
    background: rgba(91,141,255,22);
    color: white;
    border: 1px solid rgba(91,141,255,50);
    border-radius: 10px;
    text-align: left;
    padding: 11px 12px;
    font-weight: 700;
}}

QPushButton#AI {{
    background: qlineargradient(
        x1:0,
        y1:0,
        x2:1,
        y2:1,
        stop:0 {CYAN},
        stop:0.5 {BLUE},
        stop:1 {PURPLE}
    );
    border: none;
    border-radius: 12px;
    font-weight: 800;
}}

QPushButton#AI:hover {{
    background: #8e91ff;
}}

QPushButton#Play {{
    background: qlineargradient(
        x1:0,
        y1:0,
        x2:1,
        y2:1,
        stop:0 {BLUE},
        stop:1 {PURPLE}
    );
    border: none;
    border-radius: 23px;
    min-width: 65px;
    max-width: 65px;
    min-height: 65px;
    max-height: 65px;
    font-size: 20px;
    font-weight: 800;
}}

QPushButton#Play:hover {{
    background: #789fff;
}}

QPushButton#WindowButton {{
    border: none;
    background: transparent;
    border-radius: 8px;
    padding: 5px;
}}

QPushButton#WindowButton:hover {{
    background: #192234;
}}

QPushButton#CloseButton:hover {{
    background: #c9364d;
}}

QPushButton#Pill {{
    background: #111a2a;
    border-radius: 15px;
    padding: 6px 12px;
}}

QLineEdit,
QTextEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox {{
    background: #0c1420;
    border: 1px solid #29364a;
    border-radius: 10px;
    padding: 8px;
}}

QTextEdit {{
    padding: 10px;
}}

QListWidget {{
    background: transparent;
    border: none;
    outline: none;
}}

QListWidget::item {{
    padding: 11px;
    margin: 2px;
    border-radius: 9px;
}}

QListWidget::item:hover {{
    background: #141e2f;
}}

QListWidget::item:selected {{
    background: #263c63;
}}

QTabWidget::pane {{
    background: transparent;
    border: 1px solid #28364a;
    border-radius: 10px;
}}

QTabBar::tab {{
    background: #0f1724;
    padding: 10px 16px;
    border-radius: 8px;
    margin-right: 3px;
}}

QTabBar::tab:selected {{
    background: #263b62;
}}

QSlider::groove:horizontal {{
    height: 5px;
    background: #252f42;
    border-radius: 3px;
}}

QSlider::sub-page:horizontal {{
    background: {BLUE};
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    width: 16px;
    height: 16px;
    margin: -6px 0;
    background: #87a7ff;
    border-radius: 8px;
}}

QProgressBar {{
    background: #131c2a;
    border: none;
    border-radius: 6px;
    height: 12px;
}}

QProgressBar::chunk {{
    background: qlineargradient(
        x1:0,
        y1:0,
        x2:1,
        y2:0,
        stop:0 {BLUE},
        stop:1 {PURPLE}
    );
    border-radius: 6px;
}}

QGroupBox {{
    border: 1px solid #29374c;
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 12px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 5px;
    color: {MUTED};
}}

QMenuBar {{
    background: #080c14;
    color: {TEXT};
    border-bottom: 1px solid #1d293b;
    padding: 2px 6px;
    spacing: 6px;
}}

QMenuBar::item {{
    background: transparent;
    color: {TEXT};
    padding: 8px 14px;
    margin: 2px;
    border-radius: 7px;
}}

QMenuBar::item:selected,
QMenuBar::item:pressed {{
    background: #16233a;
    color: white;
}}

QMenu {{
    background: #0b111c;
    color: {TEXT};
    border: 1px solid #29384d;
    padding: 7px;
    border-radius: 10px;
    min-width: 250px;
}}

QMenu::item {{
    background: transparent;
    color: {TEXT};
    padding: 9px 18px;
    margin: 2px 0;
    border-radius: 7px;
}}

QMenu::item:selected {{
    background: #1a2b48;
    color: white;
}}

QMenu::separator {{
    height: 1px;
    background: #25344a;
    margin: 7px 8px;
}}
"""


# ============================================================
# NOVA V20 VISUAL LAYER
# ============================================================
STYLE += f"""
QMainWindow {{
    background: #05070b;
}}

QMenuBar {{
    background: #070a11;
    border-bottom: 1px solid #1a2740;
    padding: 3px 9px;
    spacing: 7px;
}}
QMenuBar::item {{
    padding: 8px 14px;
    border-radius: 8px;
}}
QMenuBar::item:selected {{
    background: #121d31;
}}

QFrame#NovaChrome {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #09101b, stop:0.50 #0b1220, stop:1 #0a0f19);
    border: 1px solid #18273e;
    border-radius: 16px;
}}

QLabel#NovaBrand {{
    color: white;
    font-size: 24px;
    font-weight: 900;
    letter-spacing: 2px;
}}

QLabel#NovaBrandAccent {{
    color: #54dcff;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
}}

QLabel#CinemaPill {{
    background: rgba(69,220,255,26);
    color: #9deeff;
    border: 1px solid rgba(69,220,255,95);
    border-radius: 10px;
    padding: 5px 10px;
    font-size: 10px;
    font-weight: 800;
}}

QLabel#NowPlayingLarge {{
    color: #eef4ff;
    font-size: 15px;
    font-weight: 650;
}}

QFrame#CinemaVideoShell {{
    background: #000000;
    border: 1px solid #24364f;
    border-radius: 20px;
}}

QFrame#CinemaControls {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #0a111c, stop:0.45 #101927, stop:1 #0b111c);
    border: 1px solid #1e304c;
    border-radius: 18px;
}}

QPushButton#CinemaControl {{
    min-width: 48px;
    max-width: 48px;
    min-height: 48px;
    max-height: 48px;
    padding: 0;
    border-radius: 14px;
    background: #111b2b;
    border: 1px solid #263a59;
    font-size: 17px;
}}
QPushButton#CinemaControl:hover {{
    background: #182842;
    border-color: #4a73b8;
}}

QPushButton#PrimaryCinema {{
    min-width: 64px;
    max-width: 64px;
    min-height: 64px;
    max-height: 64px;
    border-radius: 22px;
    border: 0;
    font-size: 22px;
    font-weight: 900;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #49dfff, stop:0.46 #5e8dff, stop:1 #9a59ff);
}}
QPushButton#PrimaryCinema:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #71e8ff, stop:0.5 #78a0ff, stop:1 #b072ff);
}}

QPushButton#GlassAction {{
    background: rgba(17,27,43,220);
    border: 1px solid #263a59;
    border-radius: 10px;
    padding: 8px 12px;
}}
QPushButton#GlassAction:hover {{
    background: #182842;
    border-color: #5b8dff;
}}

QSlider#CinemaSeek::groove:horizontal {{
    height: 6px;
    background: #1b2940;
    border-radius: 3px;
}}
QSlider#CinemaSeek::sub-page:horizontal {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #45dcff, stop:0.55 #5b8dff, stop:1 #9b59ff);
    border-radius: 3px;
}}
QSlider#CinemaSeek::handle:horizontal {{
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
    background: white;
    border: 3px solid #6f92ff;
}}

QLabel#CinemaTime {{
    color: #cbd7eb;
    font-size: 12px;
    font-weight: 700;
}}

QFrame#GlassMini {{
    background: rgba(9,15,26,225);
    border: 1px solid #233752;
    border-radius: 12px;
}}

QLineEdit#NovaSearch {{
    background: #0b1422;
    border: 1px solid #223753;
    border-radius: 12px;
    padding: 9px 13px;
    color: white;
}}
QLineEdit#NovaSearch:focus {{
    border-color: #5b8dff;
}}
"""

# V01 dialog/readability layer: make every dialog surface dark and explicitly
# paint labels/check boxes/buttons so Windows light-mode title bars do not
# leave parts of the Nova UI looking white-on-white.
STYLE += """
QDialog {
    background: #0b111c;
    color: #f4f7ff;
}
QDialog QWidget {
    color: #f4f7ff;
}
QDialog QLabel {
    color: #f4f7ff;
    background: transparent;
}
QDialog QCheckBox {
    color: #f4f7ff;
    spacing: 7px;
}
QDialog QCheckBox::indicator {
    width: 17px;
    height: 17px;
    border-radius: 5px;
    border: 1px solid #3b4f70;
    background: #111a29;
}
QDialog QCheckBox::indicator:checked {
    background: #5b8dff;
    border-color: #5b8dff;
}
QDialog QPushButton {
    color: #f4f7ff;
    background: #111b2b;
    border: 1px solid #2b4163;
    border-radius: 10px;
    padding: 9px 16px;
    min-height: 34px;
}
QDialog QPushButton:hover {
    background: #1a2a43;
    border-color: #5b8dff;
}
QDialog QLineEdit,
QDialog QTextEdit,
QDialog QComboBox,
QDialog QSpinBox,
QDialog QDoubleSpinBox {
    color: #f4f7ff;
    background: #0c1420;
    border: 1px solid #293b57;
}
QDialog QGroupBox {
    color: #c7d5e9;
}
QDialog#NovaBackgroundLog QLabel {
    color: #f4f7ff;
}
QDialog#NovaBackgroundLog QCheckBox {
    color: #dce7f7;
}
QDialog#NovaBackgroundLog QTextEdit {
    background: #0a1220;
    color: #f1f6ff;
    border: 1px solid #2a3d5a;
    border-radius: 12px;
}
QDialog#NovaAboutDialog QTextEdit {
    background: #0a1220;
    color: #f1f6ff;
    border: 1px solid #2a3d5a;
    border-radius: 12px;
}
QLabel#FullscreenSubtitle {
    qproperty-alignment: AlignCenter;
}
"""


# ============================================================
# THEMES
# ============================================================

# Keep the original Nova stylesheet intact and apply a compact theme layer on
# top of it. This makes theme switching fast and avoids rewriting the whole QSS
# file every time a user changes the GUI style.
BASE_STYLE = STYLE

THEME_NAMES = [
    "Nova Dark",
    "Nebula",
    "Aurora",
    "Midnight",
    "OLED",
    "Crimson",
    "Emerald",
    "Platinum",
]

THEME_SPECS = {
    "Nova Dark": {
        "bg": "#06080d",
        "panel": "#090d15",
        "card": "#0d131f",
        "card2": "#111a29",
        "border": "#253653",
        "text": "#f4f7ff",
        "muted": "#7f8ca2",
        "accent": "#5b8dff",
        "accent2": "#8b5cff",
        "glow": "#45dcff",
        "active": "#162a4a",
    },
    "Nebula": {
        "bg": "#09070f",
        "panel": "#110b1b",
        "card": "#171023",
        "card2": "#211632",
        "border": "#4d2d69",
        "text": "#fff4ff",
        "muted": "#b99dc1",
        "accent": "#9d6cff",
        "accent2": "#ff5bbd",
        "glow": "#7c83ff",
        "active": "#392050",
    },
    "Aurora": {
        "bg": "#050b0a",
        "panel": "#081511",
        "card": "#0c1c16",
        "card2": "#11271f",
        "border": "#2f634c",
        "text": "#effff7",
        "muted": "#8bb3a1",
        "accent": "#35d68f",
        "accent2": "#45dcff",
        "glow": "#9dffb5",
        "active": "#123a2b",
    },
    "Midnight": {
        "bg": "#070a10",
        "panel": "#0a0f18",
        "card": "#101722",
        "card2": "#172235",
        "border": "#30435f",
        "text": "#eef4ff",
        "muted": "#8797ad",
        "accent": "#8aa4c8",
        "accent2": "#627ea8",
        "glow": "#9ab1d1",
        "active": "#1d304d",
    },
    "OLED": {
        "bg": "#000000",
        "panel": "#000000",
        "card": "#050505",
        "card2": "#090909",
        "border": "#262b35",
        "text": "#ffffff",
        "muted": "#8d96a5",
        "accent": "#a9c7ff",
        "accent2": "#d0a8ff",
        "glow": "#80e7ff",
        "active": "#101722",
    },
    "Crimson": {
        "bg": "#0d0609",
        "panel": "#14090d",
        "card": "#1d0e14",
        "card2": "#29121b",
        "border": "#643245",
        "text": "#fff3f6",
        "muted": "#bd929f",
        "accent": "#ff5577",
        "accent2": "#ff8a5b",
        "glow": "#ff6f91",
        "active": "#47202d",
    },
    "Emerald": {
        "bg": "#04100c",
        "panel": "#061711",
        "card": "#092119",
        "card2": "#103025",
        "border": "#2f6d58",
        "text": "#effff8",
        "muted": "#86b4a2",
        "accent": "#24d39a",
        "accent2": "#72e7ba",
        "glow": "#5fffd1",
        "active": "#124333",
    },
    "Platinum": {
        "bg": "#101318",
        "panel": "#15191f",
        "card": "#1b2027",
        "card2": "#242a33",
        "border": "#505a68",
        "text": "#f7f9fc",
        "muted": "#a7b0bd",
        "accent": "#d8e1ee",
        "accent2": "#9eb7d4",
        "glow": "#b9e1ff",
        "active": "#2d3744",
    },
}


# ============================================================
# INTERFACE LAYOUT THEMES
# ============================================================

# These are deliberately different interface compositions, not just color
# palettes. Each theme can change the navigation rail, queue placement,
# header density, spacing, control height and timeline/control order.
THEME_LAYOUTS = {
    "Nova Dark": {
        "mode": "cinema",
        "sidebar": False,
        "sidebar_width": 230,
        "queue": False,
        "orientation": Qt.Orientation.Horizontal,
        "header": "full",
        "margins": (18, 14, 18, 14),
        "spacing": 12,
        "controls_min": 122,
        "controls_max": 142,
        "timeline_first": False,
        "queue_ratio": 0,
    },
    "Nebula": {
        "mode": "studio",
        "sidebar": True,
        "sidebar_width": 238,
        "queue": True,
        "orientation": Qt.Orientation.Horizontal,
        "header": "full",
        "margins": (14, 12, 14, 12),
        "spacing": 10,
        "controls_min": 112,
        "controls_max": 132,
        "timeline_first": False,
        "queue_ratio": 32,
    },
    "Aurora": {
        "mode": "theater",
        "sidebar": False,
        "sidebar_width": 230,
        "queue": True,
        "orientation": Qt.Orientation.Vertical,
        "header": "full",
        "margins": (22, 16, 22, 16),
        "spacing": 9,
        "controls_min": 108,
        "controls_max": 124,
        "timeline_first": True,
        "queue_ratio": 25,
    },
    "Midnight": {
        "mode": "classic",
        "sidebar": True,
        "sidebar_width": 250,
        "queue": True,
        "orientation": Qt.Orientation.Horizontal,
        "header": "compact",
        "margins": (12, 10, 12, 10),
        "spacing": 8,
        "controls_min": 104,
        "controls_max": 118,
        "timeline_first": True,
        "queue_ratio": 28,
    },
    "OLED": {
        "mode": "minimal",
        "sidebar": False,
        "sidebar_width": 210,
        "queue": False,
        "orientation": Qt.Orientation.Horizontal,
        "header": "minimal",
        "margins": (8, 8, 8, 8),
        "spacing": 6,
        "controls_min": 88,
        "controls_max": 102,
        "timeline_first": True,
        "queue_ratio": 0,
    },
    "Crimson": {
        "mode": "director",
        "sidebar": True,
        "sidebar_width": 282,
        "queue": False,
        "orientation": Qt.Orientation.Horizontal,
        "header": "compact",
        "margins": (20, 14, 20, 14),
        "spacing": 12,
        "controls_min": 118,
        "controls_max": 136,
        "timeline_first": False,
        "queue_ratio": 0,
    },
    "Emerald": {
        "mode": "library",
        "sidebar": True,
        "sidebar_width": 220,
        "queue": True,
        "orientation": Qt.Orientation.Vertical,
        "header": "compact",
        "margins": (14, 12, 14, 12),
        "spacing": 7,
        "controls_min": 100,
        "controls_max": 114,
        "timeline_first": True,
        "queue_ratio": 30,
    },
    "Platinum": {
        "mode": "workstation",
        "sidebar": True,
        "sidebar_width": 205,
        "queue": True,
        "orientation": Qt.Orientation.Horizontal,
        "header": "full",
        "margins": (10, 9, 10, 9),
        "spacing": 8,
        "controls_min": 96,
        "controls_max": 110,
        "timeline_first": False,
        "queue_ratio": 38,
    },
}

THEME_DESCRIPTIONS = {
    "Nova Dark": "Immersive cinema layout — video first, distraction-free controls.",
    "Nebula": "Studio layout — navigation rail and queue stay visible beside the video.",
    "Aurora": "Theater layout — queue moves below the video for a stacked workspace.",
    "Midnight": "Classic layout — traditional media-player navigation and queue arrangement.",
    "OLED": "Minimal layout — maximum video area with compact controls and almost no chrome.",
    "Crimson": "Director layout — wide navigation rail with a clean single-player workspace.",
    "Emerald": "Library layout — navigation plus a bottom queue for browsing and playback together.",
    "Platinum": "Workstation layout — dense professional arrangement with a larger queue panel.",
}


def theme_stylesheet(name):
    """Return the visual override layer for one Nova GUI theme."""
    spec = THEME_SPECS.get(name, THEME_SPECS["Nova Dark"])
    bg = spec["bg"]
    panel = spec["panel"]
    card = spec["card"]
    card2 = spec["card2"]
    border = spec["border"]
    text = spec["text"]
    muted = spec["muted"]
    accent = spec["accent"]
    accent2 = spec["accent2"]
    glow = spec["glow"]
    active = spec["active"]

    return f"""
QMainWindow {{
    background: {bg};
}}
QWidget {{
    color: {text};
}}
QFrame#Window {{
    background: {bg};
}}
QFrame#TitleBar {{
    background: {panel};
    border-bottom: 1px solid {border};
}}
QFrame#Sidebar {{
    background: {panel};
    border-right: 1px solid {border};
}}
QFrame#Card, QFrame#GlassMini {{
    background: {card};
    border-color: {border};
}}
QFrame#NovaChrome {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {panel}, stop:0.5 {card2}, stop:1 {panel});
    border-color: {border};
}}
QFrame#CinemaControls {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {panel}, stop:0.5 {card2}, stop:1 {panel});
    border-color: {border};
}}
QLabel#NovaBrandAccent {{
    color: {glow};
}}
QLabel#NowPlayingLarge, QLabel#PageTitle, QLabel#Brand, QLabel#CinemaTime {{
    color: {text};
}}
QLabel#NowPlaying, QLabel#Section {{
    color: {muted};
}}
QPushButton {{
    background: {card2};
    color: {text};
    border-color: {border};
}}
QPushButton:hover {{
    background: {active};
    border-color: {accent};
}}
QPushButton#Nav {{
    color: {muted};
}}
QPushButton#Nav:hover, QPushButton#NavActive {{
    background: {active};
    color: {text};
    border-color: {accent};
}}
QPushButton#AI, QPushButton#PrimaryCinema, QPushButton#Play {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 {glow}, stop:0.5 {accent}, stop:1 {accent2});
}}
QPushButton#AI:hover, QPushButton#PrimaryCinema:hover, QPushButton#Play:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 {accent}, stop:0.5 {glow}, stop:1 {accent2});
}}
QSlider::sub-page:horizontal, QSlider#CinemaSeek::sub-page:horizontal {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {glow}, stop:0.55 {accent}, stop:1 {accent2});
}}
QSlider::handle:horizontal {{
    background: {text};
    border-color: {accent};
}}
QLineEdit#NovaSearch:focus {{
    border-color: {accent};
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {glow}, stop:1 {accent2});
}}
QTabBar::tab:selected {{
    background: {active};
    color: {text};
}}
QMenuBar {{
    background: {panel};
    color: {text};
}}
QMenuBar::item:selected {{
    background: {active};
    color: {text};
}}
QMenu {{
    background: {panel};
    color: {text};
    border-color: {border};
}}
QMenu::item:selected {{
    background: {active};
    color: {text};
}}
QToolTip {{
    background: {panel};
    color: {text};
    border-color: {border};
}}
QFrame#Sidebar {{
    border-right: 1px solid {border};
}}
QFrame#CinemaControls {{
    border-radius: 16px;
}}
QFrame#CinemaVideoShell {{
    border-color: {border};
}}
QDialog, QDialog QWidget, QDialog QLabel {{
    color: {text};
}}
QDialog {{
    background: {panel};
}}
QDialog QTextEdit, QDialog QLineEdit, QDialog QComboBox,
QDialog QSpinBox, QDialog QDoubleSpinBox {{
    background: {card};
    color: {text};
    border-color: {border};
}}
QDialog QPushButton {{
    background: {card2};
    color: {text};
    border-color: {border};
}}
QDialog QPushButton:hover {{
    background: {active};
    border-color: {accent};
}}
"""


# ============================================================
# UTILITIES
# ============================================================

def read_json(path, default):
    try:
        if path.exists():
            return json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )
    except Exception:
        pass

    return default


def write_json(path, data):
    try:
        path.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )
    except Exception:
        pass


def ffmpeg():
    """Locate an FFmpeg executable for AI extraction/conversion tasks.

    Qt Multimedia may have its own FFmpeg runtime, but that does not make
    ffmpeg.exe available to subprocess calls. Try PATH first, then a few
    common local locations so AI subtitles can work when FFmpeg is installed
    but not exported to PATH.
    """
    found = shutil.which("ffmpeg")
    if found:
        return found

    candidates = []
    here = Path(__file__).resolve().parent
    candidates.extend([
        here / "ffmpeg.exe",
        here / "bin" / "ffmpeg.exe",
        Path.cwd() / "ffmpeg.exe",
        Path.cwd() / "bin" / "ffmpeg.exe",
        Path(r"C:\ffmpeg\bin\ffmpeg.exe"),
        Path(r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"),
        Path(r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe"),
    ])
    for candidate in candidates:
        try:
            if candidate.is_file():
                return str(candidate)
        except Exception:
            pass
    return None


def ffprobe():
    return shutil.which("ffprobe")


def is_media(path):
    return (
        Path(path).suffix.lower()
        in MEDIA_EXTENSIONS
    )


def format_time(ms):
    ms = max(
        0,
        int(ms or 0)
    )

    total = ms // 1000

    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60

    if h:
        return (
            f"{h:02}:{m:02}:{s:02}"
        )

    return (
        f"{m:02}:{s:02}"
    )


def parse_timestamp(value):
    value = value.strip()
    value = value.replace(
        ",",
        "."
    )

    parts = value.split(":")

    try:

        if len(parts) == 3:

            h, m, sec = parts

            return (
                int(h) * 3600
                + int(m) * 60
                + float(sec)
            )

        if len(parts) == 2:

            m, sec = parts

            return (
                int(m) * 60
                + float(sec)
            )

    except Exception:
        pass

    return 0.0


def srt_timestamp(seconds):
    ms = max(
        0,
        int(round(seconds * 1000))
    )

    h = ms // 3600000
    ms %= 3600000

    m = ms // 60000
    ms %= 60000

    s = ms // 1000
    ms %= 1000

    return (
        f"{h:02}:"
        f"{m:02}:"
        f"{s:02},"
        f"{ms:03}"
    )


# ============================================================
# NATIVE RESIZABLE TITLE BAR
# ============================================================

class ResizeHelper(QWidget):

    def __init__(
        self,
        window,
        parent=None
    ):
        super().__init__(parent)

        self.window = window

        self.setMouseTracking(
            True
        )

        self.edge = 8

        self.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            False
        )

    def mouseMoveEvent(
        self,
        event
    ):

        pos = event.position().toPoint()

        rect = self.rect()

        left = pos.x() <= self.edge
        right = pos.x() >= rect.width() - self.edge

        top = pos.y() <= self.edge
        bottom = pos.y() >= rect.height() - self.edge

        cursor = Qt.ArrowCursor

        if top and left:
            cursor = Qt.SizeFDiagCursor

        elif bottom and right:
            cursor = Qt.SizeFDiagCursor

        elif top and right:
            cursor = Qt.SizeBDiagCursor

        elif bottom and left:
            cursor = Qt.SizeBDiagCursor

        elif left or right:
            cursor = Qt.SizeHorCursor

        elif top or bottom:
            cursor = Qt.SizeVerCursor

        self.setCursor(
            QCursor(cursor)
        )

    def mousePressEvent(
        self,
        event
    ):

        if (
            event.button()
            != Qt.LeftButton
        ):
            return

        pos = event.position().toPoint()

        rect = self.rect()

        left = pos.x() <= self.edge
        right = pos.x() >= rect.width() - self.edge

        top = pos.y() <= self.edge
        bottom = pos.y() >= rect.height() - self.edge

        edges = Qt.Edges()

        if left:
            edges |= Qt.LeftEdge

        if right:
            edges |= Qt.RightEdge

        if top:
            edges |= Qt.TopEdge

        if bottom:
            edges |= Qt.BottomEdge

        if edges:

            try:

                self.window.windowHandle().startSystemResize(
                    edges
                )

            except Exception:

                pass


# ============================================================
# CUSTOM TITLE BAR
# ============================================================

class TitleBar(QFrame):

    def __init__(
        self,
        parent
    ):

        super().__init__(
            parent
        )

        self.parent_window = parent

        self.setObjectName(
            "TitleBar"
        )

        self.setFixedHeight(
            48
        )

        layout = QHBoxLayout(
            self
        )

        layout.setContentsMargins(
            12,
            0,
            8,
            0
        )

        layout.setSpacing(
            5
        )

        icon = QLabel(
            "◈"
        )

        icon.setStyleSheet(
            f"""
            color:{CYAN};
            font-size:20px;
            font-weight:800;
            """
        )

        layout.addWidget(
            icon
        )

        title = QLabel(
            APP_NAME
        )

        title.setObjectName(
            "Brand"
        )

        layout.addWidget(
            title
        )

        layout.addStretch()

        minimize = QPushButton(
            "—"
        )

        minimize.setObjectName(
            "WindowButton"
        )

        minimize.setFixedSize(
            42,
            34
        )

        minimize.clicked.connect(
            parent.showMinimized
        )

        maximize = QPushButton(
            "□"
        )

        maximize.setObjectName(
            "WindowButton"
        )

        maximize.setFixedSize(
            42,
            34
        )

        maximize.clicked.connect(
            self.toggle_maximize
        )

        close = QPushButton(
            "✕"
        )

        close.setObjectName(
            "CloseButton"
        )

        close.setFixedSize(
            42,
            34
        )

        close.clicked.connect(
            parent.close
        )

        layout.addWidget(
            minimize
        )

        layout.addWidget(
            maximize
        )

        layout.addWidget(
            close
        )

        self._drag_position = None

    def toggle_maximize(self):

        if self.parent_window.isMaximized():

            self.parent_window.showNormal()

        else:

            self.parent_window.showMaximized()

    def mousePressEvent(
        self,
        event
    ):

        if event.button() == Qt.LeftButton:

            self._drag_position = (
                event.globalPosition()
                .toPoint()
                - self.parent_window.frameGeometry().topLeft()
            )

            event.accept()

    def mouseMoveEvent(
        self,
        event
    ):

        if (
            self._drag_position
            and event.buttons()
            & Qt.LeftButton
            and not self.parent_window.isMaximized()
        ):

            self.parent_window.move(
                event.globalPosition().toPoint()
                - self._drag_position
            )

            event.accept()

    def mouseReleaseEvent(
        self,
        event
    ):

        self._drag_position = None


# ============================================================
# WHISPER WORKER
# ============================================================

class WhisperWorker(QObject):

    progress = Signal(int, str)
    finished = Signal(dict)
    failed = Signal(str)

    # Keep at most one cached model per backend/model combination. This avoids
    # reloading Whisper weights every time the user generates subtitles.
    _model_cache = {}

    def __init__(
        self,
        source_file,
        model,
        language,
        device
    ):
        super().__init__()
        self.source_file = str(source_file)
        self.model = str(model or "base")
        self.language = language
        self.device = str(device or "auto").lower()
        self.temp_audio = None
        self.cancel_requested = False
        self._dll_dirs = []

    def _emit(self, value, text):
        try:
            self.progress.emit(int(max(0, min(100, value))), str(text))
        except Exception:
            pass

    def _add_dll_dir(self, directory):
        directory = str(directory)
        if not directory or not os.path.isdir(directory):
            return
        if directory not in self._dll_dirs:
            self._dll_dirs.append(directory)
            try:
                if hasattr(os, "add_dll_directory"):
                    os.add_dll_directory(directory)
            except Exception:
                pass
            # Some Windows wheels/loaders still consult PATH.
            current = os.environ.get("PATH", "")
            parts = current.split(os.pathsep) if current else []
            if directory not in parts:
                os.environ["PATH"] = directory + os.pathsep + current

    def _prepare_cuda_runtime(self):
        """Add CUDA runtime DLL directories that may live inside Python wheels.

        On Windows, NVIDIA runtime wheels keep DLLs under site-packages rather
        than putting them on the system PATH. CTranslate2 can report a CUDA
        device even when a lazy-loaded cuBLAS/cuDNN DLL is unavailable; the
        actual failure may therefore appear only when the transcribe generator
        starts decoding.
        """
        if os.name != "nt":
            return []

        dll_dirs = []

        def add_dir(path):
            try:
                path = Path(path)
                if not path.is_dir():
                    return
                text = str(path.resolve())
                if text in dll_dirs:
                    return
                dll_dirs.append(text)
                self._add_dll_dir(text)
            except Exception:
                pass

        # Look inside NVIDIA Python wheels first. Their Windows wheels are
        # distributed with the actual CUDA DLLs under package-local bin dirs.
        for module_name in ("nvidia.cublas", "nvidia.cudnn"):
            try:
                module = importlib.import_module(module_name)
                roots = []
                module_path = getattr(module, "__path__", None)
                if module_path:
                    roots.extend(list(module_path))
                module_file = getattr(module, "__file__", None)
                if module_file:
                    roots.append(str(Path(module_file).parent))
                for root in roots:
                    root_path = Path(root)
                    add_dir(root_path / "bin")
                    add_dir(root_path / "lib")
                    # Some wheel layouts add another nested version/bin.
                    try:
                        for dll in root_path.rglob("*.dll"):
                            add_dir(dll.parent)
                            # Avoid walking unnecessarily deep once we found
                            # a CUDA runtime DLL directory.
                            if any(name in dll.name.lower() for name in (
                                "cublas64_12", "cudnn64_9", "cudnn_ops64_9", "cudnn_cnn64_9"
                            )):
                                pass
                    except Exception:
                        pass
            except Exception:
                pass

        # Also inspect the active Python environment directly.
        prefixes = []
        for getter in (site.getsitepackages,):
            try:
                prefixes.extend(getter())
            except Exception:
                pass
        try:
            prefixes.append(site.getusersitepackages())
        except Exception:
            pass
        prefixes.extend([sys.prefix, str(Path(sys.executable).parent)])

        seen = set()
        for prefix in prefixes:
            if not prefix:
                continue
            root = Path(prefix)
            key = str(root.resolve()) if root.exists() else str(root)
            if key in seen:
                continue
            seen.add(key)
            for candidate in (
                root / "nvidia" / "cublas" / "bin",
                root / "nvidia" / "cublas" / "lib",
                root / "nvidia" / "cudnn" / "bin",
                root / "nvidia" / "cudnn" / "lib",
            ):
                add_dir(candidate)

        # Finally add a normal CUDA 12 installation if the user has one.
        for base in (
            os.environ.get("CUDA_PATH_V12_0", ""),
            os.environ.get("CUDA_PATH_V12_1", ""),
            os.environ.get("CUDA_PATH_V12_2", ""),
            os.environ.get("CUDA_PATH_V12_3", ""),
            os.environ.get("CUDA_PATH_V12_4", ""),
            os.environ.get("CUDA_PATH_V12_5", ""),
            os.environ.get("CUDA_PATH_V12_6", ""),
            os.environ.get("CUDA_PATH_V12_7", ""),
            os.environ.get("CUDA_PATH_V12_8", ""),
            os.environ.get("CUDA_PATH_V12_9", ""),
            os.environ.get("CUDA_PATH", ""),
        ):
            if base:
                add_dir(Path(base) / "bin")

        return dll_dirs

    def _cuda_runtime_check(self):
        """Use CTranslate2 for GPU detection, while preparing Windows DLL paths."""
        prepared = self._prepare_cuda_runtime()

        # Do not use PATH/DLL presence as the GPU selection test. CTranslate2
        # is the actual inference backend and can report the CUDA device even
        # when DLLs are loaded lazily later during transcription.
        try:
            import ctranslate2
            count = int(ctranslate2.get_cuda_device_count())
            if count > 0:
                # Give a useful diagnostic, but keep CUDA selection based on
                # the backend's actual device visibility.
                missing = []
                if os.name == "nt":
                    try:
                        ctypes.WinDLL("cublas64_12.dll")
                    except Exception:
                        missing.append("cuBLAS (cublas64_12.dll)")
                    try:
                        ctypes.WinDLL("cudnn64_9.dll")
                    except Exception:
                        try:
                            ctypes.WinDLL("cudnn_cnn64_9.dll")
                        except Exception:
                            missing.append("cuDNN 9")
                if missing:
                    return True, (
                        f"CTranslate2 reports {count} CUDA device(s), but Windows "
                        f"could not directly load: {', '.join(missing)}. "
                        "CUDA will be attempted and the exact inference error will "
                        "be reported if a runtime library is actually missing."
                    )
                return True, f"CTranslate2 reports {count} CUDA device(s); CUDA runtime prepared ({len(prepared)} DLL directories)."

            return False, "CTranslate2 reports no CUDA devices."
        except Exception as exc:
            return False, f"CTranslate2 CUDA detection failed: {exc}"

    def _load_model(self, device):
        from faster_whisper import WhisperModel

        key = (self.model, device)
        cached = self._model_cache.get(key)
        if cached is not None:
            self._emit(15, f"Using cached Whisper {self.model} model ({device.upper()})…")
            return cached

        cpu_threads = max(2, min(12, os.cpu_count() or 4))
        if device == "cuda":
            self._emit(12, f"Loading Whisper {self.model} on GPU (CUDA 12)…")
            model = WhisperModel(
                self.model,
                device="cuda",
                compute_type="float16",
            )
        else:
            self._emit(12, f"Loading Whisper {self.model} on CPU INT8 ({cpu_threads} threads)…")
            model = WhisperModel(
                self.model,
                device="cpu",
                compute_type="int8",
                cpu_threads=cpu_threads,
                num_workers=1,
            )

        self._model_cache[key] = model
        return model

    def _transcribe_to_list(self, model):
        kwargs = {
            "language": self.language,
            "beam_size": 1,
            "best_of": 1,
            "temperature": 0.0,
            "vad_filter": True,
            "vad_parameters": {"min_silence_duration_ms": 500},
            "word_timestamps": False,
            "condition_on_previous_text": False,
            "compression_ratio_threshold": 2.4,
            "log_prob_threshold": -1.0,
            "no_speech_threshold": 0.6,
        }

        # faster-whisper uses PyAV for decoding, so we can transcribe the
        # original media directly. This removes the previous FFmpeg->WAV step,
        # disk I/O, temporary-file creation and several minutes of startup work
        # on large videos.
        segments, info = model.transcribe(self.source_file, **kwargs)

        result_segments = []
        duration = float(getattr(info, "duration", 0.0) or 0.0)
        last_percent = -1

        for segment in segments:
            if self.cancel_requested:
                raise RuntimeError("AI subtitle generation was cancelled.")

            text = str(getattr(segment, "text", "") or "").strip()
            if not text:
                continue

            start = float(getattr(segment, "start", 0.0) or 0.0)
            end = float(getattr(segment, "end", start) or start)
            result_segments.append({
                "start": start,
                "end": max(start, end),
                "text": text,
                "words": []
            })

            if duration > 0:
                percent = min(97, 20 + int((end / duration) * 77))
            else:
                percent = min(97, 20 + min(77, len(result_segments)))

            if percent != last_percent:
                last_percent = percent
                self._emit(
                    percent,
                    f"Transcribing… {format_time(int(end * 1000))}"
                )

        return result_segments, info

    @Slot()
    def run(self):
        try:
            source = Path(self.source_file)
            if not source.exists() or not source.is_file():
                raise RuntimeError("The selected media file no longer exists.")
            if source.stat().st_size <= 0:
                raise RuntimeError("The selected media file is empty.")

            self._emit(2, "Preparing audio decoder…")

            try:
                from faster_whisper import WhisperModel
            except Exception as exc:
                raise RuntimeError(
                    "faster-whisper could not be imported. Install it with:\n"
                    "pip install --upgrade faster-whisper\n\n"
                    f"Import error: {exc}"
                ) from exc

            requested = self.device
            runtime_ok, runtime_note = self._cuda_runtime_check()

            if requested in ("gpu", "cuda"):
                if runtime_ok:
                    selected_device = "cuda"
                    self._emit(8, "CUDA device detected — initializing GPU Whisper…")
                else:
                    selected_device = "cpu"
                    self._emit(8, "GPU CUDA backend unavailable — using CPU INT8…")
                    self._emit(9, runtime_note)
            elif requested == "auto":
                if runtime_ok:
                    selected_device = "cuda"
                    self._emit(8, "CUDA device detected — initializing GPU Whisper…")
                else:
                    selected_device = "cpu"
                    self._emit(8, "CUDA backend unavailable — using CPU INT8 directly…")
                    self._emit(9, runtime_note)
            else:
                selected_device = "cpu"

            try:
                model = self._load_model(selected_device)
            except Exception as model_exc:
                if selected_device != "cuda":
                    raise RuntimeError(
                        f"Whisper model '{self.model}' could not be loaded on CPU.\n{model_exc}"
                    ) from model_exc

                self._emit(18, "CUDA model failed — switching to CPU INT8…")
                self._emit(19, str(model_exc).strip()[:500])
                self._model_cache.pop((self.model, "cuda"), None)
                import gc
                gc.collect()
                selected_device = "cpu"
                model = self._load_model("cpu")

            self._emit(20, f"Transcribing with {selected_device.upper()}…")

            try:
                result_segments, info = self._transcribe_to_list(model)
            except Exception as transcribe_exc:
                message = str(transcribe_exc).strip()
                is_cuda_failure = (
                    selected_device == "cuda"
                    and any(token in message.lower() for token in (
                        "cublas", "cudnn", "cuda", "dll", "cannot be loaded", "library"
                    ))
                )
                if not is_cuda_failure:
                    raise

                self._emit(22, "CUDA transcription failed — switching to CPU INT8…")
                self._emit(23, message[:500])
                if any(token in message.lower() for token in ("cublas", "cudnn", "cuda", "dll", "cannot be loaded")):
                    self._emit(24, "GPU runtime libraries are missing or not loadable. Install CUDA 12 cuBLAS + cuDNN 9, then restart Nova.")
                    self._emit(25, 'Run: python -m pip install --upgrade nvidia-cublas-cu12 "nvidia-cudnn-cu12==9.*"')
                self._model_cache.pop((self.model, "cuda"), None)
                import gc
                gc.collect()

                selected_device = "cpu"
                model = self._load_model("cpu")
                self._emit(26, "CPU fallback active…")
                result_segments, info = self._transcribe_to_list(model)

            if not result_segments:
                raise RuntimeError(
                    "Whisper completed but returned no speech segments. "
                    "The audio may be silent, extremely noisy, or unsupported."
                )

            self._emit(98, "Finalizing subtitles…")
            self.finished.emit({
                "segments": result_segments,
                "language": getattr(info, "language", "unknown"),
                "probability": getattr(info, "language_probability", 0),
                "device": selected_device,
                "model": self.model,
            })

        except Exception:
            self.failed.emit(traceback.format_exc())



# ============================================================
# SETTINGS DIALOG
# ============================================================

class SettingsDialog(QDialog):

    def __init__(
        self,
        config,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.config = config

        self.setWindowTitle(
            "Nova Settings"
        )

        self.resize(
            820,
            650
        )

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "Settings"
        )

        title.setFont(
            QFont(
                "Segoe UI",
                23,
                QFont.Weight.Bold
            )
        )

        layout.addWidget(
            title
        )

        subtitle = QLabel(
            "Customize playback, appearance, subtitles, "
            "AI, library and application behavior."
        )

        subtitle.setStyleSheet(
            f"color:{MUTED};"
        )

        layout.addWidget(
            subtitle
        )

        tabs = QTabWidget()

        # ----------------------------------------------------
        # GENERAL
        # ----------------------------------------------------

        general = QWidget()

        general_form = QFormLayout(
            general
        )

        self.auto_play = QCheckBox()

        self.auto_play.setChecked(
            config.get(
                "autoplay",
                True
            )
        )

        general_form.addRow(
            "Autoplay:",
            self.auto_play
        )

        self.remember_position = QCheckBox()

        self.remember_position.setChecked(
            config.get(
                "remember_position",
                True
            )
        )

        general_form.addRow(
            "Remember playback position:",
            self.remember_position
        )

        self.loop_playlist = QCheckBox()

        self.loop_playlist.setChecked(
            config.get(
                "loop",
                False
            )
        )

        general_form.addRow(
            "Loop playlist:",
            self.loop_playlist
        )

        self.seek = QSpinBox()

        self.seek.setRange(
            1,
            120
        )

        self.seek.setValue(
            config.get(
                "seek_seconds",
                5
            )
        )

        general_form.addRow(
            "Seek interval:",
            self.seek
        )

        tabs.addTab(
            general,
            "General"
        )

        # ----------------------------------------------------
        # APPEARANCE
        # ----------------------------------------------------

        appearance = QWidget()

        appearance_form = QFormLayout(
            appearance
        )

        self.show_sidebar = QCheckBox()

        self.show_sidebar.setChecked(
            config.get(
                "show_sidebar",
                True
            )
        )

        appearance_form.addRow(
            "Show navigation sidebar:",
            self.show_sidebar
        )

        self.compact_controls = QCheckBox()

        self.compact_controls.setChecked(
            config.get(
                "compact_controls",
                False
            )
        )

        appearance_form.addRow(
            "Compact playback controls:",
            self.compact_controls
        )

        self.animations = QCheckBox()

        self.animations.setChecked(
            config.get(
                "animations",
                True
            )
        )

        appearance_form.addRow(
            "Interface animations:",
            self.animations
        )

        tabs.addTab(
            appearance,
            "Appearance"
        )

        # ----------------------------------------------------
        # SUBTITLES
        # ----------------------------------------------------

        subtitles = QWidget()

        subtitle_form = QFormLayout(
            subtitles
        )

        self.subtitle_size = QSpinBox()

        self.subtitle_size.setRange(
            10,
            72
        )

        self.subtitle_size.setValue(
            config.get(
                "subtitle_size",
                18
            )
        )

        subtitle_form.addRow(
            "Subtitle size:",
            self.subtitle_size
        )

        self.subtitle_delay = QSpinBox()

        self.subtitle_delay.setRange(
            -60000,
            60000
        )

        self.subtitle_delay.setSingleStep(
            100
        )

        subtitle_form.addRow(
            "Default subtitle delay:",
            self.subtitle_delay
        )

        tabs.addTab(
            subtitles,
            "Subtitles"
        )

        # ----------------------------------------------------
        # AUDIO
        # ----------------------------------------------------

        audio = QWidget()

        audio_form = QFormLayout(
            audio
        )

        self.volume = QSpinBox()

        self.volume.setRange(
            0,
            100
        )

        self.volume.setValue(
            config.get(
                "volume",
                75
            )
        )

        audio_form.addRow(
            "Startup volume:",
            self.volume
        )

        self.normalization = QCheckBox()

        self.normalization.setChecked(
            config.get(
                "normalization",
                False
            )
        )

        audio_form.addRow(
            "Replay/volume normalization:",
            self.normalization
        )

        tabs.addTab(
            audio,
            "Audio"
        )

        # ----------------------------------------------------
        # AI
        # ----------------------------------------------------

        ai = QWidget()

        ai_form = QFormLayout(
            ai
        )

        self.whisper_model = QComboBox()

        self.whisper_model.addItems(
            [
                "tiny",
                "base",
                "small",
                "medium",
                "large-v3"
            ]
        )

        self.whisper_model.setCurrentText(
            config.get(
                "ai_model",
                "base"
            )
        )

        ai_form.addRow(
            "Whisper model:",
            self.whisper_model
        )

        self.ai_device = QComboBox()

        self.ai_device.addItems(
            [
                "Auto",
                "CPU",
                "GPU"
            ]
        )

        ai_device_saved = config.get(
            "ai_device",
            "auto"
        )

        self.ai_device.setCurrentText(
            ai_device_saved.title()
        )

        ai_form.addRow(
            "Whisper device:",
            self.ai_device
        )

        self.openai_model = QLineEdit()

        self.openai_model.setText(
            config.get(
                "openai_model",
                ""
            )
        )

        ai_form.addRow(
            "Online AI model:",
            self.openai_model
        )

        self.openai_key = QLineEdit()

        self.openai_key.setEchoMode(
            QLineEdit.Password
        )

        self.openai_key.setText(
            config.get(
                "openai_api_key",
                ""
            )
        )

        ai_form.addRow(
            "API key:",
            self.openai_key
        )

        ai_note = QLabel(
            "Local Whisper transcription does not require an "
            "online API. The online AI settings are optional."
        )

        ai_note.setWordWrap(
            True
        )

        ai_note.setStyleSheet(
            f"color:{MUTED};"
        )

        ai_form.addRow(
            "",
            ai_note
        )

        tabs.addTab(
            ai,
            "AI"
        )

        # ----------------------------------------------------
        # LIBRARY
        # ----------------------------------------------------

        library = QWidget()

        library_form = QFormLayout(
            library
        )

        self.scan_subfolders = QCheckBox()

        self.scan_subfolders.setChecked(
            config.get(
                "scan_subfolders",
                True
            )
        )

        library_form.addRow(
            "Scan subfolders:",
            self.scan_subfolders
        )

        self.auto_library = QCheckBox()

        self.auto_library.setChecked(
            config.get(
                "auto_library",
                False
            )
        )

        library_form.addRow(
            "Automatically scan library:",
            self.auto_library
        )

        tabs.addTab(
            library,
            "Library"
        )

        # ----------------------------------------------------
        # ADVANCED
        # ----------------------------------------------------

        advanced = QWidget()

        advanced_form = QFormLayout(
            advanced
        )

        self.debug = QCheckBox()

        self.debug.setChecked(
            config.get(
                "debug",
                False
            )
        )

        advanced_form.addRow(
            "Debug logging:",
            self.debug
        )

        self.hardware = QCheckBox()

        self.hardware.setChecked(
            config.get(
                "hardware_acceleration",
                True
            )
        )

        advanced_form.addRow(
            "Allow hardware acceleration:",
            self.hardware
        )

        tabs.addTab(
            advanced,
            "Advanced"
        )

        layout.addWidget(
            tabs
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save
            | QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(
            self.accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout.addWidget(
            buttons
        )

    def apply(
        self
    ):

        self.config[
            "autoplay"
        ] = self.auto_play.isChecked()

        self.config[
            "remember_position"
        ] = self.remember_position.isChecked()

        self.config[
            "loop"
        ] = self.loop_playlist.isChecked()

        self.config[
            "seek_seconds"
        ] = self.seek.value()

        self.config[
            "show_sidebar"
        ] = self.show_sidebar.isChecked()

        self.config[
            "compact_controls"
        ] = self.compact_controls.isChecked()

        self.config[
            "animations"
        ] = self.animations.isChecked()

        self.config[
            "subtitle_size"
        ] = self.subtitle_size.value()

        self.config[
            "subtitle_delay"
        ] = self.subtitle_delay.value()

        self.config[
            "volume"
        ] = self.volume.value()

        self.config[
            "normalization"
        ] = self.normalization.isChecked()

        self.config[
            "ai_model"
        ] = self.whisper_model.currentText()

        self.config[
            "ai_device"
        ] = self.ai_device.currentText().lower()

        self.config[
            "openai_model"
        ] = self.openai_model.text().strip()

        self.config[
            "openai_api_key"
        ] = self.openai_key.text().strip()

        self.config[
            "scan_subfolders"
        ] = self.scan_subfolders.isChecked()

        self.config[
            "auto_library"
        ] = self.auto_library.isChecked()

        self.config[
            "debug"
        ] = self.debug.isChecked()

        self.config[
            "hardware_acceleration"
        ] = self.hardware.isChecked()


# ============================================================
# TRANSCRIPT WINDOW
# ============================================================

class TranscriptDialog(QDialog):

    jump = Signal(
        int
    )

    def __init__(
        self,
        segments,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.segments = segments

        self.setWindowTitle(
            "AI Transcript"
        )

        self.resize(
            960,
            680
        )

        layout = QVBoxLayout(
            self
        )

        header = QHBoxLayout()

        title = QLabel(
            "Transcript"
        )

        title.setFont(
            QFont(
                "Segoe UI",
                22,
                QFont.Weight.Bold
            )
        )

        header.addWidget(
            title
        )

        header.addStretch()

        search = QLineEdit()

        search.setPlaceholderText(
            "Search transcript..."
        )

        search.setMaximumWidth(
            300
        )

        header.addWidget(
            search
        )

        layout.addLayout(
            header
        )

        self.list = QListWidget()

        layout.addWidget(
            self.list
        )

        self.populate()

        search.textChanged.connect(
            self.filter
        )

        self.list.itemDoubleClicked.connect(
            self.open_time
        )

        close = QPushButton(
            "Close"
        )

        close.clicked.connect(
            self.accept
        )

        layout.addWidget(
            close
        )

    def populate(self):

        for i, segment in enumerate(
            self.segments
        ):

            item = QListWidgetItem(
                "["
                + format_time(
                    segment["start"] * 1000
                )
                + "]  "
                + segment["text"]
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                i
            )

            self.list.addItem(
                item
            )

    def filter(
        self,
        value
    ):

        value = value.lower()

        for i in range(
            self.list.count()
        ):

            item = self.list.item(i)

            item.setHidden(
                value not in item.text().lower()
            )

    def open_time(
        self,
        item
    ):

        index = item.data(
            Qt.ItemDataRole.UserRole
        )

        if index is None:
            return

        self.jump.emit(
            int(
                self.segments[index][
                    "start"
                ]
                * 1000
            )
        )


# ============================================================
# MEDIA INFORMATION
# ============================================================

class MediaInfoDialog(QDialog):

    def __init__(
        self,
        source,
        player,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.setWindowTitle(
            "Media Information"
        )

        self.resize(
            900,
            650
        )

        layout = QVBoxLayout(
            self
        )

        tabs = QTabWidget()

        general = QTextEdit()

        general.setReadOnly(
            True
        )

        try:

            size = os.path.getsize(
                source
            )

            mb = size / 1024 / 1024

        except Exception:

            mb = 0

        general.setHtml(
            f"""
            <h2>{Path(source).name}</h2>

            <p><b>Path:</b> {source}</p>

            <p><b>Duration:</b>
            {format_time(player.duration())}</p>

            <p><b>Current position:</b>
            {format_time(player.position())}</p>

            <p><b>File size:</b>
            {mb:.2f} MB</p>

            <p><b>Extension:</b>
            {Path(source).suffix.upper()}</p>
            """
        )

        tabs.addTab(
            general,
            "General"
        )

        probe = QTextEdit()

        probe.setReadOnly(
            True
        )

        executable = ffprobe()

        if executable:

            try:

                result = subprocess.run(
                    [
                        executable,
                        "-hide_banner",
                        source
                    ],
                    capture_output=True,
                    text=True,
                    errors="replace"
                )

                probe.setPlainText(
                    result.stderr
                )

            except Exception as e:

                probe.setPlainText(
                    str(e)
                )

        else:

            probe.setPlainText(
                "FFprobe is not available."
            )

        tabs.addTab(
            probe,
            "FFprobe"
        )

        layout.addWidget(
            tabs
        )

        close = QPushButton(
            "Close"
        )

        close.clicked.connect(
            self.accept
        )

        layout.addWidget(
            close
        )



# ============================================================
# ADVANCED DIALOGS
# ============================================================

class SubtitleEditorDialog(QDialog):

    changed = Signal(list)

    def __init__(self, subtitles, parent=None):
        super().__init__(parent)
        self.subtitles = [dict(x) for x in subtitles]
        self.setWindowTitle("Subtitle Editor")
        self.resize(1050, 680)

        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        title = QLabel("Subtitle Editor")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        top.addWidget(title)
        top.addStretch()

        add = QPushButton("+ Add")
        delete = QPushButton("Delete")
        shift = QPushButton("Shift All")
        top.addWidget(add)
        top.addWidget(delete)
        top.addWidget(shift)
        layout.addLayout(top)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Start", "End", "Text"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        layout.addWidget(self.table)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        add.clicked.connect(self.add_row)
        delete.clicked.connect(self.delete_row)
        shift.clicked.connect(self.shift_all)
        self.populate()

    def populate(self):
        self.table.setRowCount(len(self.subtitles))
        for row, item in enumerate(self.subtitles):
            self.table.setItem(row, 0, QTableWidgetItem(srt_timestamp(item["start"])))
            self.table.setItem(row, 1, QTableWidgetItem(srt_timestamp(item["end"])))
            self.table.setItem(row, 2, QTableWidgetItem(item["text"]))

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        now = 0.0
        if self.subtitles:
            now = self.subtitles[-1]["end"]
        self.table.setItem(row, 0, QTableWidgetItem(srt_timestamp(now)))
        self.table.setItem(row, 1, QTableWidgetItem(srt_timestamp(now + 2)))
        self.table.setItem(row, 2, QTableWidgetItem("New subtitle"))

    def delete_row(self):
        rows = sorted({i.row() for i in self.table.selectedItems()}, reverse=True)
        for row in rows:
            self.table.removeRow(row)

    def shift_all(self):
        value, ok = QInputDialog.getInt(
            self, "Shift subtitles", "Milliseconds (+/-):", 0, -3600000, 3600000, 100
        )
        if not ok:
            return
        for row in range(self.table.rowCount()):
            start = parse_timestamp(self.table.item(row, 0).text()) + value / 1000
            end = parse_timestamp(self.table.item(row, 1).text()) + value / 1000
            self.table.item(row, 0).setText(srt_timestamp(max(0, start)))
            self.table.item(row, 1).setText(srt_timestamp(max(0, end)))

    def save(self):
        result = []
        for row in range(self.table.rowCount()):
            try:
                start = max(0, parse_timestamp(self.table.item(row, 0).text()))
                end = max(start, parse_timestamp(self.table.item(row, 1).text()))
                text = self.table.item(row, 2).text().strip()
                result.append({"start": start, "end": end, "text": text})
            except Exception:
                continue
        self.subtitles = result
        self.changed.emit(result)
        self.accept()


class BookmarkManagerDialog(QDialog):

    jump = Signal(int)

    def __init__(self, bookmarks, parent=None):
        super().__init__(parent)
        self.bookmarks = list(bookmarks)
        self.setWindowTitle("Bookmark Manager")
        self.resize(500, 420)
        layout = QVBoxLayout(self)
        self.list = QListWidget()
        layout.addWidget(self.list)
        for pos in self.bookmarks:
            self.list.addItem(format_time(pos))
        self.list.itemDoubleClicked.connect(self.go)
        close = QPushButton("Close")
        close.clicked.connect(self.accept)
        layout.addWidget(close)

    def go(self, item):
        row = self.list.row(item)
        if 0 <= row < len(self.bookmarks):
            self.jump.emit(self.bookmarks[row])


class PlaylistManagerDialog(QDialog):

    changed = Signal(list)

    def __init__(self, paths, parent=None):
        super().__init__(parent)
        self.paths = list(paths)
        self.setWindowTitle("Playlist Manager")
        self.resize(780, 580)
        layout = QVBoxLayout(self)
        self.list = QListWidget()
        for p in self.paths:
            self.list.addItem(p)
        self.list.setDragDropMode(QAbstractItemView.InternalMove)
        layout.addWidget(self.list)
        row = QHBoxLayout()
        up = QPushButton("↑")
        down = QPushButton("↓")
        remove = QPushButton("Remove")
        row.addWidget(up)
        row.addWidget(down)
        row.addWidget(remove)
        layout.addLayout(row)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        up.clicked.connect(lambda: self.move(-1))
        down.clicked.connect(lambda: self.move(1))
        remove.clicked.connect(self.remove)

    def move(self, delta):
        row = self.list.currentRow()
        target = row + delta
        if row < 0 or target < 0 or target >= self.list.count():
            return
        item = self.list.takeItem(row)
        self.list.insertItem(target, item)
        self.list.setCurrentRow(target)

    def remove(self):
        row = self.list.currentRow()
        if row >= 0:
            self.list.takeItem(row)

    def save(self):
        self.paths = [self.list.item(i).text() for i in range(self.list.count())]
        self.changed.emit(self.paths)
        self.accept()


class SleepTimerDialog(QDialog):

    minutes_changed = Signal(int)

    def __init__(self, current=0, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sleep Timer")
        self.resize(430, 220)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Stop playback after a chosen number of minutes."))
        self.minutes = QSpinBox()
        self.minutes.setRange(0, 1440)
        self.minutes.setValue(current)
        layout.addWidget(self.minutes)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: (self.minutes_changed.emit(self.minutes.value()), self.accept()))
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class ConvertDialog(QDialog):

    def __init__(self, source, parent=None):
        super().__init__(parent)
        self.source = source
        self.setWindowTitle("Convert / Export Media")
        self.resize(560, 340)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Source:"))
        layout.addWidget(QLabel(source))
        form = QFormLayout()
        self.format = QComboBox()
        self.format.addItems(["mp4", "mkv", "webm", "mp3", "wav", "flac"])
        form.addRow("Output format:", self.format)
        self.quality = QComboBox()
        self.quality.addItems(["High", "Balanced", "Small"])
        form.addRow("Quality:", self.quality)
        layout.addLayout(form)
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        go = QPushButton("Convert")
        layout.addWidget(go)
        close = QPushButton("Close")
        layout.addWidget(close)
        go.clicked.connect(self.convert)
        close.clicked.connect(self.reject)

    def convert(self):
        exe = ffmpeg()
        if not exe:
            QMessageBox.warning(self, "FFmpeg", "ffmpeg.exe was not found in PATH.")
            return
        ext = self.format.currentText()
        quality = self.quality.currentText()
        output, _ = QFileDialog.getSaveFileName(
            self,
            "Save converted media",
            str(Path(self.source).with_suffix("." + ext)),
            f"{ext.upper()} (*.{ext})"
        )
        if not output:
            return
        if ext == "mp3":
            args = [exe, "-y", "-i", self.source, "-vn", "-c:a", "libmp3lame", "-q:a", "2", output]
        elif ext == "wav":
            args = [exe, "-y", "-i", self.source, "-vn", "-c:a", "pcm_s16le", output]
        elif ext == "flac":
            args = [exe, "-y", "-i", self.source, "-vn", "-c:a", "flac", output]
        elif ext == "webm":
            args = [exe, "-y", "-i", self.source, "-c:v", "libvpx-vp9", "-c:a", "libopus", output]
        else:
            args = [exe, "-y", "-i", self.source, "-c:v", "libx264", "-c:a", "aac", output]
            if quality == "High":
                args.insert(-1, "-crf")
                args.insert(-1, "18")
            elif quality == "Small":
                args.insert(-1, "-crf")
                args.insert(-1, "28")
        self.progress.setRange(0, 0)
        try:
            result = subprocess.run(args, capture_output=True, text=True, errors="replace")
            self.progress.setRange(0, 1)
            self.progress.setValue(1 if result.returncode == 0 else 0)
            if result.returncode == 0:
                QMessageBox.information(self, "Conversion", "Conversion completed.")
            else:
                QMessageBox.critical(self, "Conversion failed", result.stderr[-4000:])
        except Exception as e:
            QMessageBox.critical(self, "Conversion failed", str(e))


class AudioOutputDialog(QDialog):

    selected = Signal(object)

    def __init__(self, current_device, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Audio Output Device")
        self.resize(620, 260)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Choose the Windows audio output used by Nova."))
        self.combo = QComboBox()
        try:
            from PySide6.QtMultimedia import QMediaDevices
            devices = QMediaDevices.audioOutputs()
        except Exception:
            devices = []
        for device in devices:
            self.combo.addItem(device.description, device)
            if current_device and device == current_device:
                self.combo.setCurrentIndex(self.combo.count() - 1)
        layout.addWidget(self.combo)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def device(self):
        return self.combo.currentData()


class EqualizerDialog(QDialog):

    values_changed = Signal(list)

    def __init__(self, values=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("10-Band Equalizer")
        self.resize(600, 500)
        layout = QVBoxLayout(self)
        values = values or [0] * 10
        self.sliders = []
        freqs = ["31", "62", "125", "250", "500", "1k", "2k", "4k", "8k", "16k"]
        for i, freq in enumerate(freqs):
            row = QHBoxLayout()
            row.addWidget(QLabel(freq + " Hz"))
            slider = QSlider(Qt.Horizontal)
            slider.setRange(-12, 12)
            slider.setValue(values[i])
            row.addWidget(slider)
            value = QLabel(str(values[i]))
            row.addWidget(value)
            slider.valueChanged.connect(value.setNum)
            layout.addLayout(row)
            self.sliders.append(slider)
        reset = QPushButton("Reset")
        layout.addWidget(reset)
        reset.clicked.connect(lambda: [s.setValue(0) for s in self.sliders])
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def save(self):
        self.values_changed.emit([s.value() for s in self.sliders])
        self.accept()


# ============================================================
# BACKGROUND ACTIVITY LOG
# ============================================================

class BackgroundLogDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nova — Background Activity Log")
        self.setObjectName("NovaBackgroundLog")
        self.resize(900, 620)
        self.setMinimumSize(700, 460)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("Background Activity")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()

        self.autoscroll = QCheckBox("Auto-scroll")
        self.autoscroll.setChecked(True)
        header.addWidget(self.autoscroll)

        clear = QPushButton("Clear")
        clear.clicked.connect(self.clear_log)
        header.addWidget(clear)

        close = QPushButton("Close")
        close.clicked.connect(self.close)
        header.addWidget(close)

        layout.addLayout(header)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.log, 1)

    def append_line(self, line):
        self.log.append(line)
        if self.autoscroll.isChecked():
            cursor = self.log.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.log.setTextCursor(cursor)
            self.log.ensureCursorVisible()

    def clear_log(self):
        self.log.clear()


# ============================================================
# V15 PROFESSIONAL UI DIALOGS
# ============================================================

class CommandPaletteDialog(QDialog):
    def __init__(self, actions, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nova Command Palette")
        self.setModal(True)
        self.setMinimumSize(720, 460)
        lay = QVBoxLayout(self)
        title = QLabel("⌘  Search Nova")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        lay.addWidget(title)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Type a command, tool, or action…")
        lay.addWidget(self.search)
        self.list = QListWidget()
        lay.addWidget(self.list, 1)
        self._actions = list(actions)
        self.populate("")
        self.search.textChanged.connect(self.populate)
        self.list.itemDoubleClicked.connect(self.activate)
        self.search.returnPressed.connect(self.activate_first)
        self.list.setFocus()

    def populate(self, text):
        q = text.lower().strip()
        self.list.clear()
        for label, callback in self._actions:
            if not q or q in label.lower():
                it = QListWidgetItem(label)
                it.setData(Qt.ItemDataRole.UserRole, callback)
                self.list.addItem(it)
        if self.list.count():
            self.list.setCurrentRow(0)

    def activate_first(self):
        if self.list.count(): self.activate(self.list.currentItem())

    def activate(self, item):
        cb = item.data(Qt.ItemDataRole.UserRole)
        self.accept()
        if callable(cb): cb()


class VideoAdjustmentsDialog(QDialog):
    changed = Signal(dict)
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Video Adjustments")
        self.resize(560, 430)
        self.config = config
        root = QVBoxLayout(self)
        title = QLabel("🎛 Video Picture Controls")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        root.addWidget(title)
        form = QFormLayout()
        self.sliders = {}
        specs = [("Brightness", -100, 100), ("Contrast", -100, 100), ("Saturation", -100, 100), ("Hue", -180, 180), ("Sharpness", 0, 100), ("Gamma", -100, 100)]
        saved = config.get("video_adjustments", {})
        for name, lo, hi in specs:
            key = name.lower()
            sl = QSlider(Qt.Horizontal); sl.setRange(lo, hi); sl.setValue(int(saved.get(key, 0)))
            val = QLabel(str(sl.value())); sl.valueChanged.connect(lambda v, label=val: label.setText(str(v)))
            row = QHBoxLayout(); row.addWidget(sl,1); row.addWidget(val)
            holder = QWidget(); holder.setLayout(row)
            form.addRow(name, holder); self.sliders[key]=sl
        root.addLayout(form)
        note=QLabel("Picture controls are stored with the project. Real-time GPU video filtering requires a lower-level FFmpeg/libVLC video pipeline; the player keeps playback stable on Qt Multimedia.")
        note.setWordWrap(True); note.setStyleSheet(f"color:{MUTED};")
        root.addWidget(note)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.apply); buttons.rejected.connect(self.reject); root.addWidget(buttons)
    def apply(self):
        values={k: s.value() for k,s in self.sliders.items()}
        self.config["video_adjustments"]=values
        self.changed.emit(values); self.accept()


class AICommandCenterDialog(QDialog):
    def __init__(self, player, parent=None):
        super().__init__(parent or player)
        self.player=player
        self.setWindowTitle("✨ Nova AI Command Center")
        self.resize(820, 580)
        root=QVBoxLayout(self)
        title=QLabel("✨ NOVA AI"); title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold)); root.addWidget(title)
        sub=QLabel("Understand, search, summarize and transform the current media.")
        sub.setStyleSheet(f"color:{MUTED};font-size:15px;"); root.addWidget(sub)
        grid=QGridLayout(); root.addLayout(grid)
        cards=[
            ("✨ Generate AI Subtitles", player.ai_subtitles),
            ("🧾 Transcript Viewer", player.show_transcript),
            ("🧠 AI Assistant", player.show_ai_assistant),
            ("🧭 Generate Chapters", player.generate_chapters),
            ("🌐 Translate Subtitles", player.translate_subtitles),
            ("🔎 Search Transcript", player.open_transcript_search),
        ]
        for i,(label,cb) in enumerate(cards):
            b=QPushButton(label); b.setMinimumHeight(62); b.setObjectName("AI"); b.clicked.connect(cb); grid.addWidget(b,i//2,i%2)
        root.addSpacing(10)
        q=QLabel("AI workflow"); q.setObjectName("Section"); root.addWidget(q)
        self.summary=QTextEdit(); self.summary.setPlaceholderText("AI notes and transcript insights appear here…"); root.addWidget(self.summary,1)
        close=QPushButton("Close"); close.clicked.connect(self.close); root.addWidget(close)



FEATURE_MATRIX = [('Playback', 'Smart Autoplay', 'adv_smart_autoplay'),
 ('Playback', 'Auto Resume', 'adv_auto_resume'),
 ('Playback', 'Remember Last Position', 'adv_remember_last_position'),
 ('Playback', 'Auto Next', 'adv_auto_next'),
 ('Playback', 'Shuffle Playlist', 'adv_shuffle_playlist'),
 ('Playback', 'Repeat One', 'adv_repeat_one'),
 ('Playback', 'Repeat All', 'adv_repeat_all'),
 ('Playback', 'Gapless Playback', 'adv_gapless_playback'),
 ('Playback', 'Pause on Minimize', 'adv_pause_on_minimize'),
 ('Playback', 'Pause on Focus Loss', 'adv_pause_on_focus_loss'),
 ('Playback', 'Resume After Seek', 'adv_resume_after_seek'),
 ('Playback', 'Seek Preview', 'adv_seek_preview'),
 ('Playback', 'Seek 5s', 'adv_seek_5s'),
 ('Playback', 'Seek 10s', 'adv_seek_10s'),
 ('Playback', 'Seek 30s', 'adv_seek_30s'),
 ('Playback', 'Seek 60s', 'adv_seek_60s'),
 ('Playback', 'Frame Step Mode', 'adv_frame_step_mode'),
 ('Playback', 'Next Frame', 'adv_next_frame'),
 ('Playback', 'Previous Frame', 'adv_previous_frame'),
 ('Playback', 'Rate 0.25x', 'adv_rate_0.25x'),
 ('Playback', 'Rate 0.5x', 'adv_rate_0.5x'),
 ('Playback', 'Rate 0.75x', 'adv_rate_0.75x'),
 ('Playback', 'Rate 1.25x', 'adv_rate_1.25x'),
 ('Playback', 'Rate 1.5x', 'adv_rate_1.5x'),
 ('Playback', 'Rate 2x', 'adv_rate_2x'),
 ('Video', 'Auto Fit', 'adv_auto_fit'),
 ('Video', 'Fill Screen', 'adv_fill_screen'),
 ('Video', 'Zoom 100', 'adv_zoom_100'),
 ('Video', 'Zoom 125', 'adv_zoom_125'),
 ('Video', 'Zoom 150', 'adv_zoom_150'),
 ('Video', 'Zoom 200', 'adv_zoom_200'),
 ('Video', 'Pan Mode', 'adv_pan_mode'),
 ('Video', 'Rotate 90', 'adv_rotate_90'),
 ('Video', 'Rotate 180', 'adv_rotate_180'),
 ('Video', 'Rotate 270', 'adv_rotate_270'),
 ('Video', 'Mirror Horizontal', 'adv_mirror_horizontal'),
 ('Video', 'Mirror Vertical', 'adv_mirror_vertical'),
 ('Video', 'Deinterlace', 'adv_deinterlace'),
 ('Video', 'Cinematic Mode', 'adv_cinematic_mode'),
 ('Video', 'Low Latency', 'adv_low_latency'),
 ('Video', 'Frame Drop Guard', 'adv_frame_drop_guard'),
 ('Video', 'Smooth Seek', 'adv_smooth_seek'),
 ('Video', 'Seek Thumbnail', 'adv_seek_thumbnail'),
 ('Video', 'HDR Mode', 'adv_hdr_mode'),
 ('Video', 'Color Management', 'adv_color_management'),
 ('Video', 'Brightness Control', 'adv_brightness_control'),
 ('Video', 'Contrast Control', 'adv_contrast_control'),
 ('Video', 'Saturation Control', 'adv_saturation_control'),
 ('Video', 'Gamma Control', 'adv_gamma_control'),
 ('Video', 'Sharpness Control', 'adv_sharpness_control'),
 ('Audio', 'Volume Memory', 'adv_volume_memory'),
 ('Audio', 'Mute Restore', 'adv_mute_restore'),
 ('Audio', 'Loudness Normalization', 'adv_loudness_normalization'),
 ('Audio', 'Dialogue Boost', 'adv_dialogue_boost'),
 ('Audio', 'Night Mode', 'adv_night_mode'),
 ('Audio', 'Bass Boost', 'adv_bass_boost'),
 ('Audio', 'Treble Boost', 'adv_treble_boost'),
 ('Audio', 'Mono Mix', 'adv_mono_mix'),
 ('Audio', 'Stereo Width', 'adv_stereo_width'),
 ('Audio', 'Audio Delay', 'adv_audio_delay'),
 ('Audio', 'Audio Track Memory', 'adv_audio_track_memory'),
 ('Audio', 'Exclusive Output', 'adv_exclusive_output'),
 ('Audio', 'Output Device Memory', 'adv_output_device_memory'),
 ('Audio', 'Equalizer Presets', 'adv_equalizer_presets'),
 ('Audio', 'Flat EQ', 'adv_flat_eq'),
 ('Audio', 'Rock EQ', 'adv_rock_eq'),
 ('Audio', 'Pop EQ', 'adv_pop_eq'),
 ('Audio', 'Movie EQ', 'adv_movie_eq'),
 ('Audio', 'Voice EQ', 'adv_voice_eq'),
 ('Audio', 'Classical EQ', 'adv_classical_eq'),
 ('Subtitles', 'Auto Sidecar', 'adv_auto_sidecar'),
 ('Subtitles', 'Auto Detect Language', 'adv_auto_detect_language'),
 ('Subtitles', 'Subtitle Cache', 'adv_subtitle_cache'),
 ('Subtitles', 'Subtitle Delay', 'adv_subtitle_delay'),
 ('Subtitles', 'Subtitle Size', 'adv_subtitle_size'),
 ('Subtitles', 'Subtitle Outline', 'adv_subtitle_outline'),
 ('Subtitles', 'Subtitle Shadow', 'adv_subtitle_shadow'),
 ('Subtitles', 'Subtitle Background', 'adv_subtitle_background'),
 ('Subtitles', 'Dual Language', 'adv_dual_language'),
 ('Subtitles', 'Subtitle Search', 'adv_subtitle_search'),
 ('Subtitles', 'Subtitle Quick Edit', 'adv_subtitle_quick_edit'),
 ('Subtitles', 'Subtitle Shift All', 'adv_subtitle_shift_all'),
 ('Subtitles', 'Subtitle Export SRT', 'adv_subtitle_export_srt'),
 ('Subtitles', 'Subtitle Export VTT', 'adv_subtitle_export_vtt'),
 ('Subtitles', 'Subtitle Export ASS', 'adv_subtitle_export_ass'),
 ('Subtitles', 'Subtitle Repair', 'adv_subtitle_repair'),
 ('Subtitles', 'Forced Subtitle', 'adv_forced_subtitle'),
 ('Subtitles', 'Prefer External', 'adv_prefer_external'),
 ('Subtitles', 'Subtitle Safe Area', 'adv_subtitle_safe_area'),
 ('Subtitles', 'Subtitle Fade', 'adv_subtitle_fade'),
 ('AI', 'AI Subtitle Auto', 'adv_ai_subtitle_auto'),
 ('AI', 'AI Subtitle Fast Mode', 'adv_ai_subtitle_fast_mode'),
 ('AI', 'AI Subtitle High Accuracy', 'adv_ai_subtitle_high_accuracy'),
 ('AI', 'AI Language Detect', 'adv_ai_language_detect'),
 ('AI', 'AI Chapter Detect', 'adv_ai_chapter_detect'),
 ('AI', 'AI Summary', 'adv_ai_summary'),
 ('AI', 'AI Key Points', 'adv_ai_key_points'),
 ('AI', 'AI Action Items', 'adv_ai_action_items'),
 ('AI', 'AI Topic Search', 'adv_ai_topic_search'),
 ('AI', 'AI Transcript Search', 'adv_ai_transcript_search'),
 ('AI', 'AI Ask Nova', 'adv_ai_ask_nova'),
 ('AI', 'AI Speaker Labels', 'adv_ai_speaker_labels'),
 ('AI', 'AI Timestamp Answers', 'adv_ai_timestamp_answers'),
 ('AI', 'AI Translation', 'adv_ai_translation'),
 ('AI', 'AI Subtitle Repair', 'adv_ai_subtitle_repair'),
 ('AI', 'AI Scene Notes', 'adv_ai_scene_notes'),
 ('AI', 'AI Highlight Detection', 'adv_ai_highlight_detection'),
 ('AI', 'AI Sensitive Content Flag', 'adv_ai_sensitive_content_flag'),
 ('AI', 'AI Model Cache', 'adv_ai_model_cache'),
 ('AI', 'AI Job Queue', 'adv_ai_job_queue'),
 ('Library', 'Library Auto Scan', 'adv_library_auto_scan'),
 ('Library', 'Library Watch Folders', 'adv_library_watch_folders'),
 ('Library', 'Library Metadata Cache', 'adv_library_metadata_cache'),
 ('Library', 'Library Thumbnail Cache', 'adv_library_thumbnail_cache'),
 ('Library', 'Library Smart Groups', 'adv_library_smart_groups'),
 ('Library', 'Recently Added', 'adv_recently_added'),
 ('Library', 'Recently Played', 'adv_recently_played'),
 ('Library', 'Continue Watching', 'adv_continue_watching'),
 ('Library', 'Unwatched Filter', 'adv_unwatched_filter'),
 ('Library', 'Favorites Filter', 'adv_favorites_filter'),
 ('Library', 'Duplicate Detection', 'adv_duplicate_detection'),
 ('Library', 'Missing File Detection', 'adv_missing_file_detection'),
 ('Library', 'Broken File Report', 'adv_broken_file_report'),
 ('Library', 'Folder Statistics', 'adv_folder_statistics'),
 ('Library', 'Library Search', 'adv_library_search'),
 ('Playlist', 'Playlist Drag Reorder', 'adv_playlist_drag_reorder'),
 ('Playlist', 'Playlist Search', 'adv_playlist_search'),
 ('Playlist', 'Playlist Save', 'adv_playlist_save'),
 ('Playlist', 'Playlist Restore', 'adv_playlist_restore'),
 ('Playlist', 'Playlist Export', 'adv_playlist_export'),
 ('Playlist', 'Playlist Import', 'adv_playlist_import'),
 ('Playlist', 'Playlist Deduplicate', 'adv_playlist_deduplicate'),
 ('Playlist', 'Playlist Sort Name', 'adv_playlist_sort_name'),
 ('Playlist', 'Playlist Sort Date', 'adv_playlist_sort_date'),
 ('Playlist', 'Playlist Sort Duration', 'adv_playlist_sort_duration'),
 ('Capture', 'Screenshot PNG', 'adv_screenshot_png'),
 ('Capture', 'Screenshot JPEG', 'adv_screenshot_jpeg'),
 ('Capture', 'Screenshot WebP', 'adv_screenshot_webp'),
 ('Capture', 'Copy Frame Clipboard', 'adv_copy_frame_clipboard'),
 ('Capture', 'Timestamped Filenames', 'adv_timestamped_filenames'),
 ('Capture', 'Screenshot Gallery', 'adv_screenshot_gallery'),
 ('Capture', 'Burst Capture', 'adv_burst_capture'),
 ('Capture', 'Capture Original Resolution', 'adv_capture_original_resolution'),
 ('Interface', 'Glass Cards', 'adv_glass_cards'),
 ('Interface', 'Soft Shadows', 'adv_soft_shadows'),
 ('Interface', 'Compact Controls', 'adv_compact_controls'),
 ('Interface', 'Minimal Mode', 'adv_minimal_mode'),
 ('Interface', 'Cinema Mode', 'adv_cinema_mode'),
 ('Interface', 'Always On Top', 'adv_always_on_top'),
 ('Interface', 'Remember Window Size', 'adv_remember_window_size'),
 ('Interface', 'Remember Window Position', 'adv_remember_window_position'),
 ('Interface', 'Start Maximized', 'adv_start_maximized'),
 ('Interface', 'Start Fullscreen', 'adv_start_fullscreen'),
 ('Interface', 'Dark UI', 'adv_dark_ui'),
 ('Interface', 'OLED UI', 'adv_oled_ui'),
 ('Interface', 'Blue Accent', 'adv_blue_accent'),
 ('Interface', 'Purple Accent', 'adv_purple_accent'),
 ('Interface', 'Cyan Accent', 'adv_cyan_accent'),
 ('Interface', 'Green Accent', 'adv_green_accent'),
 ('Interface', 'Reduced Motion', 'adv_reduced_motion'),
 ('Interface', 'Large Text', 'adv_large_text'),
 ('Interface', 'High Contrast', 'adv_high_contrast'),
 ('Interface', 'Command Palette', 'adv_command_palette'),
 ('Advanced', 'Background Activity Log', 'adv_background_activity_log'),
 ('Advanced', 'Auto Save State', 'adv_auto_save_state'),
 ('Advanced', 'Auto Save Every 30s', 'adv_auto_save_every_30s'),
 ('Advanced', 'Debug Logging', 'adv_debug_logging'),
 ('Advanced', 'Hardware Acceleration', 'adv_hardware_acceleration'),
 ('Advanced', 'GPU Preference', 'adv_gpu_preference'),
 ('Advanced', 'CPU Safe Mode', 'adv_cpu_safe_mode'),
 ('Advanced', 'Network Cache', 'adv_network_cache'),
 ('Advanced', 'Fast Startup', 'adv_fast_startup'),
 ('Advanced', 'Single Instance', 'adv_single_instance'),
 ('Advanced', 'Crash Recovery', 'adv_crash_recovery'),
 ('Advanced', 'Local Telemetry', 'adv_local_telemetry'),
 ('Advanced', 'Error History', 'adv_error_history'),
 ('Advanced', 'Performance HUD', 'adv_performance_hud'),
 ('Advanced', 'FPS HUD', 'adv_fps_hud'),
 ('Advanced', 'Dropped Frame HUD', 'adv_dropped_frame_hud'),
 ('Advanced', 'Media Probe Cache', 'adv_media_probe_cache'),
 ('Advanced', 'FFmpeg Detection', 'adv_ffmpeg_detection'),
 ('Advanced', 'Environment Diagnostics', 'adv_environment_diagnostics'),
 ('Advanced', 'Settings Backup', 'adv_settings_backup')]
FEATURE_COUNT = len(FEATURE_MATRIX)


class AdvancedFeaturesDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle(f"Nova Advanced Feature Center — {FEATURE_COUNT} Controls")
        self.resize(1180, 820)
        self.setMinimumSize(980, 680)
        self.setStyleSheet(f"""
            QDialog {{ background: {BG}; color: {TEXT}; }}
            QScrollArea {{ background: {CARD}; border: 1px solid #28364a; border-radius: 14px; }}
            QScrollArea > QWidget > QWidget {{ background: {CARD}; }}
            QCheckBox {{ color: {TEXT}; spacing: 10px; background: transparent; padding: 8px 10px; }}
            QCheckBox:hover {{ background: #152139; border-radius: 8px; }}
            QCheckBox::indicator {{ width: 18px; height: 18px; border: 1px solid #60728f; border-radius: 5px; background: #0b1220; }}
            QCheckBox::indicator:checked {{ background: {BLUE}; border-color: {BLUE}; }}
            QLabel#FeatureCount {{ color: {MUTED}; font-size: 12px; }}
            QFrame#FeatureCard {{ background: #101827; border: 1px solid #25344a; border-radius: 10px; }}
            QFrame#FeatureCard:hover {{ border-color: #4c74b8; background: #132036; }}
        """)
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)
        title = QLabel("Nova Advanced Feature Center")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        root.addWidget(title)
        note = QLabel(f"{FEATURE_COUNT} advanced controls across playback, video, audio, subtitles, AI, library, playlist, capture, interface and diagnostics. Settings are persisted by Nova. Backend-dependent capabilities use the active Qt/FFmpeg support.")
        note.setWordWrap(True)
        note.setStyleSheet(f"color:{MUTED};")
        root.addWidget(note)
        search = QLineEdit()
        search.setPlaceholderText("Search advanced features…")
        root.addWidget(search)
        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)
        self.boxes = {}
        self.category_pages = {}
        self.category_counts = {}
        seen = set()
        for category, _label, _key in FEATURE_MATRIX:
            if category in seen:
                continue
            seen.add(category)
            page = QWidget()
            page.setStyleSheet(f"background:{CARD};")
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(14, 14, 14, 14)
            page_layout.setSpacing(10)

            items = [x for x in FEATURE_MATRIX if x[0] == category]
            header = QHBoxLayout()
            info = QLabel(f"{category} features")
            info.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            count = QLabel(f"{len(items)} controls")
            count.setObjectName("FeatureCount")
            header.addWidget(info)
            header.addStretch()
            header.addWidget(count)
            page_layout.addLayout(header)

            grid = QGridLayout()
            grid.setHorizontalSpacing(12)
            grid.setVerticalSpacing(8)
            for idx, (_cat, text, fkey) in enumerate(items):
                card = QFrame()
                card.setObjectName("FeatureCard")
                card_layout = QHBoxLayout(card)
                card_layout.setContentsMargins(8, 3, 8, 3)
                cb = QCheckBox(text)
                cb.setChecked(bool(self.config.get(fkey, False)))
                cb.setToolTip(f"Toggle {text}")
                self.boxes[fkey] = cb
                card_layout.addWidget(cb)
                grid.addWidget(card, idx // 2, idx % 2)
            page_layout.addLayout(grid)
            page_layout.addStretch(1)

            scroll = QScrollArea()
            scroll.setObjectName("AdvancedScroll")
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setWidget(page)
            self.tabs.addTab(scroll, f"{category}  ·  {len(items)}")
            self.category_pages[category] = page
            self.category_counts[category] = count
        quick = QHBoxLayout()
        current_on = QPushButton("Enable Current Category")
        current_off = QPushButton("Disable Current Category")
        quick.addWidget(current_on)
        quick.addWidget(current_off)
        quick.addStretch()
        root.addLayout(quick)

        buttons = QHBoxLayout()
        all_on = QPushButton("Enable All")
        all_off = QPushButton("Disable All")
        defaults = QPushButton("Recommended Defaults")
        save = QPushButton("Save")
        close = QPushButton("Close")
        buttons.addWidget(all_on)
        buttons.addWidget(all_off)
        buttons.addWidget(defaults)
        buttons.addStretch()
        buttons.addWidget(save)
        buttons.addWidget(close)
        root.addLayout(buttons)
        search.textChanged.connect(self._filter)
        current_on.clicked.connect(lambda: self._set_current_category(True))
        current_off.clicked.connect(lambda: self._set_current_category(False))
        all_on.clicked.connect(lambda: self._set_all(True))
        all_off.clicked.connect(lambda: self._set_all(False))
        defaults.clicked.connect(self._defaults)
        save.clicked.connect(self._save)
        close.clicked.connect(self.reject)

    def _filter(self, text):
        query = text.lower().strip()
        for cb in self.boxes.values():
            widget = cb.parentWidget()
            if widget is not None:
                widget.setVisible(not query or query in cb.text().lower())
            else:
                cb.setVisible(not query or query in cb.text().lower())

        for i in range(self.tabs.count()):
            scroll = self.tabs.widget(i)
            visible = any(
                widget.isVisible()
                for widget in self.boxes.values()
                if widget.parentWidget() is not None
                and widget.parentWidget().parentWidget() is not None
                and scroll.isAncestorOf(widget.parentWidget())
            )
            self.tabs.setTabVisible(i, visible or not query)

    def _set_current_category(self, value):
        index = self.tabs.currentIndex()
        if index < 0:
            return
        category = self.tabs.tabText(index).split("  ·  ", 1)[0]
        for cat, _label, key in FEATURE_MATRIX:
            if cat == category and key in self.boxes:
                self.boxes[key].setChecked(value)

    def _set_all(self, value):
        for cb in self.boxes.values():
            cb.setChecked(value)

    def _defaults(self):
        recommended = {
            "adv_smart_autoplay": True, "adv_auto_resume": True,
            "adv_remember_last_position": True, "adv_auto_next": True,
            "adv_smooth_seek": True, "adv_seek_preview": True,
            "adv_auto_fit": True, "adv_volume_memory": True,
            "adv_auto_sidecar": True, "adv_ai_subtitle_fast_mode": True,
            "adv_recently_played": True, "adv_continue_watching": True,
            "adv_playlist_search": True, "adv_screenshot_png": True,
            "adv_timestamped_filenames": True, "adv_glass_cards": True,
            "adv_soft_shadows": True, "adv_dark_ui": True,
            "adv_command_palette": True, "adv_background_activity_log": True,
            "adv_auto_save_state": True, "adv_hardware_acceleration": True,
            "adv_ffmpeg_detection": True, "adv_environment_diagnostics": True,
        }
        for key, cb in self.boxes.items():
            cb.setChecked(recommended.get(key, False))

    def _save(self):
        for key, cb in self.boxes.items():
            self.config[key] = cb.isChecked()
        self.accept()


# ============================================================
# INTERACTIVE VIDEO SURFACE
# ============================================================

class MediaListDialog(QDialog):
    open_requested = Signal(str)

    def __init__(self, title, paths, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(820, 620)
        root = QVBoxLayout(self)
        heading = QLabel(title)
        heading.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        root.addWidget(heading)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search…")
        root.addWidget(self.search)
        self.list = QListWidget()
        root.addWidget(self.list, 1)
        self.paths = [p for p in paths if p]
        for path in self.paths:
            item = QListWidgetItem(Path(path).name)
            item.setData(Qt.ItemDataRole.UserRole, path)
            item.setToolTip(path)
            self.list.addItem(item)
        self.search.textChanged.connect(self._filter)
        self.list.itemDoubleClicked.connect(lambda item: self._open(item))
        close = QPushButton("Close")
        close.clicked.connect(self.accept)
        root.addWidget(close)

    def _filter(self, text):
        q = text.lower().strip()
        for i in range(self.list.count()):
            item = self.list.item(i)
            item.setHidden(bool(q) and q not in item.text().lower())

    def _open(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self.open_requested.emit(path)
            self.accept()


class InteractiveVideoWidget(QVideoWidget):

    clicked = Signal()
    rightClicked = Signal(QPoint)
    resized = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            event.accept()
            return
        if event.button() == Qt.RightButton:
            self.rightClicked.emit(self.mapToGlobal(event.position().toPoint()))
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            window = self.window()
            if hasattr(window, "toggle_fullscreen"):
                window.toggle_fullscreen()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        window = self.window()
        if hasattr(window, "volume") and delta:
            step = 5 if delta > 0 else -5
            try:
                window.volume.setValue(max(0, min(100, window.volume.value() + step)))
                window.audio.setVolume(window.volume.value() / 100)
                window.status.setText(f"Volume: {window.volume.value()}%")
                event.accept()
                return
            except Exception:
                pass
        super().wheelEvent(event)



# ============================================================
# V01 FEATURE WORKSPACE
# ============================================================

class NovaLibraryDialog(QDialog):
    """Visual media library with smart collections and quick resume."""
    def __init__(self, player, parent=None):
        super().__init__(parent or player)
        self.player = player
        self.setWindowTitle("Nova Media Library")
        self.resize(1100, 720)
        self.setMinimumSize(840, 560)
        root = QVBoxLayout(self)
        header = QHBoxLayout()
        title = QLabel("MEDIA LIBRARY")
        title.setFont(QFont("Segoe UI", 23, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search files, folders and media names…")
        self.search.setMinimumWidth(340)
        header.addWidget(self.search)
        self.filter = QComboBox()
        self.filter.addItems(["All", "Continue Watching", "Favorites", "Video", "Audio", "Unwatched"])
        header.addWidget(self.filter)
        self.sort = QComboBox()
        self.sort.addItems(["Name", "Recently Played", "Progress"])
        header.addWidget(self.sort)
        root.addLayout(header)

        self.stats = QLabel()
        self.stats.setStyleSheet(f"color:{MUTED};")
        root.addWidget(self.stats)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setContentsMargins(4, 4, 4, 4)
        self.grid.setSpacing(12)
        scroll.setWidget(self.grid_host)
        root.addWidget(scroll, 1)

        footer = QHBoxLayout()
        refresh = QPushButton("↻ Refresh")
        refresh.clicked.connect(self.refresh)
        open_folder = QPushButton("＋ Add Folder")
        open_folder.clicked.connect(self.player.add_library_folder)
        footer.addWidget(refresh)
        footer.addWidget(open_folder)
        footer.addStretch()
        close = QPushButton("Close")
        close.clicked.connect(self.close)
        footer.addWidget(close)
        root.addLayout(footer)

        self.search.textChanged.connect(self.refresh)
        self.filter.currentTextChanged.connect(self.refresh)
        self.sort.currentTextChanged.connect(self.refresh)
        self.refresh()

    def _items(self):
        paths = []
        seen = set()
        # Playlist entries are already individual media files; library entries
        # are registered folders, so expand those folders into media files.
        for p in self.player.playlist_files:
            p = str(p)
            if os.path.isfile(p) and is_media(p) and p not in seen:
                paths.append(p)
                seen.add(p)
        for folder in self.player.library:
            folder = str(folder)
            if not os.path.isdir(folder):
                continue
            for root, dirs, names in os.walk(folder):
                for name in names:
                    p = os.path.abspath(os.path.join(root, name))
                    if is_media(p) and p not in seen:
                        paths.append(p)
                        seen.add(p)
                if not self.player.config.get("scan_subfolders", True):
                    dirs[:] = []
        q = self.search.text().strip().lower()
        filt = self.filter.currentText()
        if q:
            paths = [p for p in paths if q in Path(p).name.lower() or q in str(Path(p).parent).lower()]
        if filt == "Continue Watching":
            paths = [p for p in paths if int(self.player.history.get(p, 0) or 0) > 5000]
        elif filt == "Favorites":
            paths = [p for p in paths if p in self.player.favorites]
        elif filt == "Video":
            paths = [p for p in paths if Path(p).suffix.lower() not in {".mp3", ".wav", ".flac", ".aac", ".ogg", ".opus", ".m4a", ".wma"}]
        elif filt == "Audio":
            paths = [p for p in paths if Path(p).suffix.lower() in {".mp3", ".wav", ".flac", ".aac", ".ogg", ".opus", ".m4a", ".wma"}]
        elif filt == "Unwatched":
            paths = [p for p in paths if int(self.player.history.get(p, 0) or 0) <= 5000]
        if self.sort.currentText() == "Recently Played":
            paths.sort(key=lambda p: int(self.player.history.get(p, 0) or 0), reverse=True)
        elif self.sort.currentText() == "Progress":
            paths.sort(key=lambda p: int(self.player.history.get(p, 0) or 0), reverse=True)
        else:
            paths.sort(key=lambda p: Path(p).name.lower())
        return paths

    def refresh(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        paths = self._items()
        self.stats.setText(f"{len(paths)} media items  •  {len(self.player.favorites)} favorites  •  {sum(1 for p,v in self.player.history.items() if v)} resume points")
        if not paths:
            empty = QLabel("No media matches this collection.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(f"color:{MUTED};font-size:16px;padding:50px;")
            self.grid.addWidget(empty, 0, 0, 1, 4)
            return
        for i, path in enumerate(paths):
            self._add_card(path, i // 4, i % 4)

    def _find_cover(self, path):
        p = Path(path)
        candidates = [p.with_suffix(ext) for ext in (".jpg", ".jpeg", ".png", ".webp")]
        for c in candidates:
            if c.exists():
                return c
        for c in [p.parent / "folder.jpg", p.parent / "folder.png", p.parent / "cover.jpg", p.parent / "cover.png"]:
            if c.exists():
                return c
        return None

    def _add_card(self, path, row, col):
        card = QFrame()
        card.setObjectName("Card")
        card.setMinimumSize(220, 210)
        lay = QVBoxLayout(card)
        preview = QLabel()
        preview.setFixedHeight(112)
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cover = self._find_cover(path)
        if cover:
            pm = QPixmap(str(cover))
            if not pm.isNull():
                preview.setPixmap(pm.scaled(200, 108, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        if preview.pixmap() is None:
            suffix = Path(path).suffix.lower()
            glyph = "♫" if suffix in {".mp3", ".wav", ".flac", ".aac", ".ogg", ".opus", ".m4a", ".wma"} else "▶"
            preview.setText(glyph)
            preview.setStyleSheet(f"font-size:42px;color:{CYAN};background:#05070b;border-radius:12px;")
        lay.addWidget(preview)
        name = QLabel(Path(path).stem)
        name.setWordWrap(True)
        name.setToolTip(path)
        name.setStyleSheet("font-weight:700;")
        lay.addWidget(name)
        pos = int(self.player.history.get(path, 0) or 0)
        progress = QLabel(f"Resume: {format_time(pos)}" if pos > 0 else "Not played")
        progress.setStyleSheet(f"color:{MUTED};font-size:11px;")
        lay.addWidget(progress)
        buttons = QHBoxLayout()
        play = QPushButton("▶ Play")
        play.clicked.connect(lambda _=False, p=path: (self.player.add_files([p]), self.player.play_file(p), self.player.show_player(), self.close()))
        buttons.addWidget(play)
        fav = QPushButton("★" if path in self.player.favorites else "☆")
        fav.setFixedWidth(42)
        def toggle():
            self.player.current_source = path
            self.player.toggle_favorite()
            self.refresh()
        fav.clicked.connect(toggle)
        buttons.addWidget(fav)
        info = QPushButton("Info")
        info.clicked.connect(lambda _=False, p=path: self._show_info(p))
        buttons.addWidget(info)
        lay.addLayout(buttons)
        self.grid.addWidget(card, row, col)

    def _show_info(self, path):
        old = self.player.current_source
        try:
            self.player.current_source = path
            self.player.show_media_info()
        finally:
            self.player.current_source = old


class NovaUniversalSearchDialog(QDialog):
    """Search media, transcript, bookmarks, favorites and library in one place."""
    def __init__(self, player, parent=None):
        super().__init__(parent or player)
        self.player = player
        self.setWindowTitle("Nova Universal Search")
        self.resize(900, 620)
        root = QVBoxLayout(self)
        title = QLabel("UNIVERSAL SEARCH")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        root.addWidget(title)
        self.query = QLineEdit()
        self.query.setPlaceholderText("Search media, transcript text, bookmarks or folders…")
        root.addWidget(self.query)
        self.scope = QComboBox()
        self.scope.addItems(["Everything", "Media", "Transcript", "Bookmarks", "Favorites"])
        root.addWidget(self.scope)
        self.results = QListWidget()
        root.addWidget(self.results, 1)
        close = QPushButton("Close")
        close.clicked.connect(self.close)
        root.addWidget(close)
        self.query.textChanged.connect(self.refresh)
        self.scope.currentTextChanged.connect(self.refresh)
        self.results.itemDoubleClicked.connect(self.open_result)
        self.refresh()

    def refresh(self):
        self.results.clear()
        q = self.query.text().strip().lower()
        scope = self.scope.currentText()
        if not q:
            self.results.addItem("Type to search Nova…")
            return
        added = 0
        paths = []
        seen = set()
        for p in self.player.playlist_files:
            p = str(p)
            if os.path.isfile(p) and p not in seen:
                paths.append(p); seen.add(p)
        for folder in self.player.library:
            folder = str(folder)
            if not os.path.isdir(folder):
                continue
            for root, dirs, names in os.walk(folder):
                for name in names:
                    p = os.path.abspath(os.path.join(root, name))
                    if is_media(p) and p not in seen:
                        paths.append(p); seen.add(p)
                if not self.player.config.get("scan_subfolders", True):
                    dirs[:] = []
        if scope in ("Everything", "Media"):
            for p in paths:
                if q in Path(p).name.lower() or q in str(Path(p).parent).lower():
                    it = QListWidgetItem(f"🎬 MEDIA   {Path(p).name}  —  {Path(p).parent}")
                    it.setData(Qt.ItemDataRole.UserRole, ("media", p))
                    self.results.addItem(it); added += 1
        if scope in ("Everything", "Favorites"):
            for p in self.player.favorites:
                if q in Path(p).name.lower():
                    it = QListWidgetItem(f"★ FAVORITE   {Path(p).name}")
                    it.setData(Qt.ItemDataRole.UserRole, ("media", p))
                    self.results.addItem(it); added += 1
        if scope in ("Everything", "Bookmarks"):
            for p, marks in self.player.bookmarks.items():
                if q in Path(p).name.lower():
                    for mark in marks:
                        it = QListWidgetItem(f"🔖 BOOKMARK   {Path(p).name}  —  {format_time(mark)}")
                        it.setData(Qt.ItemDataRole.UserRole, ("bookmark", p, int(mark)))
                        self.results.addItem(it); added += 1
        if scope in ("Everything", "Transcript") and self.player.transcript:
            for s in self.player.transcript:
                txt = str(s.get("text", ""))
                if q in txt.lower():
                    it = QListWidgetItem(f"🧾 TRANSCRIPT   [{format_time(int(float(s.get('start',0))*1000))}] {txt}")
                    it.setData(Qt.ItemDataRole.UserRole, ("timestamp", int(float(s.get("start", 0))*1000)))
                    self.results.addItem(it); added += 1
        if not added:
            self.results.addItem("No matching results.")

    def open_result(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
        if data[0] == "media":
            self.player.add_files([data[1]])
            self.player.play_file(data[1])
            self.player.show_player()
            self.close()
        elif data[0] == "bookmark":
            self.player.add_files([data[1]])
            self.player.play_file(data[1])
            QTimer.singleShot(300, lambda: self.player.player.setPosition(data[2]))
            self.close()
        elif data[0] == "timestamp":
            self.player.player.setPosition(data[1])
            self.player.show_player()
            self.close()


class NovaSubtitleCenterDialog(QDialog):
    """One place for subtitle tracks, timing and appearance controls."""
    def __init__(self, player, parent=None):
        super().__init__(parent or player)
        self.player = player
        self.setWindowTitle("Nova Subtitle Center")
        self.resize(760, 620)
        root = QVBoxLayout(self)
        title = QLabel("SUBTITLE CENTER")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        root.addWidget(title)
        current = QLabel(f"Current media: {Path(player.current_source).name if player.current_source else 'None'}")
        current.setStyleSheet(f"color:{MUTED};")
        root.addWidget(current)
        tabs = QTabWidget()
        timing = QWidget(); tl = QFormLayout(timing)
        self.delay = QSpinBox(); self.delay.setRange(-60000,60000); self.delay.setSingleStep(50); self.delay.setValue(int(player.config.get("subtitle_delay",0)))
        self.size = QSpinBox(); self.size.setRange(10,72); self.size.setValue(int(player.config.get("subtitle_size",18)))
        self.font = QComboBox(); self.font.addItems(["Segoe UI","Arial","Verdana","Tahoma","Georgia","Consolas"])
        self.outline = QCheckBox(); self.outline.setChecked(True)
        tl.addRow("Delay (ms):", self.delay); tl.addRow("Font size:", self.size); tl.addRow("Font:", self.font); tl.addRow("Outline/shadow:", self.outline)
        tabs.addTab(timing,"Appearance & Timing")
        track = QWidget(); tr = QVBoxLayout(track)
        self.track_info = QListWidget()
        if player.current_subtitles:
            for i,s in enumerate(player.current_subtitles):
                self.track_info.addItem(f"{i+1:03}  [{format_time(int(float(s.get('start',0))*1000))}]  {s.get('text','')}")
        else:
            self.track_info.addItem("No external subtitles loaded. Use Load Subtitle below.")
        tr.addWidget(self.track_info,1)
        row = QHBoxLayout()
        load = QPushButton("Load Subtitle"); load.clicked.connect(player.load_subtitle)
        side = QPushButton("Load Sidecar"); side.clicked.connect(player.load_sidecar_subtitle)
        remove = QPushButton("Remove"); remove.clicked.connect(player.remove_subtitle)
        row.addWidget(load); row.addWidget(side); row.addWidget(remove); tr.addLayout(row)
        tabs.addTab(track,"Tracks")
        trans = QWidget(); transl = QVBoxLayout(trans)
        label = QLabel("AI translation uses the existing Nova online AI settings.")
        label.setWordWrap(True); label.setStyleSheet(f"color:{MUTED};")
        transl.addWidget(label)
        translate = QPushButton("🌐 Translate Current Transcript")
        translate.clicked.connect(player.translate_subtitles)
        transl.addWidget(translate)
        transl.addStretch()
        tabs.addTab(trans,"Translation")
        root.addWidget(tabs,1)
        buttons = QHBoxLayout()
        apply = QPushButton("Apply")
        apply.clicked.connect(self.apply)
        buttons.addWidget(apply); buttons.addStretch()
        close = QPushButton("Close"); close.clicked.connect(self.close); buttons.addWidget(close)
        root.addLayout(buttons)

    def apply(self):
        self.player.config["subtitle_delay"] = int(self.delay.value())
        self.player.config["subtitle_size"] = int(self.size.value())
        write_json(CONFIG_FILE, self.player.config)
        self.player.update_subtitle(self.player.player.position())
        self.player.status.setText("Subtitle settings applied.")


class NovaIntelligenceDialog(QDialog):
    """Unified AI workspace for the existing local and online intelligence tools."""
    def __init__(self, player, parent=None):
        super().__init__(parent or player)
        self.player = player
        self.setWindowTitle("Nova Intelligence")
        self.resize(900, 640)
        root = QVBoxLayout(self)
        title = QLabel("NOVA INTELLIGENCE")
        title.setFont(QFont("Segoe UI", 23, QFont.Weight.Bold))
        root.addWidget(title)
        sub = QLabel("Understand, search, summarize and transform the current media.")
        sub.setStyleSheet(f"color:{MUTED};")
        root.addWidget(sub)
        grid = QGridLayout(); root.addLayout(grid)
        actions = [
            ("✨ Generate AI Subtitles", player.ai_subtitles),
            ("🧾 Transcript Viewer", player.show_transcript),
            ("🧠 Ask Nova", player.show_ai_assistant),
            ("🧭 Generate Chapters", player.generate_chapters),
            ("🌐 Translate", player.translate_subtitles),
            ("🔎 Search Transcript", player.open_transcript_search),
        ]
        for i,(label,cb) in enumerate(actions):
            b=QPushButton(label); b.setObjectName("AI"); b.setMinimumHeight(64); b.clicked.connect(cb); grid.addWidget(b,i//2,i%2)
        tabs=QTabWidget(); root.addWidget(tabs,1)
        summary=QTextEdit(); summary.setReadOnly(False); summary.setPlaceholderText("Write notes about this video, or paste AI output here…")
        tabs.addTab(summary,"Notes / Summary")
        transcript=QTextEdit(); transcript.setReadOnly(True); transcript.setPlainText("\n".join(f"[{format_time(int(s.get('start',0)*1000))}] {s.get('text','')}" for s in player.transcript) if player.transcript else "Generate a transcript to populate this view.")
        tabs.addTab(transcript,"Transcript")
        close=QPushButton("Close"); close.clicked.connect(self.close); root.addWidget(close)


class NovaTaskCenterDialog(QDialog):
    def __init__(self, player, parent=None):
        super().__init__(parent or player)
        self.player = player
        self.setWindowTitle("Nova Task Center")
        self.resize(760, 480)
        root=QVBoxLayout(self)
        title=QLabel("BACKGROUND TASK CENTER"); title.setFont(QFont("Segoe UI",22,QFont.Weight.Bold)); root.addWidget(title)
        self.list=QListWidget(); root.addWidget(self.list,1)
        row=QHBoxLayout(); refresh=QPushButton("↻ Refresh"); refresh.clicked.connect(self.refresh); row.addWidget(refresh); row.addStretch(); close=QPushButton("Close"); close.clicked.connect(self.close); row.addWidget(close); root.addLayout(row)
        self.refresh()
        self._timer=QTimer(self); self._timer.timeout.connect(self.refresh); self._timer.start(1000)

    def refresh(self):
        self.list.clear()
        tasks=getattr(self.player,"_v30_tasks",[])
        if not tasks:
            self.list.addItem("No background tasks are running.")
            return
        for t in tasks:
            self.list.addItem(f"{t.get('status','RUNNING'):10}  {t.get('name','Task')}  {t.get('detail','')}")


class NovaNowPlayingDialog(QDialog):
    def __init__(self, player, parent=None):
        super().__init__(parent or player)
        self.player=player; self.setWindowTitle("Nova — Now Playing"); self.resize(680,520)
        root=QVBoxLayout(self)
        title=QLabel("NOW PLAYING"); title.setFont(QFont("Segoe UI",22,QFont.Weight.Bold)); root.addWidget(title)
        self.details=QTextEdit(); self.details.setReadOnly(True); root.addWidget(self.details,1)
        close=QPushButton("Close"); close.clicked.connect(self.close); root.addWidget(close)
        self.refresh()
    def refresh(self):
        p=self.player.current_source
        if not p:
            self.details.setPlainText("No media is currently loaded."); return
        try: size=os.path.getsize(p)/1024/1024
        except Exception: size=0
        dur=self.player.player.duration(); pos=self.player.player.position()
        ext=Path(p).suffix.upper()
        favorite="Yes" if p in self.player.favorites else "No"
        text=(f"Title: {Path(p).stem}\n\nPath: {p}\n\nFormat: {ext}\n"
              f"File size: {size:.2f} MB\n\nPosition: {format_time(pos)} / {format_time(dur)}\n"
              f"Playback speed: {self.player.speed.currentText()}\n\nFavorite: {favorite}\n"
              f"Subtitles loaded: {len(self.player.current_subtitles)}\n"
              f"Transcript segments: {len(self.player.transcript)}\n"
              f"Bookmarks: {len(self.player.bookmarks.get(p,[]))}")
        self.details.setPlainText(text)


class NovaSessionRecoveryDialog(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session=session; self.restore_requested=False
        self.setWindowTitle("Nova Session Recovery"); self.resize(620,300)
        root=QVBoxLayout(self)
        title=QLabel("Resume Previous Session?"); title.setFont(QFont("Segoe UI",22,QFont.Weight.Bold)); root.addWidget(title)
        src=session.get("current_source","")
        info=QLabel(f"Nova found an unfinished session.\n\nMedia: {Path(src).name if src else 'No media'}\nPosition: {format_time(int(session.get('position',0) or 0))}\nPlaylist items: {len(session.get('playlist',[]))}")
        info.setWordWrap(True); root.addWidget(info)
        row=QHBoxLayout(); yes=QPushButton("Restore Session"); no=QPushButton("Start Fresh")
        yes.clicked.connect(self._restore); no.clicked.connect(self.reject); row.addWidget(yes); row.addWidget(no); root.addLayout(row)
    def _restore(self): self.restore_requested=True; self.accept()


class MiniPlayerWindow(QWidget):
    closed = Signal()
    def __init__(self, player, video, parent=None):
        super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowTitleHint)
        self.player=player; self.video=video
        self.setWindowTitle("Nova Mini Player")
        self.setWindowIcon(QIcon(str(ICON_FILE)) if ICON_FILE.exists() else QIcon())
        self.resize(640,420); self.setMinimumSize(360,260)
        root=QVBoxLayout(self); root.setContentsMargins(4,4,4,4); root.setSpacing(4)
        root.addWidget(video,1)
        row=QHBoxLayout()
        for label, cb in [("⏮",player.previous),("▶ / Ⅱ",player.toggle_play),("⏭",player.next)]:
            b=QPushButton(label); b.setObjectName("CinemaControl"); b.clicked.connect(cb); row.addWidget(b)
        back=QPushButton("−5s"); back.clicked.connect(lambda:player.seek_relative(-5000)); row.addWidget(back)
        fwd=QPushButton("+5s"); fwd.clicked.connect(lambda:player.seek_relative(5000)); row.addWidget(fwd)
        full=QPushButton("⛶"); full.clicked.connect(self._fullscreen); row.addWidget(full)
        close=QPushButton("Restore"); close.clicked.connect(self.close); row.addWidget(close)
        root.addLayout(row)
    def _fullscreen(self): self.player.toggle_fullscreen()
    def closeEvent(self,event):
        self.closed.emit(); event.accept()


# ============================================================
# NOVA PLAYER
# ============================================================

class NovaPlayer(QMainWindow):

    def __init__(
        self
    ):

        super().__init__()

        # Apply the Nova icon to the main window.
        if ICON_FILE.exists():
            self.setWindowIcon(QIcon(str(ICON_FILE)))

        # ----------------------------------------------------
        # BORDERLESS MODERN WINDOW
        # ----------------------------------------------------

        # Start inside the usable desktop area instead of assuming every
        # monitor can display a 1560x920 window. This prevents the timeline,
        # controls and lower status area from opening below the taskbar on
        # 1366x768/High-DPI laptop screens.
        self.setMinimumSize(980, 620)
        screen = QApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            start_w = min(1560, max(980, int(available.width() * 0.90)))
            start_h = min(920, max(620, int(available.height() * 0.86)))
            self.resize(start_w, start_h)
            self.move(
                available.x() + max(0, (available.width() - start_w) // 2),
                available.y() + max(0, (available.height() - start_h) // 2),
            )
        else:
            self.resize(1360, 820)

        self.setAcceptDrops(
            True
        )

        # ----------------------------------------------------
        # DATA
        # ----------------------------------------------------

        self.config = read_json(
            CONFIG_FILE,
            {
                "volume": 75,
                "speed": 1.0,
                "autoplay": True,
                "remember_position": True,
                "loop": False,
                "seek_seconds": 5,
                "show_sidebar": True,
                "compact_controls": False,
                "animations": True,
                "subtitle_size": 18,
                "subtitle_delay": 0,
                "normalization": False,
                "ai_model": "base",
                "ai_device": "auto",
                "openai_model": "",
                "openai_api_key": "",
                "scan_subfolders": True,
                "auto_library": False,
                "debug": False,
                "hardware_acceleration": True,
                "theme": "Nova Dark",
                "accent": "blue",
                "repeat_mode": "Off",
                "video_adjustments": {},
                "network_history": [],
                "ui_style": "Nova Futuristic",
                "cinema_controls": True,
                "compact_header": False,
                "performance_mode": True,
                "seek_resume_delay_ms": 300
            }
        )

        self.history = read_json(
            HISTORY_FILE,
            {}
        )

        self.bookmarks = read_json(
            BOOKMARK_FILE,
            {}
        )

        self.library = read_json(
            LIBRARY_FILE,
            []
        )

        self.playlist_files = read_json(
            PLAYLIST_FILE,
            []
        )

        self.playlist_files = [
            p
            for p in self.playlist_files
            if os.path.exists(p)
        ]

        self.current_source = ""

        self.current_index = -1

        self.transcript = []

        self.current_subtitles = []

        self.ab_start = None
        self.ab_end = None

        # Smooth seeking / startup performance state.
        self._was_playing_before_seek = False
        self._seek_target = 0
        self._seek_resume_timer = None
        self._seek_generation = 0
        self._pending_autoplay = False
        self._pending_start_position = 0
        self._pending_source = ""
        self._last_ui_position = -1000
        self._subtitle_starts = []
        self._subtitle_cache_id = 0
        self._subtitle_cache_len = -1
        self._subtitle_last_index = -2
        self._subtitle_last_text = None
        self._subtitle_style_size = None

        # Fullscreen / interactive-video state.
        self._fullscreen_ui_state = None
        self._video_context_menu = None

        self.favorites = set(
            read_json(
                APP_DATA / "favorites.json",
                []
            )
        )

        self.sleep_timer = None

        self.eq_values = [0] * 10
        self._timeline_preview = None
        self._palette_dialog = None
        self.advanced_features = {k: bool(self.config.get(k, False)) for _c, _n, k in FEATURE_MATRIX}

        self.sidebar_buttons = []

        # Background activity / window management
        self._background_log_lines = []
        self._background_log_dialog = None
        self._open_dialogs = []
        self._ai_job_started_at = None
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

        # ----------------------------------------------------
        # MEDIA
        # ----------------------------------------------------

        self.player = QMediaPlayer(
            self
        )

        self.audio = QAudioOutput(
            self
        )

        self.player.setAudioOutput(
            self.audio
        )

        self.video = InteractiveVideoWidget()
        self.video.setObjectName("VideoSurface")
        self._timeline_preview = QLabel(self.video)
        self._timeline_preview.hide()
        self._timeline_preview.setObjectName("TimelinePreview")
        self._timeline_preview.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # Fullscreen subtitle overlay is a separate transparent top-level tool
        # window. QVideoWidget can be backed by a native video surface on
        # Windows, which can paint over ordinary child/sibling QLabel widgets.
        # A top-level click-through tool window sits above that native surface.
        self._fullscreen_subtitle = QLabel(
            None,
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self._fullscreen_subtitle.setObjectName("FullscreenSubtitle")
        self._fullscreen_subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self._fullscreen_subtitle.setWordWrap(True)
        self._fullscreen_subtitle.setTextFormat(Qt.TextFormat.PlainText)
        self._fullscreen_subtitle.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True
        )
        self._fullscreen_subtitle.setAttribute(
            Qt.WidgetAttribute.WA_ShowWithoutActivating,
            True
        )
        self._fullscreen_subtitle.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            True
        )
        self._fullscreen_subtitle.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )
        try:
            self._fullscreen_subtitle.setWindowFlag(
                Qt.WindowType.WindowTransparentForInput,
                True
            )
        except Exception:
            pass
        self._fullscreen_subtitle.setText("")
        self._fullscreen_subtitle.hide()

        self.player.setVideoOutput(
            self.video
        )
        self.video.resized.connect(self._position_fullscreen_subtitle)

        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

        self.build_ui()

        self.build_menu()

        self.connect_signals()

        self.setup_timer()

        self.restore_settings()

        self.setup_extra_features()

        # V01 productivity/media-workspace features
        self._init_v30_features()

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        outer = QWidget()

        outer.setObjectName(
            "Window"
        )

        self.setCentralWidget(
            outer
        )

        outer_layout = QVBoxLayout(
            outer
        )

        outer_layout.setContentsMargins(
            1,
            1,
            1,
            1
        )

        outer_layout.setSpacing(
            0
        )

        # Native Windows frame is intentionally used so Windows 10/11
        # resizing, snapping, maximize and minimize work normally.

        # BODY

        body = QHBoxLayout()

        body.setContentsMargins(
            0,
            0,
            0,
            0
        )

        body.setSpacing(
            0
        )

        outer_layout.addLayout(
            body,
            1
        )

        # SIDEBAR

        self.sidebar = QFrame()

        self.sidebar.setObjectName(
            "Sidebar"
        )

        self.sidebar.setFixedWidth(
            230
        )

        side_layout = QVBoxLayout(
            self.sidebar
        )

        side_layout.setContentsMargins(
            12,
            18,
            12,
            15
        )

        side_layout.setSpacing(
            6
        )

        brand = QLabel(
            "NOVA"
        )

        brand.setFont(
            QFont(
                "Segoe UI",
                18,
                QFont.Weight.Bold
            )
        )

        brand.setStyleSheet(
            f"color:{CYAN};"
        )

        side_layout.addWidget(
            brand
        )

        tagline = QLabel(
            "AI MEDIA EXPERIENCE"
        )

        tagline.setStyleSheet(
            f"""
            color:{MUTED};
            font-size:9px;
            font-weight:800;
            """
        )

        side_layout.addWidget(
            tagline
        )

        side_layout.addSpacing(
            18
        )

        self.add_nav(
            "⌂  Home",
            self.show_home
        )

        self.add_nav(
            "▶  Player",
            self.show_player
        )

        self.add_nav(
            "☰  Playlist",
            self.focus_playlist
        )

        self.add_nav(
            "▤  Transcript",
            self.show_transcript
        )

        self.add_nav(
            "✨  AI Assistant",
            self.show_ai_assistant
        )

        self.add_nav(
            "📚  Library",
            self.show_library
        )

        side_layout.addSpacing(
            15
        )

        side_layout.addWidget(
            self.section_label(
                "TOOLS"
            )
        )

        self.add_nav(
            "📷  Screenshot",
            self.screenshot
        )

        self.add_nav(
            "🔖  Bookmarks",
            self.show_bookmarks
        )

        self.add_nav(
            "ℹ  Media Info",
            self.show_media_info
        )

        self.add_nav(
            "★  Favorites",
            self.show_favorites
        )

        side_layout.addStretch()

        settings_button = self.add_nav(
            "⚙  Settings",
            self.show_settings
        )

        body.addWidget(
            self.sidebar
        )
        # Clean cinema player: keep navigation commands in menus/dialogs,
        # but remove the permanent left navigation rail.
        self.sidebar.hide()

        # MAIN

        self.main_stack = QStackedWidget()

        body.addWidget(
            self.main_stack,
            1
        )

        # pages

        self.player_page = self.create_player_page()

        self.home_page = self.create_home_page()

        self.library_page = self.create_library_page()

        self.main_stack.addWidget(
            self.player_page
        )

        self.main_stack.addWidget(
            self.home_page
        )

        self.main_stack.addWidget(
            self.library_page
        )

        self.main_stack.setCurrentWidget(
            self.player_page
        )


    def resizeEvent(self, event):
        """Keep the cinema UI readable at narrow widths and high-DPI scales."""
        super().resizeEvent(event)
        try:
            compact = self.width() < 1180
            if hasattr(self, "_transport_layout"):
                self._transport_layout.setSpacing(5 if compact else 7)
            if hasattr(self, "_actions_layout"):
                self._actions_layout.setSpacing(5 if compact else 7)
            if hasattr(self, "ai_main"):
                self.ai_main.setMinimumWidth(138 if compact else 150)
            if hasattr(self, "subtitle_label"):
                self.subtitle_label.setMaximumHeight(54 if compact else 66)
            if self.isFullScreen() and hasattr(self, "_fullscreen_subtitle"):
                self._position_fullscreen_subtitle()
        except Exception:
            pass

    # ========================================================
    # NAV
    # ========================================================

    def add_nav(
        self,
        text,
        callback
    ):

        button = QPushButton(
            text
        )

        button.setObjectName(
            "Nav"
        )

        button.clicked.connect(
            callback
        )

        self.sidebar_buttons.append(
            button
        )

        self.sidebar.layout().addWidget(
            button
        )

        return button

    def section_label(
        self,
        text
    ):

        label = QLabel(
            text
        )

        label.setObjectName(
            "Section"
        )

        return label

    # ========================================================
    # HOME
    # ========================================================

    def create_home_page(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            26,
            25,
            26,
            24
        )

        layout.setSpacing(
            20
        )

        title = QLabel(
            "Good to see you."
        )

        title.setObjectName(
            "PageTitle"
        )

        layout.addWidget(
            title
        )

        subtitle = QLabel(
            "Your intelligent media workspace."
        )

        subtitle.setStyleSheet(
            f"color:{MUTED};font-size:15px;"
        )

        layout.addWidget(
            subtitle
        )

        cards = QGridLayout()

        cards.setSpacing(
            14
        )

        self.home_cards = []

        values = [
            (
                "MEDIA",
                "0",
                "Open files"
            ),
            (
                "PLAYLIST",
                "0",
                "Queued items"
            ),
            (
                "AI",
                "READY",
                "Local transcription"
            ),
            (
                "LIBRARY",
                "0",
                "Folders"
            ),
        ]

        for row, col, data in [
            (0, 0, values[0]),
            (0, 1, values[1]),
            (1, 0, values[2]),
            (1, 1, values[3]),
        ]:

            card = QFrame()

            card.setObjectName(
                "Card"
            )

            card_layout = QVBoxLayout(
                card
            )

            small = QLabel(
                data[0]
            )

            small.setObjectName(
                "Section"
            )

            number = QLabel(
                data[1]
            )

            number.setFont(
                QFont(
                    "Segoe UI",
                    25,
                    QFont.Weight.Bold
                )
            )

            desc = QLabel(
                data[2]
            )

            desc.setStyleSheet(
                f"color:{MUTED};"
            )

            card_layout.addWidget(
                small
            )

            card_layout.addWidget(
                number
            )

            card_layout.addWidget(
                desc
            )

            cards.addWidget(
                card,
                row,
                col
            )

            self.home_cards.append(
                number
            )

        layout.addLayout(
            cards
        )

        recent_card = QFrame()

        recent_card.setObjectName(
            "Card"
        )

        recent_layout = QVBoxLayout(
            recent_card
        )

        recent_layout.addWidget(
            self.section_label(
                "RECENT MEDIA"
            )
        )

        self.recent_list = QListWidget()

        recent_layout.addWidget(
            self.recent_list
        )

        layout.addWidget(
            recent_card,
            1
        )

        open_button = QPushButton(
            "＋ Open Media"
        )

        open_button.clicked.connect(
            self.open_files
        )

        layout.addWidget(
            open_button
        )

        return page

    # ========================================================
    # PLAYER PAGE
    # ========================================================

    def create_player_page(
        self
    ):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            18,
            14,
            18,
            14
        )

        layout.setSpacing(
            12
        )

        # NOVA CINEMA HEADER
        # The header is deliberately split into two rows so the title, status
        # badges and AI action remain visible on 125%-200% Windows scaling and
        # on smaller laptop displays instead of being squeezed out of the row.
        chrome = QFrame()
        chrome.setObjectName("NovaChrome")
        chrome_layout = QVBoxLayout(chrome)
        chrome_layout.setContentsMargins(16, 9, 16, 9)
        chrome_layout.setSpacing(6)

        header_top = QHBoxLayout()
        header_top.setSpacing(12)

        brand_box = QVBoxLayout()
        brand_box.setSpacing(0)
        brand = QLabel("NOVA")
        brand.setObjectName("NovaBrand")
        brand_sub = QLabel("AI MEDIA EXPERIENCE")
        brand_sub.setObjectName("NovaBrandAccent")
        brand_box.addWidget(brand)
        brand_box.addWidget(brand_sub)
        header_top.addLayout(brand_box)

        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        self.page_title = QLabel("Cinema")
        self.page_title.setObjectName("NowPlayingLarge")
        self.now_playing = QLabel("Nothing playing")
        self.now_playing.setObjectName("NowPlaying")
        self.now_playing.setMinimumWidth(120)
        self.now_playing.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        title_box.addWidget(self.page_title)
        title_box.addWidget(self.now_playing)
        header_top.addLayout(title_box, 1)
        chrome_layout.addLayout(header_top)

        header_bottom = QHBoxLayout()
        header_bottom.setSpacing(8)

        cinema = QLabel("CINEMA MODE")
        cinema.setObjectName("CinemaPill")
        self._cinema_badge = cinema
        header_bottom.addWidget(cinema)

        self.format_badge = QLabel("NO MEDIA")
        self.format_badge.setObjectName("Badge")
        header_bottom.addWidget(self.format_badge)

        self.ai_badge = QLabel("AI READY")
        self.ai_badge.setObjectName("Badge")
        header_bottom.addWidget(self.ai_badge)

        header_bottom.addStretch(1)

        self.ai_main = QPushButton("✨  AI SUBTITLES")
        self.ai_main.setObjectName("AI")
        self.ai_main.setMinimumHeight(42)
        self.ai_main.setMinimumWidth(150)
        header_bottom.addWidget(self.ai_main)

        chrome_layout.addLayout(header_bottom)

        self._player_header_widgets = [
            chrome, self.page_title, self.now_playing,
            self.format_badge, self.ai_badge, self.ai_main,
        ]

        shadow = QGraphicsDropShadowEffect(chrome)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 7)
        shadow.setColor(QColor(0, 0, 0, 160))
        chrome.setGraphicsEffect(shadow)

        layout.addWidget(chrome, 0)

        # VIDEO / QUEUE

        splitter = QSplitter(
            Qt.Horizontal
        )
        self._splitter = splitter

        # video

        video_side = QWidget()
        self._video_side = video_side

        video_layout = QVBoxLayout(
            video_side
        )

        video_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.video_card = QFrame()

        self.video_card.setObjectName(
            "CinemaVideoShell"
        )

        video_card_layout = QVBoxLayout(
            self.video_card
        )

        video_card_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        # Do not attach a QGraphicsDropShadowEffect to the widget containing
        # QVideoWidget. On Windows this can force expensive off-screen
        # composition/repaints and is a common source of first-frame stutter.
        # The video shell keeps its border/rounded styling without a live effect.
        self.video_card.setGraphicsEffect(None)

        video_card_layout.addWidget(
            self.video
        )

        video_layout.addWidget(
            self.video_card,
            1
        )

        # subtitle

        self.subtitle_label = QLabel()

        self.subtitle_label.setObjectName(
            "Subtitle"
        )

        self.subtitle_label.setAlignment(
            Qt.AlignCenter
        )

        self.subtitle_label.setWordWrap(
            True
        )

        self.subtitle_label.setMinimumHeight(36)
        self.subtitle_label.setMaximumHeight(66)
        self.subtitle_label.setWordWrap(True)

        video_layout.addWidget(
            self.subtitle_label
        )

        # status

        status_row = QHBoxLayout()

        self.status = QLabel(
            "Open a file or drag media here."
        )

        self.status.setStyleSheet(
            f"color:{MUTED};"
        )

        status_row.addWidget(
            self.status,
            1
        )

        status_row.addWidget(
            self.section_label(
                "◉ READY"
            )
        )

        video_layout.addLayout(
            status_row
        )

        self._status_row = status_row
        self._status_ready_label = status_row.itemAt(1).widget()

        splitter.addWidget(
            video_side
        )

        # queue

        queue = QFrame()
        self._queue_panel = queue

        queue.setObjectName(
            "Card"
        )

        queue_layout = QVBoxLayout(
            queue
        )

        queue_title = QHBoxLayout()

        queue_title.addWidget(
            self.section_label(
                "UP NEXT"
            )
        )

        queue_title.addStretch()

        add = QPushButton(
            "+"
        )

        add.setFixedWidth(
            38
        )

        add.clicked.connect(
            self.open_files
        )

        queue_title.addWidget(
            add
        )

        queue_layout.addLayout(
            queue_title
        )

        self.playlist_search = QLineEdit()

        self.playlist_search.setPlaceholderText(
            "Search queue..."
        )

        queue_layout.addWidget(
            self.playlist_search
        )

        self.playlist = QListWidget()

        queue_layout.addWidget(
            self.playlist
        )

        queue_actions = QHBoxLayout()

        folder = QPushButton(
            "Folder"
        )

        file = QPushButton(
            "File"
        )

        clear = QPushButton(
            "Clear"
        )

        folder.clicked.connect(
            self.open_folder
        )

        file.clicked.connect(
            self.open_files
        )

        clear.clicked.connect(
            self.clear_playlist
        )

        queue_actions.addWidget(
            folder
        )

        queue_actions.addWidget(
            file
        )

        queue_actions.addWidget(
            clear
        )

        queue_layout.addLayout(
            queue_actions
        )

        splitter.addWidget(
            queue
        )
        # Keep playlist model alive for menus/managers, but remove the
        # permanent right-side queue from the main playback surface.
        self._queue_panel.hide()
        splitter.setCollapsible(1, True)
        splitter.setHandleWidth(0)
        splitter.setSizes([9999, 0])

        layout.addWidget(
            splitter,
            1
        )

        # TIMELINE

        self._timeline_widget = QWidget(page)
        timeline = QHBoxLayout(self._timeline_widget)
        timeline.setContentsMargins(0, 0, 0, 0)

        self.current_time = QLabel(
            "00:00"
        )

        self.current_time.setObjectName(
            "CinemaTime"
        )

        self.position = QSlider(
            Qt.Horizontal
        )
        self.position.setObjectName("CinemaSeek")
        self.position.setToolTip(
            "Drag to seek • release to continue playback"
        )

        self.position.setRange(
            0,
            0
        )

        self.total_time = QLabel(
            "00:00"
        )

        self.total_time.setObjectName(
            "CinemaTime"
        )

        timeline.addWidget(
            self.current_time
        )

        timeline.addWidget(
            self.position,
            1
        )

        timeline.addWidget(
            self.total_time
        )

        # CONTROLS
        # Keep transport controls on one row and secondary actions on a second
        # row.  A single long QHBoxLayout was allowing fixed-size widgets to
        # collide or disappear on narrower windows / high-DPI scaling.
        self.controls = QFrame(page)
        controls = self.controls
        controls.setObjectName("CinemaControls")
        controls.setMinimumHeight(122)
        controls.setMaximumHeight(142)

        controls_outer = QVBoxLayout(controls)
        controls_outer.setContentsMargins(10, 8, 10, 8)
        controls_outer.setSpacing(6)

        transport_row = QHBoxLayout()
        transport_row.setSpacing(7)
        self._transport_layout = transport_row

        self.previous_btn = QPushButton("⏮", controls)
        self.previous_btn.setObjectName("CinemaControl")
        self.rewind_btn = QPushButton("↶", controls)
        self.rewind_btn.setObjectName("CinemaControl")
        self.play_btn = QPushButton("▶", controls)
        self.play_btn.setObjectName("PrimaryCinema")
        self.forward_btn = QPushButton("↷", controls)
        self.forward_btn.setObjectName("CinemaControl")
        self.next_btn = QPushButton("⏭", controls)
        self.next_btn.setObjectName("CinemaControl")

        transport_buttons = [
            self.previous_btn, self.rewind_btn, self.play_btn,
            self.forward_btn, self.next_btn
        ]
        tooltips = {
            self.previous_btn: "Previous media",
            self.rewind_btn: "Rewind 10 seconds",
            self.play_btn: "Play / Pause (Space)",
            self.forward_btn: "Forward 10 seconds",
            self.next_btn: "Next media",
        }
        for button in transport_buttons:
            button.setMinimumHeight(52)
            button.setToolTip(tooltips[button])
            transport_row.addWidget(button)

        transport_row.addSpacing(5)

        mute = QPushButton("🔊", controls)
        mute.setFixedSize(42, 42)
        mute.setToolTip("Mute / restore volume")

        self.volume = QSlider(Qt.Horizontal, controls)
        self.volume.setRange(0, 100)
        self.volume.setMinimumWidth(90)
        self.volume.setMaximumWidth(160)
        self.volume.setToolTip("Volume")

        transport_row.addWidget(mute)
        transport_row.addWidget(self.volume, 1)

        speed_label = QLabel("Speed")
        speed_label.setObjectName("CinemaTime")
        transport_row.addWidget(speed_label)

        self.speed = QComboBox(controls)
        self.speed.addItems([
            "0.25x", "0.50x", "0.75x", "1.00x", "1.25x",
            "1.50x", "1.75x", "2.00x", "2.50x", "3.00x", "4.00x"
        ])
        self.speed.setMinimumWidth(78)
        self.speed.setMaximumWidth(100)
        transport_row.addWidget(self.speed)

        controls_outer.addLayout(transport_row)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(7)
        self._actions_layout = actions_row

        self.ab_btn = QPushButton("A-B", controls)
        self.ab_btn.setToolTip("Set / clear A-B repeat")
        self.bookmark_btn = QPushButton("🔖", controls)
        self.bookmark_btn.setToolTip("Add bookmark")
        self.fav_button = QPushButton("☆", controls)
        self.fav_button.setToolTip("Add / remove favorite")
        screenshot = QPushButton("📷", controls)
        screenshot.setToolTip("Take screenshot")
        fullscreen = QPushButton("⛶", controls)
        fullscreen.setToolTip("Fullscreen")

        for button in [
            self.ab_btn, self.bookmark_btn, self.fav_button, screenshot, fullscreen
        ]:
            button.setMinimumHeight(40)
            actions_row.addWidget(button)

        actions_row.addStretch(1)
        hint = QLabel("Space Play/Pause  •  F Fullscreen  •  ←/→ Seek")
        hint.setStyleSheet(f"color:{MUTED}; font-size:11px;")
        actions_row.addWidget(hint)

        controls_outer.addLayout(actions_row)

        controls_shadow = QGraphicsDropShadowEffect(controls)
        controls_shadow.setBlurRadius(26)
        controls_shadow.setOffset(0, 8)
        controls_shadow.setColor(QColor(0, 0, 0, 170))
        controls.setGraphicsEffect(controls_shadow)

        layout.addWidget(
            controls,
            0
        )
        layout.addWidget(
            self._timeline_widget,
            0
        )

        mute.clicked.connect(
            self.toggle_mute
        )

        screenshot.clicked.connect(
            self.screenshot
        )

        fullscreen.clicked.connect(
            self.toggle_fullscreen
        )

        return page

    # ========================================================
    # LIBRARY PAGE
    # ========================================================

    def create_library_page(
        self
    ):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            25,
            25,
            25,
            25
        )

        title = QLabel(
            "Media Library"
        )

        title.setObjectName(
            "PageTitle"
        )

        layout.addWidget(
            title
        )

        subtitle = QLabel(
            "Folders indexed by Nova."
        )

        subtitle.setStyleSheet(
            f"color:{MUTED};"
        )

        layout.addWidget(
            subtitle
        )

        self.library_list = QListWidget()

        layout.addWidget(
            self.library_list,
            1
        )

        buttons = QHBoxLayout()

        add = QPushButton(
            "＋ Add Folder"
        )

        scan = QPushButton(
            "↻ Scan"
        )

        add.clicked.connect(
            self.add_library_folder
        )

        scan.clicked.connect(
            self.scan_library
        )

        buttons.addWidget(
            add
        )

        buttons.addWidget(
            scan
        )

        buttons.addStretch()

        layout.addLayout(
            buttons
        )

        return page

    # ========================================================
    # MENU
    # ========================================================

    def build_menu(
        self
    ):
        """Build all top-level menus with visible actions."""
        bar = self.menuBar()
        bar.setVisible(True)
        bar.setNativeMenuBar(False)
        bar.setMinimumHeight(34)

        file_menu = bar.addMenu("File")
        file_menu.addAction(self.action("Open File", "Ctrl+O", self.open_files))
        file_menu.addAction(self.action("Open Folder", "Ctrl+Shift+O", self.open_folder))
        file_menu.addAction(self.action("Add Folder to Library", "", self.add_library_folder))
        file_menu.addSeparator()
        file_menu.addAction(self.action("Show Library", "", self.show_library))
        file_menu.addAction(self.action("Show Favorites", "", self.show_favorites))
        file_menu.addAction(self.action("Show Playlist", "", self.focus_playlist))
        file_menu.addSeparator()
        file_menu.addAction(self.action("Clear Playlist", "", self.clear_playlist))
        file_menu.addAction(self.action("Save State", "", self.save_state))
        file_menu.addSeparator()
        file_menu.addAction(self.action("Exit", "Alt+F4", self.close))

        playback = bar.addMenu("Playback")
        playback.addAction(self.action("Play / Pause", "Space", self.toggle_play))
        playback.addAction(self.action("Previous", "PageUp", self.previous))
        playback.addAction(self.action("Next", "PageDown", self.next))
        playback.addSeparator()
        playback.addAction(self.action("Seek Back", "Left", lambda: self.seek_relative(-self.seek_amount())))
        playback.addAction(self.action("Seek Forward", "Right", lambda: self.seek_relative(self.seek_amount())))
        playback.addAction(self.action("Seek Back 30 Seconds", "Shift+Left", lambda: self.seek_relative(-30000)))
        playback.addAction(self.action("Seek Forward 30 Seconds", "Shift+Right", lambda: self.seek_relative(30000)))
        playback.addSeparator()
        playback.addAction(self.action("A-B Repeat", "", self.toggle_ab))
        playback.addAction(self.action("Fullscreen", "F", self.toggle_fullscreen))
        playback.addAction(self.action("Add Bookmark", "Ctrl+B", self.add_bookmark))
        playback.addAction(self.action("Bookmarks", "", self.show_bookmarks))

        subtitles = bar.addMenu("Subtitles")
        subtitles.addAction(self.action("Load External Subtitle", "Ctrl+Shift+L", self.load_subtitle))
        subtitles.addAction(self.action("Load Sidecar Subtitle", "", self.load_sidecar_subtitle))
        subtitles.addAction(self.action("Remove Subtitle", "", self.remove_subtitle))
        subtitles.addSeparator()
        subtitles.addAction(self.action("Generate AI Subtitles", "Ctrl+Shift+A", self.ai_subtitles))
        subtitles.addAction(self.action("Subtitle Editor", "", self.open_subtitle_editor))
        subtitles.addAction(self.action("Translate Subtitles", "", self.translate_subtitles))
        subtitles.addAction(self.action("Transcript", "", self.show_transcript))

        ai = bar.addMenu("AI")
        ai.addAction(self.action("Generate AI Subtitles", "Ctrl+Shift+A", self.ai_subtitles))
        ai.addAction(self.action("Transcript Viewer", "", self.show_transcript))
        ai.addAction(self.action("AI Assistant", "", self.show_ai_assistant))
        ai.addAction(self.action("Generate Chapters", "", self.generate_chapters))
        ai.addAction(self.action("Translate Subtitles", "", self.translate_subtitles))
        ai.addSeparator()
        ai.addAction(self.action("AI / Whisper Settings", "", self.show_settings))

        tools = bar.addMenu("Tools")
        tools.addAction(self.action("Screenshot", "Ctrl+Alt+S", self.screenshot))
        tools.addAction(self.action("Media Information", "", self.show_media_info))
        tools.addAction(self.action("Subtitle Editor", "", self.open_subtitle_editor))
        tools.addAction(self.action("Playlist Manager", "", self.open_playlist_manager))
        tools.addAction(self.action("Bookmarks", "Ctrl+B", self.show_bookmarks))
        tools.addAction(self.action("Favorites", "", self.show_favorites))
        tools.addSeparator()
        tools.addAction(self.action("Sleep Timer", "", self.open_sleep_timer))
        tools.addAction(self.action("Convert / Export", "", self.open_converter))
        tools.addAction(self.action("Audio Output", "", self.open_audio_output))
        tools.addAction(self.action("Equalizer", "", self.open_equalizer))
        tools.addSeparator()
        tools.addAction(self.action("Settings", "", self.show_settings))
        tools.addAction(self.action("Background Activity Log", "Ctrl+L", self.show_background_log))
        tools.addAction(self.action("Close All Open Windows", "Ctrl+Shift+W", self.close_all_windows))


        media_menu = bar.addMenu("Media")
        media_menu.addAction(self.action("Open Network URL", "Ctrl+U", self.open_network_url))
        media_menu.addAction(self.action("Video Adjustments", "", self.open_video_adjustments))
        media_menu.addAction(self.action("Audio Tracks", "", self.show_audio_tracks))
        media_menu.addAction(self.action("Subtitle Tracks", "", self.show_subtitle_tracks))
        media_menu.addAction(self.action("Aspect Ratio", "", self.choose_aspect_ratio))
        media_menu.addAction(self.action("Fit Video", "", self.fit_video))
        media_menu.addAction(self.action("Zoom 100%", "", self.zoom_video))
        media_menu.addSeparator()
        media_menu.addAction(self.action("Frame Forward", ".", self.frame_forward))
        media_menu.addAction(self.action("Frame Backward", ",", self.frame_backward))

        ai.addAction(self.action("Open AI Command Center", "Ctrl+Shift+I", self.show_ai_center))

        tools.addAction(self.action("Video Adjustments", "", self.open_video_adjustments))
        tools.addAction(self.action("Command Palette", "Ctrl+K", self.show_command_palette))
        tools.addAction(self.action(f"Advanced Feature Center ({FEATURE_COUNT} Controls)", "Ctrl+Shift+F12", self.open_advanced_features))
        tools.addAction(self.action("Activity Center", "Ctrl+L", self.show_background_log))
        tools.addSeparator()

        # Theme selector. Each theme is checkable so the active GUI style is
        # obvious from the menu. The Theme Center is useful on touch devices
        # or when the user wants to browse all available styles at once.
        themes_menu = tools.addMenu("Themes")
        self.theme_actions = {}
        for theme_name in THEME_NAMES:
            action = themes_menu.addAction(theme_name)
            action.setCheckable(True)
            action.triggered.connect(
                lambda checked=False, name=theme_name: self.apply_theme(name)
            )
            self.theme_actions[theme_name] = action
        themes_menu.addSeparator()
        themes_menu.addAction(
            self.action("Theme Center…", "", self.show_theme_center)
        )

        # ----------------------------------------------------
        # V01 WORKSPACE
        # ----------------------------------------------------
        nova_menu = bar.addMenu("Nova")
        nova_menu.addAction(self.action("🎬 Media Library", "Ctrl+Shift+Y", self.show_v30_library))
        nova_menu.addAction(self.action("▶ Continue Watching", "Ctrl+Shift+R", self.show_continue_watching))
        nova_menu.addAction(self.action("🔎 Universal Search", "Ctrl+Shift+Space", self.show_universal_search))
        nova_menu.addAction(self.action("🧾 Subtitle Center", "", self.show_subtitle_center))
        nova_menu.addAction(self.action("🧠 Nova Intelligence", "Ctrl+Shift+N", self.show_intelligence))
        nova_menu.addAction(self.action("📋 Task Center", "Ctrl+Shift+T", self.show_task_center))
        nova_menu.addAction(self.action("ℹ Now Playing", "", self.show_now_playing))
        nova_menu.addSeparator()
        nova_menu.addAction(self.action("🪟 Mini Player", "Ctrl+Shift+P", self.toggle_mini_player))
        nova_menu.addAction(self.action("🎞 Cinema Mode", "Ctrl+Shift+C", self.activate_cinema_mode))
        nova_menu.addAction(self.action("🔄 Recover Last Session", "", self.recover_last_session))

        help_menu = bar.addMenu("Help")
        help_menu.addAction(self.action("Keyboard Shortcuts", "F1", self.show_keyboard_help))
        help_menu.addAction(self.action("About Nova AI Media Player", "", self.show_about))

        advanced_menu = bar.addMenu("Advanced")
        advanced_menu.addAction(self.action(f"Advanced Feature Center ({FEATURE_COUNT} Controls)", "Ctrl+Shift+F12", self.open_advanced_features))
        advanced_menu.addAction(self.action("Diagnostics", "Ctrl+Shift+D", self.open_diagnostics))
        advanced_menu.addAction(self.action("Performance HUD", "Ctrl+Shift+H", self.toggle_performance_hud))
        advanced_menu.addAction(self.action("Media Probe", "Ctrl+Shift+M", self.show_media_probe))
        advanced_menu.addSeparator()
        for _cat, label, key in FEATURE_MATRIX[:30]:
            action = advanced_menu.addAction(label)
            action.setCheckable(True)
            action.setChecked(bool(self.config.get(key, False)))
            action.triggered.connect(lambda checked=False, k=key: self.set_advanced_feature(k, checked))

        window_menu = bar.addMenu("Window")
        window_menu.addAction(self.action("Background Activity Log", "Ctrl+L", self.show_background_log))
        window_menu.addAction(self.action("Close All Open Windows", "Ctrl+Shift+W", self.close_all_windows))
        window_menu.addSeparator()
        window_menu.addAction(self.action("Bring Main Window to Front", "Ctrl+Shift+F", self.bring_main_to_front))

        self.file_menu = file_menu
        self.playback_menu = playback
        self.subtitles_menu = subtitles
        self.ai_menu = ai
        self.tools_menu = tools
        self.help_menu = help_menu
        self.window_menu = window_menu
        self.media_menu = media_menu
        self.advanced_menu = advanced_menu

        menu_style = f"""
            QMenu {{ background: #0b111c; color: {TEXT}; border: 1px solid #29384d; padding: 7px; }}
            QMenu::item {{ color: {TEXT}; padding: 9px 18px; }}
            QMenu::item:selected {{ background: #1a2b48; color: white; }}
            QMenu::separator {{ height: 1px; background: #25344a; margin: 7px 8px; }}
        """
        for menu in (file_menu, playback, subtitles, ai, tools, help_menu, advanced_menu, window_menu):
            menu.setStyleSheet(menu_style)

    def open_advanced_features(self):
        dialog = AdvancedFeaturesDialog(self.config, self)
        if dialog.exec():
            self.advanced_features = {k: bool(self.config.get(k, False)) for _c, _n, k in FEATURE_MATRIX}
            write_json(CONFIG_FILE, self.config)
            self.status.setText("Advanced feature settings saved.")
            self.log_activity(f"Advanced Feature Center saved {FEATURE_COUNT} controls.")

    def set_advanced_feature(self, key, value):
        self.config[key] = bool(value)
        self.advanced_features[key] = bool(value)
        if key == "adv_always_on_top":
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, bool(value))
            self.show()
        write_json(CONFIG_FILE, self.config)

    def open_diagnostics(self):
        try:
            import PySide6
            qt_version = getattr(PySide6, "__version__", "unknown")
        except Exception:
            qt_version = "unknown"
        details = [
            f"Nova: {APP_VERSION}",
            f"Python: {sys.version.split()[0]}",
            f"PySide6: {qt_version}",
            f"FFmpeg: {'available' if ffmpeg() else 'not found'}",
            f"FFprobe: {'available' if ffprobe() else 'not found'}",
            f"Current media: {self.current_source or 'none'}",
            f"Position: {format_time(self.player.position())}",
            f"Duration: {format_time(self.player.duration())}",
            f"Playlist items: {len(self.playlist_files)}",
            f"Library folders: {len(self.library)}",
            f"Favorites: {len(self.favorites)}",
            f"AI model: {self.config.get('ai_model', 'base')}",
            f"AI device: {self.config.get('ai_device', 'auto')}",
        ]
        QMessageBox.information(self, "Nova Diagnostics", "\n".join(details))

    def toggle_performance_hud(self):
        enabled = not bool(self.config.get("adv_performance_hud_live", False))
        self.config["adv_performance_hud_live"] = enabled
        write_json(CONFIG_FILE, self.config)
        self.status.setText("Performance HUD: ON" if enabled else "Performance HUD: OFF")
        self.log_activity("Performance HUD toggled " + ("ON" if enabled else "OFF"))

    def show_media_probe(self):
        if not self.current_source:
            QMessageBox.information(self, "Media Probe", "Open a media file first.")
            return
        exe = ffprobe()
        if not exe:
            QMessageBox.warning(self, "Media Probe", "ffprobe.exe is not available in PATH.")
            return
        try:
            result = subprocess.run([exe, "-hide_banner", "-show_format", "-show_streams", "-of", "json", self.current_source], capture_output=True, text=True, errors="replace", timeout=30)
            text = result.stdout or result.stderr or "No probe data."
        except Exception as exc:
            text = str(exc)
        dialog = QDialog(self)
        dialog.setWindowTitle("Media Probe")
        dialog.resize(900, 650)
        lay = QVBoxLayout(dialog)
        edit = QTextEdit()
        edit.setReadOnly(True)
        edit.setPlainText(text)
        lay.addWidget(edit)
        close = QPushButton("Close")
        close.clicked.connect(dialog.accept)
        lay.addWidget(close)
        dialog.exec()

    def eventFilter(self, watched, event):
        """Track child dialogs so Window -> Close All Open Windows can close them."""
        try:
            if isinstance(watched, QDialog) and watched is not self:
                if watched.parent() is self:
                    if event.type() == QEvent.Type.Show:
                        if watched not in self._open_dialogs:
                            self._open_dialogs.append(watched)
                    elif event.type() in (QEvent.Type.Close, QEvent.Type.Hide, QEvent.Type.Destroy):
                        if watched in self._open_dialogs:
                            self._open_dialogs.remove(watched)
        except RuntimeError:
            pass
        return super().eventFilter(watched, event)

    def log_activity(self, message):
        """Record a timestamped background event and mirror it to the log window."""
        stamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{stamp}] {message}"
        self._background_log_lines.append(line)
        if len(self._background_log_lines) > 2000:
            self._background_log_lines = self._background_log_lines[-2000:]
        dialog = getattr(self, "_background_log_dialog", None)
        if dialog is not None:
            try:
                dialog.append_line(line)
            except RuntimeError:
                self._background_log_dialog = None

    def show_background_log(self):
        if self._background_log_dialog is None:
            self._background_log_dialog = BackgroundLogDialog(self)
            self._background_log_dialog.finished.connect(
                lambda _=0: setattr(self, "_background_log_dialog", None)
            )
        try:
            self._background_log_dialog.log.setPlainText("\n".join(self._background_log_lines))
            self._background_log_dialog.show()
            self._background_log_dialog.raise_()
            self._background_log_dialog.activateWindow()
        except RuntimeError:
            self._background_log_dialog = None
            self.show_background_log()

    def close_all_windows(self):
        """Close all secondary windows/dialogs while keeping the main player open."""
        closed = 0
        for widget in list(QApplication.topLevelWidgets()):
            if widget is self:
                continue
            if isinstance(widget, QDialog):
                try:
                    widget.close()
                    closed += 1
                except RuntimeError:
                    pass
        menu = getattr(self, "_video_context_menu", None)
        if menu is not None:
            try:
                menu.close()
            except RuntimeError:
                pass
            self._video_context_menu = None
        self._open_dialogs = []
        self.status.setText(f"Closed {closed} open window(s).")
        self.log_activity(f"Window manager: closed {closed} secondary window(s).")
        self.raise_()
        self.activateWindow()

    def bring_main_to_front(self):
        try:
            if self.isMinimized():
                self.showNormal()
            self.raise_()
            self.activateWindow()
        except RuntimeError:
            pass

    def action(
        self,
        name,
        shortcut,
        callback
    ):

        action = QAction(
            name,
            self
        )

        if shortcut:

            action.setShortcut(
                QKeySequence(
                    shortcut
                )
            )

        action.triggered.connect(
            callback
        )

        return action

    def show_command_palette(self):
        actions=[
            ("▶ Play / Pause", self.toggle_play), ("⏪ Seek Back", lambda:self.seek_relative(-self.seek_amount())), ("⏩ Seek Forward", lambda:self.seek_relative(self.seek_amount())),
            ("⏮ Previous", self.previous), ("⏭ Next", self.next), ("⛶ Fullscreen", self.toggle_fullscreen), ("🔇 Mute", self.toggle_mute),
            ("✨ Generate AI Subtitles", self.ai_subtitles), ("✨ AI Command Center", self.show_ai_center), ("🧾 Transcript", self.show_transcript),
            ("🧭 Generate Chapters", self.generate_chapters), ("🌐 Translate Subtitles", self.translate_subtitles), ("🔎 Search Transcript", self.open_transcript_search),
            ("📷 Screenshot", self.screenshot), ("🔖 Bookmarks", self.show_bookmarks), ("☆ Favorites", self.show_favorites), ("🎛 Video Adjustments", self.open_video_adjustments),
            ("🎚 Equalizer", self.open_equalizer), ("🔊 Audio Output", self.open_audio_output), ("📜 Activity Center", self.show_background_log), ("⚙ Settings", self.show_settings),
            ("🎬 Media Library", self.show_v30_library), ("▶ Continue Watching", self.show_continue_watching), ("🔎 Universal Search", self.show_universal_search), ("🧾 Subtitle Center", self.show_subtitle_center), ("🧠 Nova Intelligence", self.show_intelligence), ("📋 Task Center", self.show_task_center), ("ℹ Now Playing", self.show_now_playing), ("🪟 Mini Player", self.toggle_mini_player),
        ]
        dlg=CommandPaletteDialog(actions,self); dlg.show(); dlg.raise_(); dlg.activateWindow(); self._open_dialogs.append(dlg); self._palette_dialog=dlg

    def show_ai_center(self):
        dlg=AICommandCenterDialog(self,self); dlg.show(); dlg.raise_(); dlg.activateWindow(); self._open_dialogs.append(dlg)

    def open_transcript_search(self):
        if not self.transcript:
            QMessageBox.information(self,"Transcript Search","Generate AI subtitles first."); return
        text,ok=QInputDialog.getText(self,"Search Transcript","Find text:")
        if not ok or not text.strip(): return
        q=text.lower().strip(); hits=[s for s in self.transcript if q in s.get("text","").lower()]
        if not hits:
            QMessageBox.information(self,"Transcript Search","No matching transcript segments found."); return
        lines=[f"[{format_time(int(s['start']*1000))}] {s['text']}" for s in hits]
        dlg=QDialog(self); dlg.setWindowTitle(f"Transcript Search — {len(hits)} match(es)"); dlg.resize(760,500); l=QVBoxLayout(dlg); w=QListWidget(); l.addWidget(w)
        for s in hits:
            it=QListWidgetItem(f"[{format_time(int(s['start']*1000))}]  {s['text']}"); it.setData(Qt.ItemDataRole.UserRole,int(s['start']*1000)); w.addItem(it)
        w.itemDoubleClicked.connect(lambda it:self.player.setPosition(int(it.data(Qt.ItemDataRole.UserRole))))
        b=QPushButton("Close"); b.clicked.connect(dlg.close); l.addWidget(b); dlg.show(); self._open_dialogs.append(dlg)

    def open_network_url(self):
        url,ok=QInputDialog.getText(self,"Open Network URL","HTTP / HTTPS / RTSP / HLS URL:")
        if not ok or not url.strip(): return
        self.current_source=url.strip()
        self.player.setSource(QUrl(self.current_source)); self.player.play(); self.show_player(); self.log_activity(f"Network media opened: {self.current_source}")

    def open_video_adjustments(self):
        dlg=VideoAdjustmentsDialog(self.config,self); dlg.changed.connect(lambda v:self.log_activity(f"Video adjustments updated: {v}")); dlg.show(); self._open_dialogs.append(dlg)

    def show_audio_tracks(self):
        tracks=getattr(self.player,"audioTracks",lambda:[])()
        if not tracks:
            QMessageBox.information(self,"Audio Tracks","No alternate audio tracks reported by the current Qt Multimedia backend."); return
        menu=QMenu(self); 
        for i,t in enumerate(tracks):
            label=t.get("title",f"Audio Track {i+1}") if isinstance(t,dict) else str(t)
            a=menu.addAction(label); a.triggered.connect(lambda checked=False,idx=i:self._set_audio_track(idx))
        menu.exec(QCursor.pos())
    def _set_audio_track(self,index):
        if hasattr(self.player,"setActiveAudioTrack"): self.player.setActiveAudioTrack(index)

    def show_subtitle_tracks(self):
        menu=QMenu(self); menu.addAction("Load External Subtitle").triggered.connect(self.load_subtitle); menu.addAction("Load Sidecar Subtitle").triggered.connect(self.load_sidecar_subtitle); menu.addAction("Remove Subtitle").triggered.connect(self.remove_subtitle); menu.exec(QCursor.pos())

    def choose_aspect_ratio(self):
        choice,ok=QInputDialog.getItem(self,"Aspect Ratio","Mode:",["Auto","16:9","4:3","1:1","2.39:1"],0,False)
        if ok: self.config["aspect_ratio"]=choice; self.status.setText(f"Aspect ratio: {choice}")

    def fit_video(self):
        self.video.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding); self.status.setText("Video fit: contain")
    def zoom_video(self):
        self.status.setText("Video zoom: 100%")

    def frame_forward(self):
        self._was_playing_before_seek = self.player.playbackState() == QMediaPlayer.PlayingState
        self._seek_and_resume(min(self.player.duration(), self.player.position() + 42), False)
        self.status.setText("Frame +")

    def frame_backward(self):
        self._was_playing_before_seek = self.player.playbackState() == QMediaPlayer.PlayingState
        self._seek_and_resume(max(0, self.player.position() - 42), False)
        self.status.setText("Frame -")

    def apply_theme(self, name):
        """Apply both the visual palette and the physical GUI layout."""
        if name not in THEME_SPECS:
            name = "Nova Dark"

        spec = THEME_SPECS[name]
        layout_spec = THEME_LAYOUTS.get(name, THEME_LAYOUTS["Nova Dark"])

        # Keep these globals in sync for code that still builds small UI pieces
        # using the legacy Nova color constants.
        global STYLE, BLUE, PURPLE, CYAN, BG
        BLUE = spec["accent"]
        PURPLE = spec["accent2"]
        CYAN = spec["glow"]
        BG = spec["bg"]

        QApplication.instance().setStyleSheet(
            BASE_STYLE + theme_stylesheet(name)
        )

        self.config["theme"] = name
        self.config["accent"] = spec["accent"]
        write_json(CONFIG_FILE, self.config)

        self._apply_interface_layout(layout_spec)

        for theme_name, action in getattr(self, "theme_actions", {}).items():
            try:
                action.setChecked(theme_name == name)
            except Exception:
                pass

        try:
            self.status.setText(f"Theme: {name} • {layout_spec['mode'].title()} layout")
        except Exception:
            pass
        try:
            self.log_activity(f"Theme changed to {name} ({layout_spec['mode']} layout)")
        except Exception:
            pass

    def _apply_interface_layout(self, layout_spec):
        """Physically rearrange the main player interface for a theme."""
        try:
            self.sidebar.setFixedWidth(int(layout_spec.get("sidebar_width", 230)))
            self.sidebar.setVisible(bool(layout_spec.get("sidebar", False)))

            self._queue_panel.setVisible(bool(layout_spec.get("queue", False)))
            self._splitter.setOrientation(layout_spec.get("orientation", Qt.Orientation.Horizontal))

            margins = layout_spec.get("margins", (18, 14, 18, 14))
            self.player_page.layout().setContentsMargins(*margins)
            self.player_page.layout().setSpacing(int(layout_spec.get("spacing", 12)))

            self.controls.setMinimumHeight(int(layout_spec.get("controls_min", 122)))
            self.controls.setMaximumHeight(int(layout_spec.get("controls_max", 142)))

            # Move the seek timeline above or below the transport controls.
            player_layout = self.player_page.layout()
            player_layout.removeWidget(self._timeline_widget)
            player_layout.removeWidget(self.controls)
            if layout_spec.get("timeline_first", False):
                player_layout.addWidget(self._timeline_widget, 0)
                player_layout.addWidget(self.controls, 0)
            else:
                player_layout.addWidget(self.controls, 0)
                player_layout.addWidget(self._timeline_widget, 0)

            # Compact/minimal themes hide secondary chrome while keeping the
            # actual player controls and playback information available.
            header_mode = layout_spec.get("header", "full")
            compact_widgets = [
                getattr(self, "_cinema_badge", None),
                getattr(self, "format_badge", None),
                getattr(self, "ai_badge", None),
                getattr(self, "ai_main", None),
            ]
            for widget in compact_widgets:
                if widget is not None:
                    widget.setVisible(header_mode == "full")

            if header_mode == "minimal":
                if hasattr(self, "page_title"):
                    self.page_title.setVisible(False)
                if hasattr(self, "now_playing"):
                    self.now_playing.setVisible(False)
            else:
                if hasattr(self, "page_title"):
                    self.page_title.setVisible(True)
                if hasattr(self, "now_playing"):
                    self.now_playing.setVisible(True)

            # Recompute splitter sizes after the layout has had a chance to
            # resize. The queue ratio is expressed as a percentage of the
            # available splitter extent.
            ratio = int(layout_spec.get("queue_ratio", 0))
            orientation = layout_spec.get("orientation", Qt.Orientation.Horizontal)

            def apply_sizes():
                try:
                    if not layout_spec.get("queue", False) or ratio <= 0:
                        self._splitter.setSizes([max(1, self._splitter.width() or 1), 0])
                        return
                    total = self._splitter.height() if orientation == Qt.Orientation.Vertical else self._splitter.width()
                    total = max(200, int(total))
                    queue_size = max(180, int(total * ratio / 100))
                    video_size = max(220, total - queue_size)
                    self._splitter.setSizes([video_size, queue_size])
                except Exception:
                    pass

            QTimer.singleShot(0, apply_sizes)
            QTimer.singleShot(120, apply_sizes)

            self._active_layout_theme = layout_spec.get("mode", "cinema")
        except Exception:
            pass

    def show_theme_center(self):
        """Open a simple GUI selector for the available Nova themes."""
        current = self.config.get("theme", "Nova Dark")
        if current not in THEME_NAMES:
            current = "Nova Dark"

        dialog = QDialog(self)
        dialog.setWindowTitle("Nova Theme Center")
        dialog.resize(560, 430)
        layout = QVBoxLayout(dialog)

        title = QLabel("Choose Nova Appearance")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        layout.addWidget(title)

        description = QLabel(
            "These are interface themes, not just color palettes. Each one can "
            "rearrange the navigation, video area, queue, header and controls. "
            "Your selection is saved automatically."
        )
        description.setWordWrap(True)
        description.setStyleSheet(f"color:{MUTED};")
        layout.addWidget(description)

        selector = QComboBox()
        selector.addItems(THEME_NAMES)
        selector.setCurrentText(current)
        layout.addWidget(selector)

        preview = QFrame()
        preview.setObjectName("Card")
        preview_layout = QVBoxLayout(preview)
        preview_title = QLabel("THEME PREVIEW")
        preview_title.setStyleSheet("font-weight:800; letter-spacing:1px;")
        preview_layout.addWidget(preview_title)
        preview_text = QLabel(
            THEME_DESCRIPTIONS.get(current, "The interface layout changes with this theme.")
        )
        preview_text.setWordWrap(True)
        preview_layout.addWidget(preview_text)
        layout.addWidget(preview, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Apply | QDialogButtonBox.Cancel
        )
        layout.addWidget(buttons)

        def update_preview():
            name = selector.currentText()
            preview_text.setText(THEME_DESCRIPTIONS.get(name, "The interface layout changes with this theme."))
            preview.setStyleSheet(theme_stylesheet(name))

        selector.currentTextChanged.connect(update_preview)

        def apply_selected():
            self.apply_theme(selector.currentText())
            update_preview()

        buttons.button(QDialogButtonBox.Apply).clicked.connect(apply_selected)
        buttons.rejected.connect(dialog.reject)
        dialog.exec()

    def show_keyboard_help(
        self
    ):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nova AI Media Player — Keyboard Shortcuts")
        dialog.resize(720, 560)
        layout = QVBoxLayout(dialog)
        title = QLabel("Keyboard Shortcuts")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(title)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setHtml(
            "<b>Playback</b><br>"
            "Space — Play / Pause<br>"
            "Left / Right — Seek<br>"
            "Shift + Left / Right — Seek 30 seconds<br>"
            "PageUp / PageDown — Previous / Next<br>"
            "F — Fullscreen<br>"
            "Ctrl+O — Open file<br>"
            "Ctrl+Shift+O — Open folder<br>"
            "Ctrl+Shift+A — Generate AI subtitles<br>"
            "Ctrl+Alt+S — Screenshot<br>"
            "F1 — Keyboard shortcuts<br><br>"
            "<b>Mouse</b><br>"
            "Drag media files onto the player to add and play them.<br>"
            "Double-click a queue item to play it."
        )
        layout.addWidget(text, 1)
        close = QPushButton("Close")
        close.clicked.connect(dialog.accept)
        layout.addWidget(close)
        dialog.exec()

    def show_about(
        self
    ):
        dialog = QDialog(self)
        dialog.setWindowTitle("About Nova AI Media Player")
        dialog.setObjectName("NovaAboutDialog")
        dialog.resize(680, 560)
        dialog.setMinimumSize(560, 460)
        layout = QVBoxLayout(dialog)
        title = QLabel("◈ NOVA AI MEDIA PLAYER")
        title.setFont(QFont("Segoe UI", 23, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{CYAN};")
        layout.addWidget(title)
        version = QLabel(f"Version {APP_VERSION}  •  Modern Windows desktop media player")
        developer = QLabel(f"Developer: {DEVELOPER_NAME}")
        developer.setStyleSheet(f"color:{TEXT};font-weight:700;")
        layout.addWidget(developer)
        version.setStyleSheet(f"color:{MUTED};")
        layout.addWidget(version)
        developer = QLabel(f"Developer: {DEVELOPER_NAME}")
        developer.setStyleSheet(f"color:{CYAN}; font-weight:700;")
        layout.addWidget(developer)
        info = QTextEdit()
        info.setReadOnly(True)
        info.setHtml(
            "<h3>Playback</h3>"
            "Audio/video playback, playlist queue, drag & drop, folder scanning, "
            "seeking, speed control, A-B repeat, fullscreen, volume and bookmarks."
            "<h3>Subtitles & AI</h3>"
            "External and sidecar subtitles, subtitle editing, transcript viewing, "
            "local faster-whisper transcription, translation, chapters and AI assistant."
            "<h3>Media Tools</h3>"
            "Screenshots, media information, playlist manager, favorites, sleep timer, "
            "audio output, equalizer controls and FFmpeg conversion/export."
            "<h3>AI Privacy</h3>"
            "Local transcription works without an online API key. Online AI functions "
            "use the API settings configured by the user."
            "<h3>Nova Workspace</h3>"
            "Media Library with smart collections, Continue Watching, Universal Search, "
            "Subtitle Center, Nova Intelligence workspace, Now Playing panel, Mini Player, "
            "Cinema Mode, background Task Center and crash/session recovery."
        )
        layout.addWidget(info, 1)
        close = QPushButton("Close")
        close.clicked.connect(dialog.accept)
        layout.addWidget(close)
        dialog.exec()

    def _rebuild_play_button(self):
        """Recreate the play button if an invalid Qt wrapper is encountered."""
        old = getattr(self, "play_btn", None)
        if old is not None:
            try:
                old.deleteLater()
            except Exception:
                pass
        self.play_btn = QPushButton("▶", self.controls)
        self.play_btn.setObjectName("Play")
        getattr(self, "_transport_layout", self.controls.layout()).insertWidget(2, self.play_btn)

    # ========================================================
    # SIGNALS
    # ========================================================

    def connect_signals(
        self
    ):

        # The playback controls are explicitly parented to self.controls.
        # Guard against a stale Qt wrapper so startup never dies here.
        try:
            self.play_btn.objectName()
        except RuntimeError:
            self._rebuild_play_button()

        self.play_btn.clicked.connect(
            self.toggle_play
        )

        self.previous_btn.clicked.connect(
            self.previous
        )

        self.next_btn.clicked.connect(
            self.next
        )

        self.rewind_btn.clicked.connect(
            lambda:
            self.seek_relative(
                -10000
            )
        )

        self.forward_btn.clicked.connect(
            lambda:
            self.seek_relative(
                10000
            )
        )

        self.position.sliderPressed.connect(
            self.begin_slider_seek
        )
        self.position.sliderMoved.connect(
            self.preview_slider_seek
        )
        self.position.sliderReleased.connect(
            self.commit_slider_seek
        )

        self.volume.valueChanged.connect(
            self.set_volume
        )

        self.speed.currentTextChanged.connect(
            self.set_speed
        )

        self.playlist.itemDoubleClicked.connect(
            self.play_selected
        )

        self.playlist_search.textChanged.connect(
            self.filter_playlist
        )

        self.ai_main.clicked.connect(
            self.ai_subtitles
        )

        self.ab_btn.clicked.connect(
            self.toggle_ab
        )

        self.bookmark_btn.clicked.connect(
            self.add_bookmark
        )

        self.fav_button.clicked.connect(
            self.toggle_favorite
        )

        self.video.clicked.connect(
            self.toggle_play
        )
        self.video.rightClicked.connect(
            self.show_video_context_menu
        )

        self.player.positionChanged.connect(
            self.position_changed
        )

        self.player.durationChanged.connect(
            self.duration_changed
        )

        self.player.playbackStateChanged.connect(
            self.state_changed
        )

        self.player.mediaStatusChanged.connect(
            self.media_status
        )

        self.player.errorOccurred.connect(
            self.media_error
        )

    # ========================================================
    # TIMER
    # ========================================================

    def setup_timer(
        self
    ):

        self.timer = QTimer(
            self
        )

        self.timer.timeout.connect(
            self.timer_tick
        )

        self.timer.start(
            333
        )

    # ========================================================
    # PAGE NAVIGATION
    # ========================================================

    def show_player(
        self
    ):

        self.main_stack.setCurrentWidget(
            self.player_page
        )

    def show_home(
        self
    ):

        self.main_stack.setCurrentWidget(
            self.home_page
        )

        self.update_home()

    def show_library(
        self
    ):

        self.main_stack.setCurrentWidget(
            self.library_page
        )

        self.refresh_library()

    def focus_playlist(
        self
    ):

        self.show_player()
        self.open_playlist_manager()

    # ========================================================
    # HOME
    # ========================================================

    def update_home(
        self
    ):

        self.home_cards[0].setText(
            str(
                len(
                    self.playlist_files
                )
            )
        )

        self.home_cards[1].setText(
            str(
                len(
                    self.playlist_files
                )
            )
        )

        self.home_cards[2].setText(
            "READY"
        )

        self.home_cards[3].setText(
            str(
                len(
                    self.library
                )
            )
        )

        self.recent_list.clear()

        recent = sorted(
            self.history.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for path, _ in recent[:12]:

            if not os.path.exists(
                path
            ):
                continue

            item = QListWidgetItem(
                Path(path).name
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                path
            )

            self.recent_list.addItem(
                item
            )

        self.recent_list.itemDoubleClicked.connect(
            self.recent_opened
        )

    def recent_opened(
        self,
        item
    ):

        path = item.data(
            Qt.ItemDataRole.UserRole
        )

        if path:

            self.add_files(
                [path]
            )

            self.play_file(
                path
            )

            self.show_player()

    # ========================================================
    # LIBRARY
    # ========================================================

    def refresh_library(
        self
    ):

        self.library_list.clear()

        for folder in self.library:

            self.library_list.addItem(
                folder
            )

    def add_library_folder(
        self
    ):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Add Media Library Folder"
        )

        if not folder:
            return

        folder = os.path.abspath(
            folder
        )

        if folder not in self.library:

            self.library.append(
                folder
            )

        write_json(
            LIBRARY_FILE,
            self.library
        )

        self.scan_library()

    def scan_library(
        self
    ):

        self.status.setText(
            "Scanning library..."
        )

        files = []

        for folder in self.library:

            if not os.path.isdir(
                folder
            ):
                continue

            for root, dirs, names in os.walk(
                folder
            ):

                for name in names:

                    path = os.path.join(
                        root,
                        name
                    )

                    if is_media(path):

                        files.append(
                            path
                        )

                if not self.config.get(
                    "scan_subfolders",
                    True
                ):

                    dirs[:] = []

        self.add_files(
            files
        )

        self.status.setText(
            f"Library scan complete: {len(files)} media files."
        )

    # ========================================================
    # PLAYLIST
    # ========================================================

    def add_files(
        self,
        files
    ):

        changed = False

        for path in files:

            path = os.path.abspath(
                path
            )

            if not is_media(
                path
            ):
                continue

            if path in self.playlist_files:
                continue

            self.playlist_files.append(
                path
            )

            item = QListWidgetItem(
                Path(path).name
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                path
            )

            item.setToolTip(
                path
            )

            self.playlist.addItem(
                item
            )

            changed = True

        if changed:

            self.save_playlist()

            self.update_home()

    def open_files(
        self
    ):

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Open Media"
        )

        if not files:
            return

        self.add_files(
            files
        )

        self.play_file(
            files[0]
        )

        self.show_player()

    def open_folder(
        self
    ):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Open Media Folder"
        )

        if not folder:
            return

        files = []

        for root, dirs, names in os.walk(
            folder
        ):

            for name in sorted(
                names
            ):

                path = os.path.join(
                    root,
                    name
                )

                if is_media(
                    path
                ):

                    files.append(
                        path
                    )

            if not self.config.get(
                "scan_subfolders",
                True
            ):

                dirs[:] = []

        self.add_files(
            files
        )

        if files:

            self.play_file(
                files[0]
            )

    def save_playlist(
        self
    ):

        write_json(
            PLAYLIST_FILE,
            self.playlist_files
        )

    def clear_playlist(
        self
    ):

        self.playlist.clear()

        self.playlist_files.clear()

        self.current_index = -1

        self.save_playlist()

        self.update_home()

    def filter_playlist(
        self,
        text
    ):

        text = text.lower()

        for i in range(
            self.playlist.count()
        ):

            item = self.playlist.item(i)

            item.setHidden(
                text not in item.text().lower()
            )

    # ========================================================
    # PLAYBACK
    # ========================================================

    def play_file(
        self,
        path
    ):

        if not os.path.exists(path):
            return

        self._cancel_seek_timer()
        self._seek_generation += 1
        self._pending_autoplay = True
        self._pending_source = str(path)
        self._pending_start_position = 0
        self._last_ui_position = -1000
        self._reset_subtitle_cache()

        try:
            self.current_index = self.playlist_files.index(path)
        except ValueError:
            self.current_index = -1

        self.current_source = str(path)

        try:
            self.player.stop()
        except Exception:
            pass

        self.player.setSource(QUrl.fromLocalFile(path))

        self.now_playing.setText(Path(path).name)
        self.format_badge.setText(Path(path).suffix.upper())
        self.status.setText("Loading media…")

        if self.current_index >= 0:
            self.playlist.setCurrentRow(self.current_index)

        self.current_subtitles = []
        self.subtitle_label.clear()
        if hasattr(self, "_fullscreen_subtitle"):
            self._fullscreen_subtitle.clear()
        self.load_sidecar_subtitle()

        if not self.current_subtitles:
            ai_sidecar = SUBTITLE_DIR / (Path(path).stem + ".ai.srt")
            if ai_sidecar.exists():
                try:
                    self.load_subtitle_file(str(ai_sidecar))
                    self.log_activity(f"Loaded cached AI subtitles: {ai_sidecar.name}")
                except Exception as exc:
                    self.log_activity(f"Could not load cached AI subtitles: {exc}")

        saved = self.history.get(path, 0)
        if saved and self.config.get("remember_position", True):
            self._pending_start_position = max(0, int(saved))

        self.update_home()

        # Do not call play() yet. Let Qt finish demux/decoder initialization.

    def _cancel_seek_timer(self):
        timer = self._seek_resume_timer
        self._seek_resume_timer = None
        if timer is not None:
            try:
                timer.stop()
                timer.deleteLater()
            except Exception:
                pass

    def _start_pending_playback(self):
        if not self._pending_autoplay or not self.current_source:
            return
        if self._pending_source != self.current_source:
            self._pending_autoplay = False
            return

        self._pending_autoplay = False
        target = int(self._pending_start_position or 0)
        self._pending_start_position = 0

        if target > 0:
            self.status.setText("Restoring playback position…")
            self._seek_and_resume(target, True, delay_ms=300)
        else:
            self.status.setText("Starting playback…")
            QTimer.singleShot(60, self._play_after_load)

    def _play_after_load(self):
        if not self.current_source:
            return
        try:
            # Avoid carrying an unusual playback rate into a fresh media start.
            self.player.setPlaybackRate(1.0)
            self.player.play()
        except Exception:
            pass

    def play_selected(
        self,
        item
    ):

        path = item.data(
            Qt.ItemDataRole.UserRole
        )

        if path:

            self.play_file(
                path
            )

    def toggle_play(
        self
    ):

        # A manual play/pause action overrides queued autoplay.
        self._pending_autoplay = False

        if (
            self.player.playbackState()
            == QMediaPlayer.PlayingState
        ):

            self.player.pause()

        else:

            self.player.play()

    def state_changed(
        self,
        state
    ):

        self.play_btn.setText(
            "Ⅱ"
            if state
            == QMediaPlayer.PlayingState
            else "▶"
        )

    def previous(
        self
    ):

        if not self.playlist_files:
            return

        index = max(
            0,
            self.current_index - 1
        )

        self.play_file(
            self.playlist_files[index]
        )

    def next(
        self
    ):

        if not self.playlist_files:
            return

        index = (
            self.current_index
            + 1
        )

        if (
            index
            >= len(
                self.playlist_files
            )
        ):

            if self.config.get(
                "loop",
                False
            ):

                index = 0

            else:

                return

        self.play_file(
            self.playlist_files[index]
        )

    def seek_amount(
        self
    ):

        return (
            self.config.get(
                "seek_seconds",
                5
            )
            * 1000
        )

    def _seek_and_resume(self, target, resume=True, delay_ms=300):
        """Seek once while paused and resume only after the decoder has settled."""
        duration = max(0, int(self.player.duration()))
        if duration > 0:
            target = max(0, min(int(target), duration))
        else:
            target = max(0, int(target))

        self._cancel_seek_timer()
        self._seek_generation += 1
        generation = self._seek_generation

        try:
            self.player.pause()
            self.player.setPosition(target)
        except Exception:
            return

        if not resume or not self.current_source:
            return

        self._schedule_seek_resume(generation, max(100, int(delay_ms)), 0)

    def _schedule_seek_resume(self, generation, delay_ms=300, attempts=0):
        """Wait for Loaded/Buffered state before resuming; cap wait to ~1 second."""
        self._cancel_seek_timer()
        self._seek_resume_timer = QTimer(self)
        self._seek_resume_timer.setSingleShot(True)

        def resume_when_ready():
            if generation != self._seek_generation or not self.current_source:
                return

            ready = True
            try:
                media_status = self.player.mediaStatus()
                ready_status = media_status in (
                    QMediaPlayer.LoadedMedia,
                    QMediaPlayer.BufferedMedia
                )
                if hasattr(self.player, "bufferProgress"):
                    ready = ready_status and self.player.bufferProgress() >= 0.95
                else:
                    ready = ready_status
            except Exception:
                ready = True

            if ready or attempts >= 8:
                self._seek_resume_timer = None
                try:
                    self.player.play()
                except Exception:
                    pass
                return

            self._schedule_seek_resume(
                generation,
                min(150, max(70, delay_ms)),
                attempts + 1
            )

        self._seek_resume_timer.timeout.connect(resume_when_ready)
        self._seek_resume_timer.start(max(70, int(delay_ms)))

    def seek_relative(
        self,
        value
    ):
        was_playing = (
            self.player.playbackState()
            == QMediaPlayer.PlayingState
        )
        target = self.player.position() + int(value)
        self._seek_and_resume(target, was_playing)

    def begin_slider_seek(self):
        self._was_playing_before_seek = (
            self.player.playbackState()
            == QMediaPlayer.PlayingState
        )
        self._seek_target = self.position.value()
        if self._was_playing_before_seek:
            self.player.pause()

    def preview_slider_seek(self, value):
        # Never call QMediaPlayer.setPosition while the mouse is moving.
        # This is the main fix for post-seek decoder lag/stutter.
        self._seek_target = int(value)
        self.current_time.setText(
            format_time(self._seek_target)
        )

    def commit_slider_seek(self):
        target = int(self._seek_target)
        was_playing = bool(self._was_playing_before_seek)
        self._was_playing_before_seek = False
        self._seek_and_resume(target, was_playing)

    # ========================================================
    # TIMELINE
    # ========================================================

    def position_changed(
        self,
        position
    ):
        if not self.position.isSliderDown():
            self.position.setValue(position)

        self.footer_position = position

        # Throttle text updates to avoid needless repaint/layout work.
        if (
            abs(int(position) - int(self._last_ui_position)) >= 100
            or position <= 50
            or self.player.playbackState() != QMediaPlayer.PlayingState
        ):
            self._last_ui_position = int(position)
            self.current_time.setText(format_time(position))

        if self.current_source:
            self.history[self.current_source] = position

        self.check_ab(position)

    def duration_changed(
        self,
        duration
    ):

        self.position.setRange(
            0,
            max(
                0,
                duration
            )
        )

        self.total_time.setText(
            format_time(
                duration
            )
        )

    # ========================================================
    # AUDIO
    # ========================================================

    def set_volume(
        self,
        value
    ):

        self.audio.setVolume(
            value / 100
        )

    def toggle_mute(
        self
    ):

        self.audio.setMuted(
            not self.audio.isMuted()
        )

    def set_speed(
        self,
        text
    ):

        try:

            rate = float(
                text.replace(
                    "x",
                    ""
                )
            )

            self.player.setPlaybackRate(
                rate
            )

        except Exception:
            pass

    # ========================================================
    # A-B
    # ========================================================

    def toggle_ab(
        self
    ):

        position = self.player.position()

        if self.ab_start is None:

            self.ab_start = position

            self.ab_btn.setText(
                "A "
                + format_time(position)
            )

        elif self.ab_end is None:

            if position <= self.ab_start:
                return

            self.ab_end = position

            self.ab_btn.setText(
                "A-B ✓"
            )

        else:

            self.ab_start = None

            self.ab_end = None

            self.ab_btn.setText(
                "A-B"
            )

    def check_ab(
        self,
        position
    ):

        if (
            self.ab_start is not None
            and self.ab_end is not None
            and position >= self.ab_end
        ):

            self._seek_and_resume(
                self.ab_start,
                True,
                delay_ms=220
            )

    # ========================================================
    # FULLSCREEN SUBTITLE OVERLAY
    # ========================================================

    def _position_fullscreen_subtitle(self):
        """Position the top-level subtitle window over the fullscreen video."""
        overlay = getattr(self, "_fullscreen_subtitle", None)
        if overlay is None:
            return
        try:
            if not self.isFullScreen() or not overlay.isVisible():
                return
            top_left = self.video.mapToGlobal(QPoint(0, 0))
            video_w = max(1, self.video.width())
            video_h = max(1, self.video.height())

            width = max(320, min(int(video_w * 0.82), video_w - 48))
            height = max(92, min(190, int(video_h * 0.15)))
            bottom_margin = max(36, int(video_h * 0.055))
            x = top_left.x() + max(0, (video_w - width) // 2)
            y = top_left.y() + max(0, video_h - height - bottom_margin)

            overlay.setGeometry(x, y, width, height)
            overlay.raise_()
        except Exception:
            pass

    def _sync_fullscreen_subtitle_style(self, size=None):
        overlay = getattr(self, "_fullscreen_subtitle", None)
        if overlay is None:
            return
        if size is None:
            size = self.config.get("subtitle_size", 18)
        fullscreen_size = max(22, min(56, int(size * 1.65)))
        overlay.setStyleSheet(
            f"""
            QLabel#FullscreenSubtitle {{
                background: rgba(0, 0, 0, 205);
                color: white;
                border: 1px solid rgba(255,255,255,45);
                border-radius: 14px;
                padding: 12px 24px;
                font-size: {fullscreen_size}px;
                font-weight: 800;
            }}
            """
        )

    def _show_fullscreen_subtitle(self, text=None):
        overlay = getattr(self, "_fullscreen_subtitle", None)
        if overlay is None or not self.isFullScreen():
            return
        try:
            if text is not None:
                overlay.setText(str(text))
            if overlay.text().strip():
                self._sync_fullscreen_subtitle_style(self.config.get("subtitle_size", 18))
                overlay.show()
                self._position_fullscreen_subtitle()
                overlay.raise_()
            else:
                overlay.hide()
        except Exception:
            pass

    # ========================================================
    # FULLSCREEN + VIDEO CONTEXT MENU
    # ========================================================

    def _set_fullscreen_ui(self, enabled):
        """Show only the video surface while fullscreen is active."""
        if enabled:
            if self._fullscreen_ui_state is not None:
                return

            margins = self.player_page.layout().contentsMargins()
            self._fullscreen_ui_state = {
                "sidebar": self.sidebar.isVisible(),
                "menu": self.menuBar().isVisible(),
                "header": [w.isVisible() for w in self._player_header_widgets],
                "queue": self._queue_panel.isVisible(),
                "subtitle": self.subtitle_label.isVisible(),
                "status": self.status.isVisible(),
                "ready": self._status_ready_label.isVisible(),
                "timeline": self._timeline_widget.isVisible(),
                "controls": self.controls.isVisible(),
                "margins": margins,
                "spacing": self.player_page.layout().spacing(),
                "splitter_sizes": self._splitter.sizes(),
            }

            self.menuBar().hide()
            self.sidebar.hide()
            for widget in self._player_header_widgets:
                widget.hide()
            self._queue_panel.hide()
            self.subtitle_label.hide()
            self._sync_fullscreen_subtitle_style()
            QApplication.processEvents()
            self._show_fullscreen_subtitle(self._subtitle_last_text or "")
            self._position_fullscreen_subtitle()
            self.status.hide()
            self._status_ready_label.hide()
            self._timeline_widget.hide()
            self.controls.hide()

            self.player_page.layout().setContentsMargins(0, 0, 0, 0)
            self.player_page.layout().setSpacing(0)
            try:
                self._splitter.setSizes([max(1, self.player_page.width()), 0])
            except Exception:
                pass

        else:
            state = self._fullscreen_ui_state
            if state is None:
                return

            self.menuBar().setVisible(state["menu"])
            self.sidebar.setVisible(state["sidebar"])
            for widget, visible in zip(self._player_header_widgets, state["header"]):
                widget.setVisible(visible)
            self._queue_panel.setVisible(state["queue"])
            self._fullscreen_subtitle.hide()
            self.subtitle_label.setVisible(state["subtitle"])
            self.status.setVisible(state["status"])
            self._status_ready_label.setVisible(state["ready"])
            self._timeline_widget.setVisible(state["timeline"])
            self.controls.setVisible(state["controls"])

            self.player_page.layout().setContentsMargins(state["margins"])
            self.player_page.layout().setSpacing(state["spacing"])
            try:
                self._splitter.setSizes(state["splitter_sizes"])
            except Exception:
                self._splitter.setSizes([1120, 340])

            self._fullscreen_ui_state = None

    def toggle_fullscreen(
        self
    ):
        entering = not self.isFullScreen()
        if entering:
            self.showFullScreen()
            self._set_fullscreen_ui(True)
            QApplication.processEvents()
            self._position_fullscreen_subtitle()
            QTimer.singleShot(0, self._position_fullscreen_subtitle)
            QTimer.singleShot(60, self._position_fullscreen_subtitle)
            self.video.setFocus()
        else:
            try:
                self._fullscreen_subtitle.hide()
            except Exception:
                pass
            self._set_fullscreen_ui(False)
            self.showNormal()
            self.video.setFocus()

    def show_video_context_menu(self, global_pos):
        menu = QMenu(self)
        menu.setStyleSheet(STYLE)

        play_action = menu.addAction(
            "⏸  Pause" if self.player.playbackState() == QMediaPlayer.PlayingState else "▶  Play"
        )
        menu.addSeparator()
        back = menu.addAction("↶  Back 10 seconds")
        forward = menu.addAction("↷  Forward 10 seconds")
        back30 = menu.addAction("⏪  Back 30 seconds")
        forward30 = menu.addAction("⏩  Forward 30 seconds")

        menu.addSeparator()
        speed_menu = menu.addMenu("Playback Speed")
        for rate in (0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00, 2.50, 3.00, 4.00):
            action = speed_menu.addAction(f"{rate:.2f}x")
            action.setCheckable(True)
            action.setChecked(abs(self.player.playbackRate() - rate) < 0.01)
            action.triggered.connect(lambda checked=False, r=rate: self.player.setPlaybackRate(r))

        menu.addSeparator()
        mute_action = menu.addAction("🔇  Unmute" if self.audio.isMuted() else "🔊  Mute")
        fullscreen_action = menu.addAction(
            "⛶  Exit Fullscreen" if self.isFullScreen() else "⛶  Fullscreen"
        )

        menu.addSeparator()
        subtitles = menu.addMenu("Subtitles")
        subtitles.addAction("Load External Subtitle").triggered.connect(self.load_subtitle)
        subtitles.addAction("Load Sidecar Subtitle").triggered.connect(self.load_sidecar_subtitle)
        subtitles.addAction("Remove Subtitle").triggered.connect(self.remove_subtitle)
        subtitles.addAction("✨ Generate AI Subtitles").triggered.connect(self.ai_subtitles)
        subtitles.addAction("Edit Subtitles").triggered.connect(self.open_subtitle_editor)

        tools = menu.addMenu("Tools")
        tools.addAction("📷 Screenshot").triggered.connect(self.screenshot)
        tools.addAction("ℹ Media Information").triggered.connect(self.show_media_info)
        tools.addAction("🔖 Bookmarks").triggered.connect(self.show_bookmarks)
        tools.addAction("☆ Favorites").triggered.connect(self.toggle_favorite)
        tools.addAction("⚙ Settings").triggered.connect(self.show_settings)

        selected = menu.exec(global_pos)
        if selected is play_action:
            self.toggle_play()
        elif selected is back:
            self.seek_relative(-10000)
        elif selected is forward:
            self.seek_relative(10000)
        elif selected is back30:
            self.seek_relative(-30000)
        elif selected is forward30:
            self.seek_relative(30000)
        elif selected is mute_action:
            self.toggle_mute()
        elif selected is fullscreen_action:
            self.toggle_fullscreen()

    # ========================================================
    # SUBTITLE
    # ========================================================

    def load_sidecar_subtitle(
        self
    ):

        if not self.current_source:
            return

        base = os.path.splitext(
            self.current_source
        )[0]

        for extension in [
            ".srt",
            ".ass",
            ".ssa",
            ".vtt"
        ]:

            path = base + extension

            if os.path.exists(
                path
            ):

                self.parse_subtitle(
                    path
                )

                return

    def load_subtitle(
        self
    ):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Subtitle",
            "",
            "Subtitles (*.srt *.ass *.ssa *.vtt)"
        )

        if path:

            self.parse_subtitle(
                path
            )

    def remove_subtitle(
        self
    ):

        self.current_subtitles = []

        self.subtitle_label.clear()
        if hasattr(self, "_fullscreen_subtitle"):
            self._fullscreen_subtitle.clear()

    def parse_subtitle(
        self,
        path
    ):

        extension = (
            Path(path).suffix.lower()
        )

        try:

            if extension == ".srt":

                self.current_subtitles = (
                    self.read_srt(
                        path
                    )
                )

            elif extension == ".vtt":

                self.current_subtitles = (
                    self.read_vtt(
                        path
                    )
                )

            elif extension in {
                ".ass",
                ".ssa"
            }:

                self.current_subtitles = (
                    self.read_ass(
                        path
                    )
                )

            self._reset_subtitle_cache()
            self.status.setText(
                "Subtitle loaded: "
                + Path(path).name
            )

        except Exception as e:

            QMessageBox.warning(
                self,
                "Subtitle error",
                str(e)
            )

    def read_srt(
        self,
        path
    ):

        text = Path(
            path
        ).read_text(
            encoding="utf-8-sig",
            errors="replace"
        )

        blocks = re.split(
            r"\n\s*\n",
            text.strip()
        )

        result = []

        for block in blocks:

            lines = block.splitlines()

            timing_index = -1

            for i, line in enumerate(
                lines
            ):

                if "-->" in line:

                    timing_index = i

                    break

            if timing_index < 0:
                continue

            start_text, end_text = (
                x.strip()
                for x
                in lines[timing_index].split(
                    "-->"
                )
            )

            result.append(
                {
                    "start":
                    parse_timestamp(
                        start_text
                    ),
                    "end":
                    parse_timestamp(
                        end_text
                    ),
                    "text":
                    " ".join(
                        lines[
                            timing_index + 1:
                        ]
                    )
                }
            )

        return result

    def read_vtt(
        self,
        path
    ):

        text = Path(
            path
        ).read_text(
            encoding="utf-8-sig",
            errors="replace"
        )

        blocks = re.split(
            r"\n\s*\n",
            text.strip()
        )

        result = []

        for block in blocks:

            lines = block.splitlines()

            index = -1

            for i, line in enumerate(
                lines
            ):

                if "-->" in line:

                    index = i

                    break

            if index < 0:
                continue

            start_text, end_text = (
                x.strip()
                for x
                in lines[index].split(
                    "-->"
                )
            )

            result.append(
                {
                    "start":
                    parse_timestamp(
                        start_text
                    ),
                    "end":
                    parse_timestamp(
                        end_text
                    ),
                    "text":
                    " ".join(
                        lines[index + 1:]
                    )
                }
            )

        return result

    def read_ass(
        self,
        path
    ):

        import pysubs2

        subs = pysubs2.load(
            path
        )

        result = []

        for item in subs:

            result.append(
                {
                    "start":
                    item.start / 1000,
                    "end":
                    item.end / 1000,
                    "text":
                    item.text.replace(
                        "\\N",
                        "\n"
                    )
                }
            )

        return result

    def load_subtitle_file(self, path):
        """Load a simple SRT sidecar into the current subtitle list."""
        text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
        blocks = re.split(r"\n\s*\n", text.replace("\r\n", "\n").replace("\r", "\n"))
        parsed = []
        for block in blocks:
            lines = [line.strip("\ufeff") for line in block.split("\n") if line.strip()]
            if len(lines) < 2:
                continue
            timing_idx = 1 if "-->" in lines[1] else 0
            if timing_idx >= len(lines) or "-->" not in lines[timing_idx]:
                continue
            left, right = [x.strip() for x in lines[timing_idx].split("-->", 1)]
            start = parse_timestamp(left)
            end = parse_timestamp(right)
            subtitle_text = " ".join(lines[timing_idx + 1:]).strip()
            if subtitle_text:
                parsed.append({"start": start, "end": max(start, end), "text": subtitle_text})
        self.current_subtitles = parsed
        return parsed

    def _reset_subtitle_cache(self):
        self._subtitle_cache_id = 0
        self._subtitle_cache_len = -1
        self._subtitle_starts = []
        self._subtitle_last_index = -2
        self._subtitle_last_text = None

    def update_subtitle(
        self,
        position
    ):
        subtitles = self.current_subtitles

        if not subtitles:
            if self._subtitle_last_text != "":
                self.subtitle_label.clear()
                if hasattr(self, "_fullscreen_subtitle"):
                    self._fullscreen_subtitle.clear()
                    self._fullscreen_subtitle.hide()
                self._subtitle_last_text = ""
            return

        cache_id = id(subtitles)
        if cache_id != self._subtitle_cache_id or len(subtitles) != self._subtitle_cache_len:
            try:
                subtitles.sort(key=lambda item: float(item.get("start", 0.0)))
            except Exception:
                pass
            self._subtitle_starts = [float(item.get("start", 0.0)) for item in subtitles]
            self._subtitle_cache_id = cache_id
            self._subtitle_cache_len = len(subtitles)
            self._subtitle_last_index = -2
            self._subtitle_last_text = None

        current = position / 1000 + self.config.get("subtitle_delay", 0) / 1000
        index = bisect_right(self._subtitle_starts, current) - 1

        text = ""
        if 0 <= index < len(subtitles):
            item = subtitles[index]
            if float(item.get("start", 0.0)) <= current <= float(item.get("end", 0.0)):
                text = str(item.get("text", "") or "")

        if index != self._subtitle_last_index or text != self._subtitle_last_text:
            self._subtitle_last_index = index
            self._subtitle_last_text = text
            self.subtitle_label.setText(text)
            if hasattr(self, "_fullscreen_subtitle"):
                self._fullscreen_subtitle.setText(text)
                if self.isFullScreen():
                    self._show_fullscreen_subtitle(text)
                elif not text:
                    self._fullscreen_subtitle.hide()

        size = self.config.get("subtitle_size", 18)
        if size != self._subtitle_style_size:
            self._subtitle_style_size = size
            self.subtitle_label.setStyleSheet(
                f"""
                QLabel#Subtitle {{
                    background:rgba(0,0,0,175);
                    color:white;
                    border-radius:9px;
                    padding:8px 16px;
                    font-size:{size}px;
                    font-weight:600;
                }}
                """
            )
            self._sync_fullscreen_subtitle_style(size)

    def ai_subtitles(
        self
    ):
        """Start local Whisper subtitle generation without blocking playback."""
        source_file = str(self.current_source or "")

        if not source_file:
            QMessageBox.information(
                self,
                "AI Subtitles",
                "Open a media file first."
            )
            return

        if source_file.startswith(("http://", "https://", "rtsp://")):
            QMessageBox.warning(
                self,
                "AI Subtitles",
                "AI subtitles currently require a local media file."
            )
            return

        if not os.path.isfile(source_file):
            QMessageBox.warning(
                self,
                "AI Subtitles",
                "The selected media file no longer exists."
            )
            return

        # Fail early with a useful message if faster-whisper is missing.
        try:
            import faster_whisper  # noqa: F401
        except Exception as exc:
            QMessageBox.warning(
                self,
                "faster-whisper required",
                "Install the local AI subtitle engine with:\n\n"
                "pip install --upgrade faster-whisper\n\n"
                f"Import error: {exc}"
            )
            self.log_activity(f"AI subtitles unavailable: faster-whisper import failed — {exc}")
            return

        if getattr(self, "_ai_thread", None) is not None:
            try:
                if self._ai_thread.isRunning():
                    self.status.setText("AI subtitle generation is already running…")
                    return
            except RuntimeError:
                self._ai_thread = None
                self._ai_worker = None

        dialog = QDialog(self)
        dialog.setWindowTitle("✨ AI Subtitle Studio")
        dialog.resize(560, 360)
        dialog.setModal(False)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        layout = QVBoxLayout(dialog)

        title = QLabel("✨ Generate Automatic Subtitles")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(title)

        note = QLabel(
            "Choose a Whisper model, language and device. The video keeps playing "
            "while AI transcription runs in the background. Audio is decoded directly "
            "from the media file; FFmpeg is not required for AI subtitles."
        )
        note.setWordWrap(True)
        note.setStyleSheet(f"color:{MUTED};")
        layout.addWidget(note)

        model = QComboBox()
        model.addItems(["tiny", "base", "small", "medium", "large-v3"])
        saved_model = self.config.get("ai_model", "base")
        if saved_model not in ["tiny", "base", "small", "medium", "large-v3"]:
            saved_model = "base"
        model.setCurrentText(saved_model)
        layout.addWidget(QLabel("Whisper model"))
        layout.addWidget(model)

        language = QComboBox()
        language.addItems(list(LANGUAGE_MAP.keys()))
        saved_language = self.config.get("ai_language", "Auto Detect")
        if saved_language in LANGUAGE_MAP:
            language.setCurrentText(saved_language)
        layout.addWidget(QLabel("Language"))
        layout.addWidget(language)

        device = QComboBox()
        device.addItems(["Auto", "CPU", "GPU"])
        saved_device = str(self.config.get("ai_device", "auto")).lower()
        device.setCurrentText({"auto": "Auto", "cpu": "CPU", "gpu": "GPU", "cuda": "GPU"}.get(saved_device, "Auto"))
        layout.addWidget(QLabel("Processing device"))
        layout.addWidget(device)

        progress = QProgressBar()
        progress.setRange(0, 100)
        layout.addWidget(progress)

        status = QLabel("Ready")
        status.setStyleSheet(f"color:{MUTED};")
        layout.addWidget(status)

        buttons = QDialogButtonBox()
        generate = buttons.addButton("Generate", QDialogButtonBox.AcceptRole)
        cancel = buttons.addButton("Close", QDialogButtonBox.RejectRole)
        layout.addWidget(buttons)

        def update_ui(value, text):
            self.log_activity(f"AI subtitles: {text} ({value}%)")
            self._v30_task_update("AI Subtitle Generation", f"{text} ({value}%)")
            self.status.setText(f"AI: {text}")
            self.ai_badge.setText("AI BUSY")
            try:
                progress.setValue(value)
                status.setText(text)
            except RuntimeError:
                pass

        def start():
            nonlocal source_file
            if getattr(self, "_ai_thread", None) is not None:
                try:
                    if self._ai_thread.isRunning():
                        return
                except RuntimeError:
                    pass

            self._ai_job_started_at = time.time()
            self._v30_task_start("AI Subtitle Generation", f"Starting {model.currentText()} model")
            selected_model = model.currentText()
            selected_device = device.currentText().lower()
            selected_language = language.currentText()
            language_code = LANGUAGE_MAP.get(selected_language)

            self.config["ai_model"] = selected_model
            self.config["ai_device"] = selected_device
            self.config["ai_language"] = selected_language
            write_json(CONFIG_FILE, self.config)

            self.log_activity(
                f"AI subtitles started: {Path(source_file).name} | "
                f"model={selected_model} | device={selected_device} | language={selected_language}"
            )

            worker = WhisperWorker(
                source_file,
                selected_model,
                language_code,
                selected_device,
            )
            thread = QThread()
            worker.moveToThread(thread)

            thread.started.connect(worker.run)
            worker.progress.connect(update_ui)

            def finish(data):
                try:
                    self.transcript = list(data.get("segments", []))
                    self.current_subtitles = list(self.transcript)
                    self.save_ai_srt(source_file)
                except Exception:
                    err = traceback.format_exc()
                    self.log_activity(f"AI subtitle save failed:\n{err}")
                    self.ai_badge.setText("AI ERROR")
                    self.status.setText("AI generated, but saving the SRT failed")
                    if self.config.get("debug", False):
                        print(err)
                    try:
                        thread.quit()
                    except RuntimeError:
                        pass
                    return

                elapsed = (
                    0.0 if self._ai_job_started_at is None
                    else time.time() - self._ai_job_started_at
                )
                self.ai_badge.setText("AI READY")
                self.status.setText(
                    f"AI subtitles ready — {len(self.transcript)} segments"
                )
                self._v30_task_finish("AI Subtitle Generation", "Completed")
                self.log_activity(
                    f"AI subtitles complete — {len(self.transcript)} segments in {elapsed:.1f}s "
                    f"(model={data.get('model', selected_model)}, device={data.get('device', selected_device)})"
                )
                self.update_subtitle(self.player.position())
                try:
                    thread.quit()
                except RuntimeError:
                    pass

            def failure(error):
                self.ai_badge.setText("AI ERROR")
                self.status.setText("AI subtitle generation failed — see Activity Log")
                # Preserve the full traceback in the background log even when debug mode is off.
                self._v30_task_finish("AI Subtitle Generation", "Failed")
                self.log_activity("AI SUBTITLE ERROR:\n" + str(error).strip())
                if self.config.get("debug", False):
                    print(error)
                try:
                    thread.quit()
                except RuntimeError:
                    pass

            def thread_finished():
                self.log_activity("AI background worker stopped.")
                self._ai_thread = None
                self._ai_worker = None
                try:
                    dialog.close()
                except RuntimeError:
                    pass
                try:
                    thread.deleteLater()
                    worker.deleteLater()
                except RuntimeError:
                    pass

            worker.finished.connect(finish)
            worker.failed.connect(failure)
            thread.finished.connect(thread_finished)

            self._ai_thread = thread
            self._ai_worker = worker

            self.status.setText("AI: Preparing audio…")
            self.ai_badge.setText("AI BUSY")
            dialog.hide()
            thread.start()

        generate.clicked.connect(start)
        cancel.clicked.connect(dialog.close)

        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def save_ai_srt(
        self,
        source_file=None
    ):
        source = str(source_file or self.current_source or "")
        if not source:
            raise RuntimeError("No source media is selected.")

        output = (
            SUBTITLE_DIR
            / (
                Path(source).stem
                + ".ai.srt"
            )
        )

        lines = []
        for index, segment in enumerate(self.transcript, 1):
            text = str(segment.get("text", "")).strip()
            if not text:
                continue
            lines.extend([
                str(index),
                (
                    srt_timestamp(float(segment.get("start", 0)))
                    + " --> "
                    + srt_timestamp(float(segment.get("end", 0)))
                ),
                text,
                "",
            ])

        output.write_text(
            "\n".join(lines),
            encoding="utf-8"
        )

        self.status.setText("AI subtitle saved.")
        self.log_activity(f"AI SRT saved: {output}")
        return output

    # ========================================================
    # TRANSCRIPT
    # ========================================================

    def show_transcript(
        self
    ):

        segments = (
            self.transcript
            or self.current_subtitles
        )

        if not segments:

            QMessageBox.information(
                self,
                "Transcript",
                "Generate subtitles first."
            )

            return

        dialog = TranscriptDialog(
            segments,
            self
        )

        dialog.jump.connect(
            self.player.setPosition
        )

        dialog.exec()

    # ========================================================
    # ONLINE AI ASSISTANT
    # ========================================================

    def show_ai_assistant(
        self
    ):

        if not self.transcript:

            QMessageBox.information(
                self,
                "AI Assistant",
                "Generate an AI transcript first."
            )

            return

        api_key = (
            self.config.get(
                "openai_api_key",
                ""
            ).strip()
            or os.environ.get(
                "NOVA_OPENAI_API_KEY",
                ""
            ).strip()
        )

        if not api_key:

            QMessageBox.warning(
                self,
                "AI Assistant",
                "Configure your online AI API key in Settings."
            )

            return

        dialog = QDialog(
            self
        )

        dialog.setWindowTitle(
            "✨ Nova AI Assistant"
        )

        dialog.resize(
            900,
            650
        )

        layout = QVBoxLayout(
            dialog
        )

        title = QLabel(
            "✨ Ask about this video"
        )

        title.setFont(
            QFont(
                "Segoe UI",
                21,
                QFont.Weight.Bold
            )
        )

        layout.addWidget(
            title
        )

        chat = QTextEdit()

        chat.setReadOnly(
            True
        )

        layout.addWidget(
            chat,
            1
        )

        row = QHBoxLayout()

        question = QLineEdit()

        question.setPlaceholderText(
            "Ask something about the transcript..."
        )

        ask = QPushButton(
            "Ask"
        )

        row.addWidget(
            question,
            1
        )

        row.addWidget(
            ask
        )

        layout.addLayout(
            row
        )

        def ask_ai():

            text = question.text().strip()

            if not text:
                return

            transcript = "\n".join(
                [
                    (
                        "["
                        + format_time(
                            s["start"] * 1000
                        )
                        + "] "
                        + s["text"]
                    )
                    for s in self.transcript
                ]
            )

            if len(transcript) > 160000:

                transcript = transcript[
                    :160000
                ]

            prompt = f"""
You are Nova AI inside a desktop media player.

Answer the user question using ONLY the transcript.

Include timestamps whenever useful.
Do not invent information.

TRANSCRIPT:
{transcript}

QUESTION:
{text}
"""

            chat.append(
                "<b>You:</b> "
                + text
            )

            question.clear()

            answer = self.online_ai_request(
                api_key,
                prompt
            )

            chat.append(
                "<b>Nova:</b><br>"
                + answer.replace(
                    "\n",
                    "<br>"
                )
            )

        ask.clicked.connect(
            ask_ai
        )

        question.returnPressed.connect(
            ask_ai
        )

        dialog.exec()

    def online_ai_request(
        self,
        api_key,
        prompt
    ):

        model = (
            self.config.get(
                "openai_model",
                ""
            ).strip()
        )

        if not model:

            return (
                "No online AI model is configured."
            )

        try:

            payload = json.dumps(
                {
                    "model": model,
                    "input": prompt
                }
            ).encode(
                "utf-8"
            )

            request = urllib.request.Request(
                "https://api.openai.com/v1/responses",
                data=payload,
                headers={
                    "Content-Type":
                    "application/json",
                    "Authorization":
                    "Bearer "
                    + api_key
                },
                method="POST"
            )

            with urllib.request.urlopen(
                request,
                timeout=180
            ) as response:

                data = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

            text = (
                data.get(
                    "output_text"
                )
                or ""
            )

            if text:
                return text

            pieces = []

            for item in data.get(
                "output",
                []
            ):

                for content in item.get(
                    "content",
                    []
                ):

                    value = content.get(
                        "text"
                    )

                    if value:
                        pieces.append(
                            value
                        )

            return "\n".join(
                pieces
            ) or "No response."

        except urllib.error.HTTPError as e:

            try:

                detail = e.read().decode(
                    errors="replace"
                )

            except Exception:

                detail = str(e)

            return (
                f"AI request failed: "
                f"HTTP {e.code}\n{detail}"
            )

        except Exception as e:

            return (
                "AI request failed: "
                + str(e)
            )

    # ========================================================
    # AI CHAPTERS
    # ========================================================

    def generate_chapters(
        self
    ):

        if not self.transcript:

            QMessageBox.information(
                self,
                "Chapters",
                "Generate an AI transcript first."
            )

            return

        api_key = (
            self.config.get(
                "openai_api_key",
                ""
            ).strip()
            or os.environ.get(
                "NOVA_OPENAI_API_KEY",
                ""
            ).strip()
        )

        if not api_key:

            QMessageBox.warning(
                self,
                "Chapters",
                "Configure your online AI API key first."
            )

            return

        transcript = "\n".join(
            [
                "["
                + format_time(
                    s["start"] * 1000
                )
                + "] "
                + s["text"]
                for s in self.transcript
            ]
        )

        prompt = f"""
Analyze this transcript and create useful video chapters.

Return ONLY:

HH:MM:SS | Chapter title

Use a reasonable number of chapters and real timestamps.

TRANSCRIPT:
{transcript[:150000]}
"""

        result = self.online_ai_request(
            api_key,
            prompt
        )

        dialog = QDialog(
            self
        )

        dialog.setWindowTitle(
            "AI Chapters"
        )

        dialog.resize(
            650,
            480
        )

        layout = QVBoxLayout(
            dialog
        )

        list_widget = QListWidget()

        for line in result.splitlines():

            match = re.match(
                r"\s*(\d{2}:\d{2}:\d{2})\s*\|\s*(.+)",
                line
            )

            if not match:
                continue

            stamp = match.group(1)
            title = match.group(2)

            item = QListWidgetItem(
                f"{stamp}  •  {title}"
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                int(
                    parse_timestamp(stamp)
                    * 1000
                )
            )

            list_widget.addItem(
                item
            )

        layout.addWidget(
            list_widget
        )

        list_widget.itemDoubleClicked.connect(
            lambda item:
            self.player.setPosition(
                item.data(
                    Qt.ItemDataRole.UserRole
                )
            )
        )

        close = QPushButton(
            "Close"
        )

        close.clicked.connect(
            dialog.accept
        )

        layout.addWidget(
            close
        )

        dialog.exec()

    # ========================================================
    # TRANSLATION
    # ========================================================

    def translate_subtitles(
        self
    ):

        if not self.transcript:

            QMessageBox.information(
                self,
                "Translation",
                "Generate an AI transcript first."
            )

            return

        api_key = (
            self.config.get(
                "openai_api_key",
                ""
            ).strip()
            or os.environ.get(
                "NOVA_OPENAI_API_KEY",
                ""
            ).strip()
        )

        if not api_key:

            QMessageBox.warning(
                self,
                "Translation",
                "Configure your online AI API key first."
            )

            return

        target, ok = QInputDialog.getItem(
            self,
            "Translate subtitles",
            "Language:",
            [
                "Hindi",
                "Punjabi",
                "English",
                "Spanish",
                "French",
                "German",
                "Japanese",
                "Chinese",
                "Korean"
            ],
            0,
            False
        )

        if not ok:
            return

        transcript = "\n".join(
            [
                (
                    str(i + 1)
                    + " | "
                    + srt_timestamp(
                        s["start"]
                    )
                    + " --> "
                    + srt_timestamp(
                        s["end"]
                    )
                    + " | "
                    + s["text"]
                )
                for i, s in enumerate(
                    self.transcript
                )
            ]
        )

        prompt = f"""
Translate the subtitle transcript into {target}.

Preserve:
- numbering
- start timestamps
- end timestamps

Return only subtitle lines.

TRANSCRIPT:
{transcript[:150000]}
"""

        result = self.online_ai_request(
            api_key,
            prompt
        )

        output = (
            SUBTITLE_DIR
            / (
                Path(
                    self.current_source
                ).stem
                + f".{target}.txt"
            )
        )

        output.write_text(
            result,
            encoding="utf-8"
        )

        QMessageBox.information(
            self,
            "Translation complete",
            "Translated subtitle text saved to:\n"
            + str(output)
        )

    # ========================================================
    # SCREENSHOT
    # ========================================================

    def screenshot(
        self
    ):

        if not self.current_source:

            return

        image = self.video.grab()

        filename = (
            Path(
                self.current_source
            ).stem
            + "_"
            + datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
            + ".png"
        )

        path = (
            SCREENSHOT_DIR
            / filename
        )

        image.save(
            str(path),
            "PNG"
        )

        self.status.setText(
            "Screenshot saved: "
            + str(path)
        )

    # ========================================================
    # BOOKMARKS
    # ========================================================

    def add_bookmark(
        self
    ):

        if not self.current_source:

            return

        position = self.player.position()

        self.bookmarks.setdefault(
            self.current_source,
            []
        )

        self.bookmarks[
            self.current_source
        ].append(
            position
        )

        write_json(
            BOOKMARK_FILE,
            self.bookmarks
        )

        self.status.setText(
            "Bookmark added at "
            + format_time(position)
        )

    def show_bookmarks(
        self
    ):

        if not self.current_source:

            return

        bookmarks = self.bookmarks.get(
            self.current_source,
            []
        )

        if not bookmarks:

            QMessageBox.information(
                self,
                "Bookmarks",
                "No bookmarks for this media."
            )

            return

        menu = QMenu(
            self
        )

        for position in bookmarks:

            action = menu.addAction(
                format_time(position)
            )

            action.triggered.connect(
                lambda checked=False,
                p=position:
                self.player.setPosition(
                    p
                )
            )

        menu.exec(
            QCursor.pos()
        )

    # ========================================================
    # MEDIA INFO
    # ========================================================

    def show_media_info(
        self
    ):

        if not self.current_source:
            return

        dialog = MediaInfoDialog(
            self.current_source,
            self.player,
            self
        )

        dialog.exec()

    # ========================================================
    # SETTINGS
    # ========================================================

    def show_settings(
        self
    ):

        dialog = SettingsDialog(
            self.config,
            self
        )

        if dialog.exec():

            dialog.apply()

            write_json(
                CONFIG_FILE,
                self.config
            )

            self.restore_settings()

            self.status.setText(
                "Settings saved."
            )

    def restore_settings(
        self
    ):

        volume = self.config.get(
            "volume",
            75
        )

        speed = self.config.get(
            "speed",
            1.0
        )

        self.volume.setValue(
            volume
        )

        self.audio.setVolume(
            volume / 100
        )

        self.speed.setCurrentText(
            f"{speed:.2f}x"
        )

        self.sidebar.setVisible(
            self.config.get(
                "show_sidebar",
                True
            )
        )

        self.eq_values = self.config.get(
            "equalizer",
            [0] * 10
        )

        saved_theme = self.config.get("theme", "Nova Dark")
        if saved_theme not in THEME_SPECS:
            saved_theme = "Nova Dark"
        self.apply_theme(saved_theme)

    # ========================================================
    # MEDIA STATUS
    # ========================================================

    def media_status(
        self,
        status
    ):
        if status == QMediaPlayer.EndOfMedia:
            self.next()
            return

        # Starting on LoadedMedia can show a burst of decoder work on the
        # first frames. Prefer BufferedMedia so the decoder has data queued.
        if status == QMediaPlayer.LoadedMedia and self._pending_autoplay:
            self.status.setText("Buffering first frames…")
            QTimer.singleShot(220, self._startup_buffer_fallback)
            return

        if status == QMediaPlayer.BufferedMedia and self._pending_autoplay:
            self._start_pending_playback()

    def _startup_buffer_fallback(self):
        if not self._pending_autoplay or not self.current_source:
            return
        # If buffering has completed by now, media_status(BufferedMedia) has
        # already handled startup. Otherwise start once rather than waiting
        # indefinitely on unusual containers/codecs.
        try:
            if self.player.mediaStatus() in (QMediaPlayer.BufferedMedia, QMediaPlayer.LoadedMedia):
                self._start_pending_playback()
        except Exception:
            self._start_pending_playback()

    def media_error(
        self,
        error,
        message
    ):

        if message:

            self.status.setText(
                "Playback error: "
                + message
            )

    # ========================================================
    # TIMER
    # ========================================================

    def timer_tick(
        self
    ):

        if self.current_source:

            self.update_subtitle(
                self.player.position()
            )

        # V01: periodically persist session state so an unexpected exit can
        # recover the current media and position.
        try:
            self._v30_session_heartbeat()
        except Exception:
            pass

    # ========================================================
    # DRAG & DROP
    # ========================================================

    def dragEnterEvent(
        self,
        event
    ):

        if event.mimeData().hasUrls():

            event.acceptProposedAction()

    def dropEvent(
        self,
        event
    ):

        files = []

        for url in event.mimeData().urls():

            if not url.isLocalFile():
                continue

            path = url.toLocalFile()

            if is_media(path):

                files.append(
                    path
                )

        if files:

            self.add_files(
                files
            )

            self.play_file(
                files[0]
            )

            self.show_player()

    # ========================================================
    # KEYBOARD
    # ========================================================

    def keyPressEvent(
        self,
        event
    ):

        key = event.key()

        if key == Qt.Key_Escape and self.isFullScreen():

            self.toggle_fullscreen()
            event.accept()
            return

        if key == Qt.Key_Space:

            self.toggle_play()

        elif key == Qt.Key_Left:

            self.seek_relative(
                -self.seek_amount()
            )

        elif key == Qt.Key_Right:

            self.seek_relative(
                self.seek_amount()
            )

        elif key == Qt.Key_Up:

            self.volume.setValue(
                min(
                    100,
                    self.volume.value() + 5
                )
            )

        elif key == Qt.Key_Down:

            self.volume.setValue(
                max(
                    0,
                    self.volume.value() - 5
                )
            )

        elif key == Qt.Key_M:

            self.toggle_mute()

        elif key == Qt.Key_F:

            self.toggle_fullscreen()

        elif key == Qt.Key_B:

            self.add_bookmark()

        elif key == Qt.Key_T:

            self.show_transcript()

        elif key == Qt.Key_I:

            self.show_media_info()

        elif event.key() == Qt.Key_K and event.modifiers() & Qt.ControlModifier:
            self.show_command_palette()
            event.accept()
        elif event.key() == Qt.Key_I and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
            self.show_ai_center()
            event.accept()
        elif event.key() == Qt.Key_Comma:
            self.frame_backward(); event.accept()
        elif event.key() == Qt.Key_Period:
            self.frame_forward(); event.accept()
        else:
            super().keyPressEvent(event)

    # ========================================================
    # EXTRA FEATURE SETUP
    # ========================================================

    def setup_extra_features(self):
        self.update_home_extras()
        self.apply_theme(self.config.get("theme", "Nova Dark"))

    def update_home_extras(self):
        try:
            self.home_cards[0].setText(str(len(self.playlist_files)))
            self.home_cards[1].setText(str(len(self.playlist_files)))
            self.home_cards[2].setText("LOCAL")
            self.home_cards[3].setText(str(len(self.library)))
        except Exception:
            pass

    # ========================================================
    # SUBTITLE EDITOR
    # ========================================================

    def open_subtitle_editor(self):
        if not self.current_subtitles:
            QMessageBox.information(self, "Subtitle Editor", "Load or generate subtitles first.")
            return
        dialog = SubtitleEditorDialog(self.current_subtitles, self)
        dialog.changed.connect(self.subtitle_editor_changed)
        dialog.exec()

    def subtitle_editor_changed(self, subtitles):
        self.current_subtitles = subtitles
        self.status.setText("Subtitle edits applied.")

    # ========================================================
    # PLAYLIST MANAGER
    # ========================================================

    def open_playlist_manager(self):
        dialog = PlaylistManagerDialog(self.playlist_files, self)
        dialog.changed.connect(self.playlist_manager_changed)
        dialog.exec()

    def playlist_manager_changed(self, paths):
        self.playlist_files = paths
        self.populate_playlist_after_manager()
        self.save_playlist()

    def populate_playlist_after_manager(self):
        self.playlist.clear()
        for path in self.playlist_files:
            item = QListWidgetItem(Path(path).name)
            item.setData(Qt.ItemDataRole.UserRole, path)
            item.setToolTip(path)
            self.playlist.addItem(item)

    # ========================================================
    # SLEEP TIMER
    # ========================================================

    def open_sleep_timer(self):
        current = 0
        dialog = SleepTimerDialog(current, self)
        dialog.minutes_changed.connect(self.set_sleep_timer)
        dialog.exec()

    def set_sleep_timer(self, minutes):
        if self.sleep_timer:
            self.sleep_timer.stop()
            self.sleep_timer.deleteLater()
            self.sleep_timer = None
        if minutes <= 0:
            self.status.setText("Sleep timer disabled.")
            return
        self.sleep_timer = QTimer(self)
        self.sleep_timer.setSingleShot(True)
        self.sleep_timer.timeout.connect(self.sleep_timer_fired)
        self.sleep_timer.start(minutes * 60 * 1000)
        self.status.setText(f"Sleep timer: {minutes} minute(s).")

    def sleep_timer_fired(self):
        self.player.pause()
        self.status.setText("Sleep timer stopped playback.")

    # ========================================================
    # CONVERTER
    # ========================================================

    def open_converter(self):
        if not self.current_source:
            QMessageBox.information(self, "Convert", "Open a media file first.")
            return
        ConvertDialog(self.current_source, self).exec()

    # ========================================================
    # AUDIO OUTPUT
    # ========================================================

    def open_audio_output(self):
        try:
            from PySide6.QtMultimedia import QMediaDevices
            current = self.audio.device()
            dialog = AudioOutputDialog(current, self)
            if dialog.exec():
                device = dialog.device()
                if device:
                    self.audio.setDevice(device)
                    self.status.setText("Audio output changed.")
        except Exception as e:
            QMessageBox.warning(self, "Audio Output", str(e))

    # ========================================================
    # EQUALIZER
    # ========================================================

    def open_equalizer(self):
        dialog = EqualizerDialog(self.eq_values, self)
        dialog.values_changed.connect(self.equalizer_changed)
        dialog.exec()

    def equalizer_changed(self, values):
        self.eq_values = values
        self.config["equalizer"] = values
        write_json(CONFIG_FILE, self.config)
        self.status.setText("Equalizer profile saved.")

    # ========================================================
    # V01 WORKSPACE / PRODUCTIVITY FEATURES
    # ========================================================

    def _init_v30_features(self):
        self._v30_tasks = []
        self._v30_last_session_write = 0.0
        self._v30_previous_session = read_json(SESSION_FILE, {})
        self._mini_window = None
        self._mini_video_parent = None
        self._mini_active = False
        self._v30_session_checked = False
        self._v30_session_restore_source = ""
        self._v30_add_shortcuts = True
        try:
            self._v30_session_write(force=True, clean_exit=False)
            QTimer.singleShot(600, self._offer_session_recovery)
        except Exception as exc:
            self.log_activity(f"V01 session initialization failed: {exc}")

    def _v30_task_start(self, name, detail=""):
        self._v30_task_finish(name, "Replaced")
        self._v30_tasks.append({"name": name, "status": "RUNNING", "detail": detail, "started": time.time()})
        self.log_activity(f"Task started: {name} — {detail}")

    def _v30_task_update(self, name, detail=""):
        for task in reversed(self._v30_tasks):
            if task.get("name") == name and task.get("status") == "RUNNING":
                task["detail"] = detail
                return

    def _v30_task_finish(self, name, status="Completed"):
        for task in reversed(self._v30_tasks):
            if task.get("name") == name and task.get("status") == "RUNNING":
                task["status"] = status.upper()
                task["detail"] = status
                return

    def show_v30_library(self):
        dlg = NovaLibraryDialog(self, self)
        dlg.show(); dlg.raise_(); dlg.activateWindow(); self._open_dialogs.append(dlg)

    def show_continue_watching(self):
        dlg = NovaLibraryDialog(self, self)
        dlg.setWindowTitle("Nova — Continue Watching")
        dlg.filter.setCurrentText("Continue Watching")
        dlg.show(); dlg.raise_(); dlg.activateWindow(); self._open_dialogs.append(dlg)

    def show_universal_search(self):
        dlg = NovaUniversalSearchDialog(self, self)
        dlg.show(); dlg.raise_(); dlg.activateWindow(); self._open_dialogs.append(dlg)

    def show_subtitle_center(self):
        dlg = NovaSubtitleCenterDialog(self, self)
        dlg.show(); dlg.raise_(); dlg.activateWindow(); self._open_dialogs.append(dlg)

    def show_intelligence(self):
        dlg = NovaIntelligenceDialog(self, self)
        dlg.show(); dlg.raise_(); dlg.activateWindow(); self._open_dialogs.append(dlg)

    def show_task_center(self):
        dlg = NovaTaskCenterDialog(self, self)
        dlg.show(); dlg.raise_(); dlg.activateWindow(); self._open_dialogs.append(dlg)

    def show_now_playing(self):
        dlg = NovaNowPlayingDialog(self, self)
        dlg.show(); dlg.raise_(); dlg.activateWindow(); self._open_dialogs.append(dlg)

    def activate_cinema_mode(self):
        # Cinema Mode uses the existing robust fullscreen implementation and
        # keeps the subtitle overlay working on native Windows video surfaces.
        if not self.isFullScreen():
            self.toggle_fullscreen()
        self.status.setText("Cinema Mode active")

    def toggle_mini_player(self):
        if self._mini_active:
            self._restore_from_mini_player()
            return
        if not self.current_source:
            QMessageBox.information(self, "Mini Player", "Open a media file first.")
            return
        try:
            self._mini_video_parent = self.video.parentWidget()
            if hasattr(self, "video_card"):
                self.video_card.layout().removeWidget(self.video)
            self._video_side.hide()
            self._mini_window = MiniPlayerWindow(self, self.video)
            self._mini_window.closed.connect(self._restore_from_mini_player)
            screen = QApplication.primaryScreen()
            if screen:
                geo = screen.availableGeometry()
                self._mini_window.move(geo.right() - self._mini_window.width() - 30, geo.bottom() - self._mini_window.height() - 50)
            self._mini_active = True
            self._mini_window.show()
            self.player.setVideoOutput(self.video)
            self.log_activity("Mini Player activated.")
        except Exception as exc:
            self._mini_active = False
            QMessageBox.warning(self, "Mini Player", f"Could not open Mini Player:\n{exc}")

    def _restore_from_mini_player(self):
        if not getattr(self, "_mini_active", False):
            return
        try:
            mini = self._mini_window
            if mini is not None:
                try:
                    mini.blockSignals(True)
                    mini.hide()
                except Exception:
                    pass
                try:
                    mini.deleteLater()
                except Exception:
                    pass
            self._mini_window = None
            if hasattr(self, "video_card"):
                self.video.setParent(self.video_card)
                self.video_card.layout().addWidget(self.video)
                self._video_side.show()
            self.player.setVideoOutput(self.video)
            self._mini_active = False
            self.log_activity("Mini Player restored to main interface.")
            self.showNormal()
            self.raise_(); self.activateWindow()
        except Exception as exc:
            self._mini_active = False
            self.log_activity(f"Mini Player restore failed: {exc}")

    def _session_payload(self, clean_exit=False):
        try:
            speed = float(self.speed.currentText().replace("x", ""))
        except Exception:
            speed = 1.0
        return {
            "clean_exit": bool(clean_exit),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "current_source": str(self.current_source or ""),
            "position": int(self.player.position() if self.current_source else 0),
            "duration": int(self.player.duration() if self.current_source else 0),
            "playlist": list(self.playlist_files),
            "theme": self.config.get("theme", "Nova Dark"),
            "volume": int(self.volume.value()) if hasattr(self, "volume") else 75,
            "speed": speed,
            "was_playing": self.player.playbackState() == QMediaPlayer.PlayingState if hasattr(self, "player") else False,
        }

    def _v30_session_write(self, force=False, clean_exit=False):
        now = time.time()
        if not force and now - getattr(self, "_v30_last_session_write", 0.0) < 4:
            return
        self._v30_last_session_write = now
        write_json(SESSION_FILE, self._session_payload(clean_exit=clean_exit))

    def _v30_session_heartbeat(self):
        if getattr(self, "current_source", ""):
            path = self.current_source
            try:
                pos = int(self.player.position())
                if pos > 0:
                    self.history[path] = pos
            except Exception:
                pass
        self._v30_session_write(force=False, clean_exit=False)

    def _offer_session_recovery(self):
        if self._v30_session_checked:
            return
        self._v30_session_checked = True
        session = getattr(self, "_v30_previous_session", {})
        if not session or session.get("clean_exit", True):
            return
        source = str(session.get("current_source", "") or "")
        if not source or not os.path.isfile(source):
            return
        dlg = NovaSessionRecoveryDialog(session, self)
        result = dlg.exec()
        if result == QDialog.DialogCode.Accepted and dlg.restore_requested:
            self._restore_session_payload(session)
        else:
            self.log_activity("Previous session skipped; Nova started fresh.")

    def recover_last_session(self):
        session = read_json(SESSION_FILE, {})
        if not session:
            QMessageBox.information(self, "Session Recovery", "No saved session is available.")
            return
        self._restore_session_payload(session)

    def _restore_session_payload(self, session):
        playlist = [p for p in session.get("playlist", []) if os.path.isfile(p) and is_media(p)]
        if playlist:
            self.add_files(playlist)
        source = str(session.get("current_source", "") or "")
        if source and os.path.isfile(source):
            self.play_file(source)
            self._pending_start_position = int(session.get("position", 0) or 0)
            self._pending_source = source
        theme = session.get("theme")
        if theme in THEME_SPECS:
            self.apply_theme(theme)
        if "volume" in session:
            try:
                self.volume.setValue(int(session["volume"]))
                self.audio.setVolume(self.volume.value() / 100)
            except Exception:
                pass
        self.status.setText("Previous session restored.")
        self.log_activity("Previous Nova session restored.")

    def _v30_mark_clean_exit(self):
        try:
            self._v30_session_write(force=True, clean_exit=True)
        except Exception:
            pass


    # ========================================================
    # FAVORITES
    # ========================================================

    def toggle_favorite(self):
        if not self.current_source:
            return
        if self.current_source in self.favorites:
            self.favorites.remove(self.current_source)
            self.status.setText("Removed from favorites.")
        else:
            self.favorites.add(self.current_source)
            self.status.setText("Added to favorites.")
        write_json(APP_DATA / "favorites.json", list(self.favorites))
        self.update_favorite_button()

    def update_favorite_button(self):
        try:
            self.fav_button.setText(
                "★" if self.current_source in self.favorites else "☆"
            )
        except Exception:
            pass

    # ========================================================
    # SAVE / LOAD FAVORITES
    # ========================================================

    def show_favorites(self):
        paths = [p for p in self.playlist_files if p in self.favorites and os.path.exists(p)]
        if not paths:
            QMessageBox.information(self, "Favorites", "No favorites yet.")
            return
        dialog = MediaListDialog("Favorites", paths, self)
        dialog.open_requested.connect(lambda path: (self.add_files([path]), self.play_file(path), self.show_player()))
        dialog.exec()

    # ========================================================
    # UPDATED PLAY FILE HOOK
    # ========================================================

    def set_audio_output_device(self, device):
        if device:
            self.audio.setDevice(device)

    # ========================================================
    # SAVE STATE
    # ========================================================

    def save_state(self):
        """Persist the current player state immediately.

QMenuBar { background: #080d16; color: #dfe8f7; spacing: 5px; padding: 3px 6px; }
QMenuBar::item { padding: 7px 12px; border-radius: 8px; }
QMenuBar::item:selected { background: #172742; color: white; }
QSplitter::handle { background: #141e2e; }
QToolTip { background: #0b111c; color: white; border: 1px solid #2f4160; padding: 7px; }
QFrame#Card:hover { border-color: rgba(91,141,255,55); }
QLabel#TimelinePreview { background: #070b13; color: white; border: 1px solid #39537d; border-radius: 10px; padding: 8px 12px; }
"""
        try:
            self.config["volume"] = int(self.volume.value())
        except Exception:
            pass

        try:
            self.config["speed"] = float(
                self.speed.currentText().replace("x", "")
            )
        except Exception:
            pass

        try:
            self.config["equalizer"] = list(self.eq_values)
        except Exception:
            pass

        try:
            write_json(CONFIG_FILE, self.config)
            write_json(HISTORY_FILE, self.history)
            write_json(BOOKMARK_FILE, self.bookmarks)
            write_json(LIBRARY_FILE, self.library)
            self.save_playlist()
            write_json(APP_DATA / "favorites.json", sorted(self.favorites))
            self.status.setText("State saved.")
            self.log_activity("Player state saved.")
        except Exception as exc:
            QMessageBox.warning(self, "Save State", f"Could not save state:\n{exc}")

    # ========================================================
    # CLOSE
    # ========================================================

    def closeEvent(
        self,
        event
    ):

        try:
            if hasattr(self, "_fullscreen_subtitle"):
                self._fullscreen_subtitle.close()
        except Exception:
            pass

        self.config[
            "volume"
        ] = self.volume.value()

        try:

            self.config[
                "speed"
            ] = float(
                self.speed.currentText()
                .replace(
                    "x",
                    ""
                )
            )

        except Exception:
            pass

        write_json(
            CONFIG_FILE,
            self.config
        )

        write_json(
            HISTORY_FILE,
            self.history
        )

        write_json(
            BOOKMARK_FILE,
            self.bookmarks
        )

        self.config["equalizer"] = self.eq_values

        write_json(
            LIBRARY_FILE,
            self.library
        )

        self.save_playlist()

        try:
            self._v30_mark_clean_exit()
        except Exception:
            pass

        event.accept()


# ============================================================
# MAIN
# ============================================================

def main():

    app = QApplication(
        sys.argv
    )

    # Prevent accidental duplicate Nova instances.
    instance_name = "NovaAI_Media_Player_V01_Instance"
    probe = QLocalSocket()
    probe.connectToServer(instance_name)
    if probe.waitForConnected(200):
        probe.disconnectFromServer()
        return
    QLocalServer.removeServer(instance_name)
    single_server = QLocalServer()
    single_server.listen(instance_name)
    app._nova_single_instance_server = single_server

    app.setApplicationName(
        APP_NAME
    )

    app.setApplicationVersion(
        APP_VERSION
    )

    # Apply the Nova icon to the application and taskbar/window.
    if ICON_FILE.exists():
        app.setWindowIcon(QIcon(str(ICON_FILE)))

    app.setStyleSheet(
        STYLE
    )

    window = NovaPlayer()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":

    main()