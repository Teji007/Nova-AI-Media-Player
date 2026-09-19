; ============================================================
; NOVA AI MEDIA PLAYER
; Inno Setup Installer - Version 01
; Developer: Tejinder Pal Singh
; ============================================================

#define AppName "Nova AI Media Player"
#define AppVersion "1.0.0"
#define AppPublisher "Tejinder Pal Singh"
#define AppExeName "Nova AI Media Player.exe"

; PyInstaller ONE-FOLDER output.
; This .iss file is intended to sit in the project root:
; Media Player\
; ├── Nova_AI_Media_Player_V01_FIXED2.iss
; ├── nova_icon.ico
; └── dist\
;     └── Nova AI Media Player\
;         └── Nova AI Media Player.exe

#define BuildDir "dist\Nova AI Media Player"
#define AppIcon "nova_icon.ico"


; ============================================================
; SETUP
; ============================================================

[Setup]

; Valid fixed GUID for this application.
; Do not change it between releases unless you want Windows
; to treat the installer as a different application.
AppId={{A5F7E8C4-5F12-4F0E-9A2A-6F0F5D3E2B81}}

AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}

DefaultDirName={autopf}\Nova AI Media Player
DefaultGroupName={#AppName}

OutputDir=installer
OutputBaseFilename=Nova_AI_Media_Player_V01_Setup

SetupIconFile={#AppIcon}

UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}

PrivilegesRequired=admin

; Build a 64-bit x64 installer for the 64-bit PyInstaller build.
SetupArchitecture=x64
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

WizardStyle=modern

DisableProgramGroupPage=yes
DisableWelcomePage=no

; ============================================================
; HIGH COMPRESSION
; ============================================================

Compression=lzma2/ultra64
SolidCompression=yes

LZMAMatchFinder=BT
LZMANumFastBytes=273
LZMADictionarySize=65536
CompressionThreads=auto


; ============================================================
; INSTALLER BEHAVIOR
; ============================================================

CloseApplications=yes
RestartApplications=no
AllowNoIcons=yes
ShowLanguageDialog=auto
Uninstallable=yes
CreateUninstallRegKey=yes


; ============================================================
; VERSION INFORMATION
; ============================================================

VersionInfoDescription=Nova AI Media Player Setup
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoCopyright=Copyright (C) 2026 {#AppPublisher}


; ============================================================
; FILES
; ============================================================

[Files]

Source: "{#BuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs


; ============================================================
; TASKS
; ============================================================

[Tasks]

Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked


; ============================================================
; SHORTCUTS
; ============================================================

[Icons]

; Start Menu shortcut
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#AppExeName}"; Comment: "Nova AI Media Player"

; Desktop shortcut - controlled by the task checkbox above
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#AppExeName}"; Comment: "Nova AI Media Player"; Tasks: desktopicon


; ============================================================
; RUN AFTER INSTALL
; ============================================================

[Run]

Filename: "{app}\{#AppExeName}"; Description: "Launch Nova AI Media Player"; Flags: nowait postinstall skipifsilent


; ============================================================
; UNINSTALL CLEANUP
; ============================================================

[UninstallDelete]

Type: filesandordirs; Name: "{app}"


; ============================================================
; CODE
; ============================================================

[Code]

function InitializeSetup(): Boolean;
begin
  Result := True;
end;


function InitializeUninstall(): Boolean;
begin
  Result := True;
end;
