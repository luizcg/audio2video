# SPRINT 4 — Website & CI/CD

## Context
- The desktop application is fully implemented (Sprints 1-3)
- The app converts audio files into MPEG videos using FFmpeg
- The app UI is in Brazilian Portuguese (PT-BR) and targets non-technical users
- Packaging scripts are ready (PyInstaller, Inno Setup)

## Goals
1. Create a GitHub Pages website for the project
2. Set up GitHub Actions for automated Windows builds
3. Automate release workflow

---

## PART A: GitHub Pages Website

### Website goals
- Simple, modern, and fast static site hosted on GitHub Pages
- Clear call-to-actions:
  - "Baixar para Windows" (link to GitHub Releases)
  - "Ver código no GitHub"
- Explain what the tool does, how to use it, and how to contribute
- Include licensing notes about FFmpeg
- Provide a clean documentation section

### Technical constraints
- Must work on GitHub Pages without a backend
- Use a static site approach:
  - Option A: plain HTML/CSS/JS (preferred for simplicity)
  - Option B: Jekyll (only if needed)
- All site content must be written in Portuguese (PT-BR)
- No external build step required (avoid heavy frameworks)

### Information architecture (pages/sections)

#### 1) Home (index)
- Hero: app name + tagline
- Primary buttons:
  - "Baixar para Windows" → GitHub Releases latest
  - "Ver no GitHub" → repo
- "Como funciona" section with 3 steps:
  1. Escolha a imagem de capa
  2. Adicione seus áudios
  3. Clique em Iniciar e acompanhe o progresso
- Features list:
  - Conversão em lote
  - Barra de progresso por arquivo
  - Arrastar e soltar
  - Painel de logs
  - Pasta de saída no Desktop por padrão (Audio2Video_Exports)
- Screenshots section (use placeholders)
- FAQ preview (link to full FAQ page)

#### 2) Download page (or section)
- Explain: portable vs installer (if both exist)
- Link to releases
- Notes about Windows SmartScreen (friendly explanation)

#### 3) Documentation page
- "Como usar"
- "Configurações"
- "Solução de problemas" (common errors, FFmpeg not found, permissions, etc.)

#### 4) FAQ page
- What formats are supported?
- Where does the output go?
- Why SmartScreen appears?
- Does it upload anything? (Answer: no, works offline)
- Licensing / FFmpeg explanation

#### 5) Contributing page
- How to run locally (venv, install deps)
- How to build with PyInstaller
- How to open PRs
- Code style guidance

#### 6) Licenses page
- Project license (MIT)
- Third-party licenses:
  - FFmpeg (LGPL) explanation
  - Note that binaries are distributed in releases with proper license files

### Design guidelines
- Minimal, modern layout
- Responsive (mobile-friendly)
- Use a neutral background, one primary accent color, consistent spacing
- Include a small "app icon" placeholder
- Top nav: Início, Baixar, Documentação, FAQ, Contribuir, Licenças
- Footer with:
  - GitHub repo link
  - License
  - "Feito no Brasil" (optional)

### Repository structure to generate
```
/docs                          ← GitHub Pages root
├── index.html
├── download.html
├── docs.html
├── faq.html
├── contributing.html
├── licenses.html
├── README.md                  ← How to publish via GitHub Pages
└── assets/
    ├── css/
    │   └── styles.css
    ├── js/
    │   └── main.js (optional)
    └── img/
        ├── app-main.png       ← Placeholder
        ├── app-queue.png      ← Placeholder
        └── app-logs.png       ← Placeholder
```

### Content requirements (PT-BR)
- Use friendly language for non-technical users
- Use short paragraphs and clear headings
- Include "Passo a passo" sections
- Add a "Privacidade" note: the app does not upload files or send telemetry

---

## PART B: GitHub Actions CI/CD

### Goals
- Automate Windows executable build on every release tag
- Automate FFmpeg download during build
- Upload artifacts to GitHub Releases
- No manual Windows machine required

### Workflow: Build & Release

Create `.github/workflows/build.yml`:

```yaml
name: Build Windows Executable

on:
  push:
    tags:
      - 'v*'  # Triggers on version tags like v1.0.0
  workflow_dispatch:  # Allow manual trigger

jobs:
  build-windows:
    runs-on: windows-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pyinstaller
      
      - name: Download FFmpeg
        run: |
          # Download FFmpeg essentials build
          $ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
          $zipPath = "ffmpeg.zip"
          Invoke-WebRequest -Uri $ffmpegUrl -OutFile $zipPath
          Expand-Archive -Path $zipPath -DestinationPath "ffmpeg_temp"
          
          # Find and copy binaries
          $ffmpegDir = Get-ChildItem -Path "ffmpeg_temp" -Directory | Select-Object -First 1
          Copy-Item "$($ffmpegDir.FullName)\bin\ffmpeg.exe" -Destination "bin\"
          Copy-Item "$($ffmpegDir.FullName)\bin\ffprobe.exe" -Destination "bin\"
          
          # Cleanup
          Remove-Item -Recurse -Force "ffmpeg_temp"
          Remove-Item $zipPath
        shell: pwsh
      
      - name: Build with PyInstaller
        run: pyinstaller Audio2Video.spec --noconfirm
      
      - name: Create portable ZIP
        run: |
          Compress-Archive -Path "dist\Audio2Video\*" -DestinationPath "dist\Audio2Video_Portable_${{ github.ref_name }}.zip"
        shell: pwsh
      
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: Audio2Video-Windows
          path: dist/Audio2Video_Portable_*.zip
      
      - name: Create Release
        if: startsWith(github.ref, 'refs/tags/')
        uses: softprops/action-gh-release@v1
        with:
          files: dist/Audio2Video_Portable_*.zip
          draft: false
          prerelease: false
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### How to use

1. **Push code to GitHub**
2. **Create a tag for release:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. **GitHub Actions will automatically:**
   - Build on Windows
   - Download FFmpeg
   - Create executable with PyInstaller
   - Create a ZIP file
   - Upload to GitHub Releases

### Manual trigger
- Go to Actions tab in GitHub
- Select "Build Windows Executable"
- Click "Run workflow"

---

## PART C: README Updates

Update main README.md with:
- Project description
- Website link (GitHub Pages)
- Download link to releases
- How to contribute
- License + FFmpeg notes

---

## Deliverables Checklist

### Website
- [ ] /docs/index.html - Home page
- [ ] /docs/download.html - Download page
- [ ] /docs/docs.html - Documentation
- [ ] /docs/faq.html - FAQ
- [ ] /docs/contributing.html - Contributing guide
- [ ] /docs/licenses.html - Licenses
- [ ] /docs/assets/css/styles.css - Styles
- [ ] /docs/assets/img/ - Screenshot placeholders
- [ ] /docs/README.md - GitHub Pages setup instructions

### CI/CD
- [ ] .github/workflows/build.yml - Build workflow

### Updates
- [ ] README.md - Add website and release links

---

## Now implement Sprint 4.
Focus on a clean, modern website and reliable CI/CD pipeline.
