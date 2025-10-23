[Setup]
; Basis-Informationen
AppName=DiaDrop
AppVersion=3.1
AppPublisher=LazyLoopStudio
AppPublisherURL=https://lazyloopstudio.static.domains/homepage.html
DefaultDirName={autopf}\DiaDrop
DefaultGroupName=DiaDrop
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=DiaDrop_Setup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\DiaDrop.exe

; Moderne Installer-Optionen (auskommentiert, falls Bilder fehlen)
; WizardImageFile=compiler:WizModernImage-IS.bmp
; WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "Quick Launch Verknüpfung erstellen"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Hauptprogramm - sprachabhängig (aus verschiedenen Ordnern)
Source: "dist\DE\DiaDrop.exe"; DestDir: "{app}"; Flags: ignoreversion; Languages: german
Source: "dist\EN\DiaDrop.exe"; DestDir: "{app}"; Flags: ignoreversion; Languages: english

; Icon-Datei (WICHTIG: wird in den gleichen Ordner wie die EXE kopiert)
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

; Weitere Dateien falls vorhanden (optional)
; Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
; Startmenü-Verknüpfung
Name: "{group}\DiaDrop"; Filename: "{app}\DiaDrop.exe"; IconFilename: "{app}\icon.ico"
Name: "{group}\{cm:UninstallProgram,DiaDrop}"; Filename: "{uninstallexe}"

; Desktop-Verknüpfung (optional)
Name: "{autodesktop}\DiaDrop"; Filename: "{app}\DiaDrop.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

; Quick Launch (optional)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\DiaDrop"; Filename: "{app}\DiaDrop.exe"; IconFilename: "{app}\icon.ico"; Tasks: quicklaunchicon

[Run]
; Programm nach Installation starten (optional)
Filename: "{app}\DiaDrop.exe"; Description: "{cm:LaunchProgram,DiaDrop}"; Flags: nowait postinstall skipifsilent

[Code]
// Begrüßungsnachricht
function InitializeSetup(): Boolean;
var
  Message: String;
begin
  Result := True;
  
  // Sprachabhängige Nachricht
  if ActiveLanguage = 'german' then
    Message := 'Willkommen zum DiaDrop Installer!' + #13#10#13#10 + 
               'Dieser Assistent wird DiaDrop - Diagramm Ersteller auf Ihrem Computer installieren.' + #13#10#13#10 + 
               'Möchten Sie fortfahren?'
  else
    Message := 'Welcome to the DiaDrop Installer!' + #13#10#13#10 + 
               'This wizard will install DiaDrop - Diagram Creator on your computer.' + #13#10#13#10 + 
               'Do you want to continue?';
  
  if MsgBox(Message, mbConfirmation, MB_YESNO) = IDNO then
  begin
    Result := False;
  end;
end;

// Erfolgreiche Installation
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Hier können zusätzliche Aktionen nach der Installation durchgeführt werden
  end;
end;