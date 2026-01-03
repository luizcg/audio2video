# SPRINT 3 — Packaging & Distribution

## Context
- A desktop application already exists and is fully implemented (Sprint 1 and Sprint 2).
- The app converts audio files into MPEG videos using FFmpeg.
- The app is written in Python and uses PySide6 (or PyQt6 / Tkinter fallback).
- The app already works correctly when run via Python.
- All user-facing text is in Brazilian Portuguese (PT-BR).

## ⚠️ VERY IMPORTANT
- The final distributed application MUST include FFmpeg binaries.
- All user-facing text (installer, README, messages) MUST be in Portuguese (PT-BR).
- Code comments and build scripts may be in English.

## Goals
- Generate a Windows-friendly distribution that:
  - Requires ZERO setup from the end user
  - Does NOT require Python installed
  - Includes FFmpeg and FFprobe binaries
  - Works offline
- Output:
  - A single-folder portable version
  - AND (optionally) a Windows installer (.exe)

## 1) FFmpeg inclusion
- Assume FFmpeg and FFprobe binaries are already available locally:
  - ./bin/ffmpeg.exe
  - ./bin/ffprobe.exe
- Use a standard Windows 64-bit LGPL-compatible FFmpeg build.
- Do NOT download FFmpeg automatically in the build script.

Runtime expectations
- The packaged app must access FFmpeg via a relative path.
- Paths must work when bundled inside a PyInstaller executable.

## 2) PyInstaller configuration
- Use PyInstaller to generate a Windows executable.
- Requirements:
  - One-folder build (preferred): dist/MeuConversor/
  - Optional: one-file build (secondary, explain pros/cons)
- Ensure the following are bundled:
  - Python runtime
  - All Python dependencies
  - UI framework (PySide6 / PyQt6 / Tkinter)
  - FFmpeg binaries (ffmpeg.exe, ffprobe.exe)
  - Any icons or assets
  - License files

- Handle correctly:
  - sys._MEIPASS for runtime path resolution
  - Relative access to ./bin/ffmpeg.exe
  - Windows path encoding (UTF-8)

- Provide:
  - PyInstaller command
  - Optional .spec file (preferred for clarity)

## 3) Executable metadata
- Set:
  - Application name (suggest a friendly name)
  - Window title in Portuguese
  - Application icon (.ico)
- Prevent console window from opening (GUI mode).
- Ensure correct DPI awareness if possible.

## 4) FFmpeg licensing
- Include a LICENSES folder in the final distribution containing:
  - FFmpeg license text (LGPL)
  - A short README explaining:
    - That FFmpeg is included
    - Where it comes from
    - That it is licensed under LGPL

- The main README (Portuguese) must include:
  - A short section: “Licenças de terceiros”

## 5) Windows installer (optional but recommended)

Implement an optional installer using one of:
- Inno Setup (preferred)
- NSIS (acceptable alternative)

Installer requirements
- Wizard fully in Portuguese (PT-BR)
- Steps:
  - Welcome screen
  - License screen
  - Install directory selection
  - Optional “Criar atalho na área de trabalho”
  - Finish screen with “Abrir aplicativo”
- Install location:
  - Program Files or Local AppData (no admin required if possible)

Installer behavior
- Bundle everything produced by PyInstaller
- Create:
  - Desktop shortcut
  - Start Menu entry
- Correct app icon everywhere

## 6) SmartScreen and trust notes
- Explain in README:
  - Windows SmartScreen warning
  - Why it may appear
  - How the user can safely proceed
- Mention (optional):
  - Code signing as a future improvement
  - That unsigned apps are common for personal tools

## 7) Final deliverables
Produce:
- Updated project structure
- PyInstaller command and/or .spec file
- Inno Setup (.iss) script (if installer implemented)
- Updated README.md (Portuguese)
- Notes explaining:
  - Portable vs Installer versions
  - One-folder vs One-file tradeoffs

## 8) Validation checklist
Ensure that:
- App runs on a clean Windows machine
- No Python installation is required
- FFmpeg is correctly found and executed
- Drag & drop still works
- Progress bars work
- Paths with accents work
- Output folder default (Desktop\Audio2Video_Exports) still works

## Now implement Sprint 3.
Focus on reliability, clarity, and user-friendliness.
Assume the end user is NOT technical.
