# Conversor de Áudio para Vídeo

[![Download](https://img.shields.io/github/v/release/SEU-USUARIO/audio-converter?label=Download&style=for-the-badge)](https://github.com/SEU-USUARIO/audio-converter/releases/latest)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

Aplicativo desktop que converte arquivos de áudio em vídeos MPEG, utilizando uma imagem de capa como fundo.

🌐 **Website:** [https://SEU-USUARIO.github.io/audio-converter/](https://SEU-USUARIO.github.io/audio-converter/)

⬇️ **Download:** [Última versão para Windows](https://github.com/SEU-USUARIO/audio-converter/releases/latest)

## Funcionalidades

- Converte múltiplos arquivos de áudio para vídeo (.mpg)
- Suporta diversos formatos: M4A, MP3, WAV, AAC, FLAC, OGG, WMA, OPUS
- Usa uma imagem de capa como fundo do vídeo
- Barra de progresso em tempo real para cada arquivo
- Interface gráfica amigável em Português (PT-BR)

## Requisitos

- Python 3.9 ou superior
- PySide6
- FFmpeg e FFprobe

## Instalação

### 1. Clone o repositório ou baixe os arquivos

```bash
git clone <url-do-repositorio>
cd audio-converter
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Baixe o FFmpeg

O aplicativo requer o FFmpeg para funcionar. Você precisa baixar os executáveis manualmente:

1. Acesse: https://www.gyan.dev/ffmpeg/builds/ (Windows) ou https://ffmpeg.org/download.html
2. Baixe a versão "essentials" ou "full" para Windows (64-bit)
3. Extraia os arquivos
4. Copie `ffmpeg.exe` e `ffprobe.exe` para a pasta `bin/` do projeto:

```
audio-converter/
├── bin/
│   ├── ffmpeg.exe    ← Coloque aqui
│   └── ffprobe.exe   ← Coloque aqui
├── app.py
├── converter.py
├── utils.py
└── ...
```

## Como executar

```bash
python app.py
```

## Como usar

1. **Selecione uma imagem de capa** - Clique em "Selecionar imagem de capa..." e escolha uma imagem (JPG, PNG, etc.)

2. **Adicione arquivos de áudio** - Clique em "Adicionar áudios..." e selecione um ou mais arquivos de áudio

3. **Configure a pasta de saída** (opcional) - Por padrão, os vídeos serão salvos em `Desktop\Audio2Video_Exports`

4. **Inicie a conversão** - Clique no botão "Iniciar" para começar a conversão

5. **Acompanhe o progresso** - A tabela mostra o status e progresso de cada arquivo

## Especificações do vídeo gerado

- **Formato**: MPEG (.mpg)
- **Codec de vídeo**: MPEG-2
- **Codec de áudio**: MP2
- **Resolução**: 1280x720 (HD)
- **Taxa de quadros**: 30 FPS

## Funcionalidades Extras (Sprint 2)

- **Drag & Drop**: Arraste imagens para definir capa, ou áudios/pastas para adicionar à lista
- **Painel de Logs**: Visualize o progresso detalhado da conversão
- **Menu de Contexto**: Clique direito em um item para opções adicionais
- **Botão Cancelar**: Interrompa a conversão a qualquer momento
- **Persistência**: O aplicativo lembra suas configurações

## Estrutura do projeto

```
audio-converter/
├── app.py              # Interface gráfica principal
├── converter.py        # Lógica de conversão com FFmpeg
├── config.py           # Gerenciamento de configurações
├── utils.py            # Funções utilitárias
├── requirements.txt    # Dependências Python
├── Audio2Video.spec    # Configuração do PyInstaller
├── build.bat           # Script de build (Windows)
├── bin/                # FFmpeg binaries (não incluídos)
├── assets/             # Ícones e recursos
├── installer/          # Script do Inno Setup
├── LICENSES/           # Licenças de terceiros
└── docs/               # Documentação
```

## Gerar executável (Windows)

### Método 1: Script automático

```batch
build.bat
```

### Método 2: Manual

```bash
pip install pyinstaller
pyinstaller Audio2Video.spec --noconfirm
```

O executável será gerado em `dist/Audio2Video/`.

### Pré-requisitos para o build

1. **FFmpeg**: Baixe de https://www.gyan.dev/ffmpeg/builds/
2. Copie `ffmpeg.exe` e `ffprobe.exe` para a pasta `bin/`
3. (Opcional) Adicione um ícone `assets/icon.ico`

## Criar instalador Windows

Após gerar o executável:

1. Instale o [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Abra `installer/Audio2Video.iss` no Inno Setup
3. Clique em **Build > Compile**
4. O instalador será gerado em `dist/Audio2Video_Instalador_v1.0.0.exe`

## Versão Portátil vs Instalador

| Versão | Descrição |
|--------|-----------|
| **Portátil** (`dist/Audio2Video/`) | Pasta completa, pode ser copiada para qualquer lugar |
| **Instalador** (`.exe`) | Instala no Windows, cria atalhos, permite desinstalação |

## One-Folder vs One-File

O projeto usa **one-folder** (recomendado):
- ✅ Inicia mais rápido
- ✅ Atualizações mais fáceis
- ✅ Menos problemas com antivírus
- ❌ Múltiplos arquivos (mas pode zipar)

## Aviso sobre o Windows SmartScreen

Ao executar o aplicativo pela primeira vez, o Windows pode exibir um aviso do SmartScreen dizendo que o aplicativo é desconhecido. Isso acontece porque:

- O executável não possui assinatura digital (code signing)
- Aplicativos novos e não reconhecidos pela Microsoft recebem este aviso

**Para continuar:**
1. Clique em "Mais informações"
2. Clique em "Executar assim mesmo"

Este aviso é normal para aplicativos desenvolvidos independentemente e não indica que o software seja malicioso.

## Solução de problemas

### "FFmpeg não encontrado"
- Verifique se `ffmpeg.exe` e `ffprobe.exe` estão na pasta `bin/`
- Certifique-se de que os arquivos não estão corrompidos

### A conversão falha com erro
- Verifique se o arquivo de áudio não está corrompido
- Verifique se a imagem de capa é um formato suportado (JPG, PNG, etc.)
- Verifique se há espaço suficiente no disco

### A interface congela
- Isso não deveria acontecer, pois as conversões rodam em thread separada
- Se ocorrer, reinicie o aplicativo e reporte o problema

## Licenças de Terceiros

Este aplicativo inclui os seguintes componentes:

| Componente | Licença | Website |
|------------|---------|---------|
| **FFmpeg** | LGPL 2.1+ | https://ffmpeg.org/ |
| **PySide6** | LGPL 3.0 | https://www.qt.io/qt-for-python |
| **Python** | PSF License | https://www.python.org/ |

Os binários do FFmpeg (`ffmpeg.exe`, `ffprobe.exe`) são incluídos sem modificações.
Veja a pasta `LICENSES/` para os textos completos das licenças.

## Licença

Este projeto é distribuído sob a licença MIT.

## Créditos

- [FFmpeg](https://ffmpeg.org/) - Ferramenta de conversão de mídia
- [PySide6](https://www.qt.io/qt-for-python) - Framework de interface gráfica
