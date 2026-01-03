; Inno Setup Script for Audio2Video Converter
; Generates a Windows installer (.exe)
;
; Prerequisites:
;   1. Run PyInstaller first: pyinstaller Audio2Video.spec
;   2. Ensure dist/Audio2Video/ folder exists with all files
;   3. Download Inno Setup from: https://jrsoftware.org/isinfo.php
;
; Usage:
;   Open this file in Inno Setup Compiler and click Build > Compile

#define MyAppName "Conversor de Áudio para Vídeo"
#define MyAppNameShort "Audio2Video"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Audio2Video"
#define MyAppURL "https://github.com/seu-usuario/audio-converter"
#define MyAppExeName "Audio2Video.exe"

[Setup]
; NOTE: AppId uniquely identifies this application
AppId={{A2V-CONVERTER-2024-UNIQUE-ID}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppNameShort}
DefaultGroupName={#MyAppName}
; Allow installation without admin rights (LocalAppData)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist
OutputBaseFilename=Audio2Video_Instalador_v{#MyAppVersion}
SetupIconFile=..\assets\icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; Portuguese (Brazil) language
LanguageDetectionMethod=uilanguage

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Messages]
; Override some messages to Portuguese
brazilianportuguese.BeveledLabel=Conversor de Áudio para Vídeo

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked
Name: "startmenu"; Description: "Criar atalho no Menu Iniciar"; GroupDescription: "Atalhos:"; Flags: checkedonce

[Files]
; Main application files (from PyInstaller output)
Source: "..\dist\Audio2Video\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenu
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"; Tasks: startmenu
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Option to run app after installation
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up config files on uninstall (optional)
Type: filesandordirs; Name: "{localappdata}\Audio2Video"

[Code]
// Show custom welcome message
function InitializeSetup: Boolean;
begin
  Result := True;
end;

procedure InitializeWizard;
begin
  // Optional: Add custom wizard pages or messages here
end;
