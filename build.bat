@echo off
REM ============================================
REM Build script for Audio2Video Converter
REM Run this on Windows to create the executable
REM ============================================

echo.
echo ========================================
echo  Audio2Video - Build Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado. Instale o Python 3.9+ primeiro.
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller...
    pip install pyinstaller
)

REM Check if FFmpeg binaries exist
if not exist "bin\ffmpeg.exe" (
    echo.
    echo AVISO: ffmpeg.exe nao encontrado em bin\
    echo Baixe o FFmpeg de: https://www.gyan.dev/ffmpeg/builds/
    echo Copie ffmpeg.exe e ffprobe.exe para a pasta bin\
    echo.
    pause
    exit /b 1
)

if not exist "bin\ffprobe.exe" (
    echo.
    echo AVISO: ffprobe.exe nao encontrado em bin\
    echo.
    pause
    exit /b 1
)

echo.
echo [1/2] Gerando executavel com PyInstaller...
echo.

pyinstaller Audio2Video.spec --noconfirm

if errorlevel 1 (
    echo.
    echo ERRO: Falha ao gerar o executavel.
    pause
    exit /b 1
)

echo.
echo [2/2] Build concluido!
echo.
echo O executavel foi gerado em: dist\Audio2Video\
echo.
echo Para criar o instalador:
echo   1. Instale o Inno Setup: https://jrsoftware.org/isinfo.php
echo   2. Abra installer\Audio2Video.iss no Inno Setup
echo   3. Clique em Build ^> Compile
echo.

pause
