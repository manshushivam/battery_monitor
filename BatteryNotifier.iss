[Setup]
AppName=Battery Notifier
AppVersion=1.0
DefaultDirName={autopf}\BatteryNotifier
DefaultGroupName=BatteryNotifier
OutputBaseFilename=BatteryNotifierInstaller
Compression=lzma
SolidCompression=yes
SetupIconFile=icon.ico  

[Files]
Source: "dist\launcher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\battery_monitor.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "battery_alert.wav"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Run]
; 🔪 Kill any existing old launcher/monitor process
Filename: "taskkill"; Parameters: "/F /IM launcher.exe"; StatusMsg: "Stopping previous launcher..."
Filename: "taskkill"; Parameters: "/F /IM battery_monitor.exe"; StatusMsg: "Stopping previous monitor..."
; 🚀 Start new launcher
Filename: "{app}\launcher.exe"; Description: "Start Battery Notifier"; Flags: nowait postinstall skipifsilent

[Icons]
; Desktop and Start Menu shortcuts
Name: "{autoprograms}\Battery Notifier"; Filename: "{app}\launcher.exe"; IconFilename: "{app}\icon.ico"
; Startup folder shortcut (for auto-start at login)
Name: "{userstartup}\Battery Notifier"; Filename: "{app}\launcher.exe"; IconFilename: "{app}\icon.ico"

[UninstallDelete]
Type: files; Name: "{app}\launcher.exe"
Type: files; Name: "{app}\battery_monitor.exe"
Type: files; Name: "{app}\battery_alert.wav"
Type: files; Name: "{app}\icon.ico"
; 🧹 Clean logs folder
Type: filesandordirs; Name: "{userappdata}\BatteryNotifier"
