# SPRINT 1 — Core working app (must work)

## Goal
- Input: 1 required cover image + 1 or more audio files (.m4a, .mp3, and any other formats FFmpeg supports).
- Output: For each audio file, generate an MPEG video file (.mpg) that uses the cover image as the video track and the audio as the audio track.
- Use FFmpeg (bundled locally in the project under ./bin/ffmpeg.exe). Do NOT assume FFmpeg is installed globally.

## Default output folder
- Create by default: Desktop\Audio2Video_Exports
- Folder name suggestion (use exactly this): "Audio2Video_Exports"

## Requirements

### 1) FFmpeg command (per audio file)
- Use ffmpeg.exe.
- Create a video using the cover image looped for the duration of the audio.
- Encoding:
  - Container: MPEG (.mpg)
  - Video codec: mpeg2video
  - Audio codec: mp2
- Ensure the output ends exactly when the audio ends.
- Handle paths with spaces and accents safely (subprocess args list + pathlib).

Suggested encoding defaults
- Resolution: 1280x720
- FPS: 30
- Pixel format: yuv420p
- Reasonable target bitrate for compatibility.

### 2) UI (Python)
- Use PySide6 (preferred). If unavailable, use PyQt6. If neither, fall back to Tkinter.
- All UI text must be in Portuguese (PT-BR).

UI elements:

a) Cover image selector
- Required field
- Show selected filename
- Optional thumbnail preview
- Labels/examples in Portuguese (e.g., “Imagem de capa (obrigatória)”)

b) “Adicionar áudios…” button
- Multiple file selection
- Filters: m4a, mp3, wav, aac, flac, ogg, and “Todos os arquivos”

c) Table (one row per audio file)
Columns (Portuguese names):
- Arquivo
- Status
- Progresso
- Arquivo de saída

Status values (exact wording):
- "Na fila"
- "Convertendo"
- "Concluído"
- "Erro"
- "Cancelado" (used later in Sprint 2)

d) Output folder selector
- Label in Portuguese
- Default: Desktop\Audio2Video_Exports
- Create folder automatically if missing

e) Controls
- "Iniciar"
- "Remover selecionados"
- "Limpar lista"
- Optional: "Abrir pasta de saída"
- Disable "Iniciar" until:
  - Cover image selected
  - At least one audio file added

### 3) Async conversions (no UI freeze)
- Conversions must run asynchronously.
- Use QThread / QRunnable + signals if using Qt.
- Convert files sequentially by default.
- UI must remain responsive at all times.

### 4) Progress tracking (important)
- Implement real progress per file.
- Use FFmpeg flags:
  - `-progress pipe:1`
  - `-nostats`
- Parse key=value output from stdout.
- Calculate progress using:
  - out_time_ms / total_duration_ms
- Duration detection:
  - Prefer ffprobe.exe bundled at ./bin/ffprobe.exe
  - If ffprobe is missing, attempt fallback via FFmpeg metadata
  - If duration is unknown, show indeterminate progress bar

### 5) File naming rules
- Output filename = audio base name + ".mpg"
- If file exists, append:
  - " (1)", " (2)", etc.
- Keep the same order as added in the table.

### 6) Packaging readiness
- Structure project so it can be packaged later with PyInstaller.
- All paths resolved relative to app directory.
- Do NOT hardcode absolute paths.

### 7) Deliverables (Sprint 1)
- app.py (or main.py) — GUI
- converter.py — FFmpeg execution + progress parsing
- utils.py — helpers (desktop path, output naming, path safety)
- converter_cli.py (optional) — CLI reuse of conversion logic
- README.md (written in Portuguese)
- bin/ folder placeholder (no binaries included)

README.md (Portuguese)
- Como executar o projeto
- Onde colocar ffmpeg.exe e ffprobe.exe
- Como gerar o executável com PyInstaller
- Observação sobre aviso do Windows SmartScreen

Implementation details
- Use pathlib everywhere.
- Use subprocess without shell=True.
- Capture stdout (progress) and stderr (logs/errors).
- On failure:
  - Set status to “Erro”
  - Store error message
  - Show a friendly message dialog in Portuguese.
