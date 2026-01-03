# SPRINT 2 — UX polish (enhancements)

Implement these AFTER Sprint 1 is complete.

## A) Drag & drop
- Drag & drop onto window or table:
  - Image file → sets cover image
  - Audio files → added to table
  - Folder → optionally scan recursively for audio files
- Show friendly feedback in Portuguese when files are unsupported.

## B) Improved cover image UX
- Always show a thumbnail preview.
- Changing the cover image does NOT clear the audio list.
- New cover applies to subsequent conversions.

## C) Log panel
- Collapsible “Logs” panel:
  - Show FFmpeg stderr tail (last N lines)
  - Show high-level events (start, finish, error)
  - Button: “Copiar logs”
  - Option: save logs to file in output folder

## D) Row-level actions
- Context menu per row:
  - “Abrir arquivo de saída”
  - “Abrir pasta de saída”
  - “Tentar novamente”
  - “Remover”
- Global progress indicator:
  - Example: “3 de 10 concluídos”
  - Optional global progress bar

## E) Cancel behavior
- Add “Cancelar” button.
- Gracefully stop current FFmpeg process.
- Mark item as “Cancelado”.
- Do not auto-resume unless user restarts.

## F) Small usability details
- Remember last used output folder and cover image
  - Save config locally (JSON)
- Optional toggle:
  - “Abrir pasta ao finalizar”
