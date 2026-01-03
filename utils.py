"""
Utility functions for the audio-to-video converter.
Handles path resolution, output naming, and desktop path detection.
"""

import sys
from pathlib import Path
from typing import Optional


def get_app_dir() -> Path:
    """
    Returns the application directory.
    Handles both normal execution and PyInstaller bundled execution.
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Running as script
        return Path(__file__).parent.resolve()


def get_ffmpeg_path() -> Path:
    """
    Returns the path to ffmpeg executable.
    Uses .exe on Windows, no extension on Mac/Linux.
    Falls back to system ffmpeg if bundled version not found.
    """
    import shutil
    
    if sys.platform == "win32":
        bundled = get_app_dir() / "bin" / "ffmpeg.exe"
    else:
        bundled = get_app_dir() / "bin" / "ffmpeg"
    
    if bundled.exists():
        return bundled
    
    # Fallback to system ffmpeg (useful for development on Mac/Linux)
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return Path(system_ffmpeg)
    
    # Return expected path even if not found (error will be shown later)
    return bundled


def get_ffprobe_path() -> Path:
    """
    Returns the path to ffprobe executable.
    Uses .exe on Windows, no extension on Mac/Linux.
    Falls back to system ffprobe if bundled version not found.
    """
    import shutil
    
    if sys.platform == "win32":
        bundled = get_app_dir() / "bin" / "ffprobe.exe"
    else:
        bundled = get_app_dir() / "bin" / "ffprobe"
    
    if bundled.exists():
        return bundled
    
    # Fallback to system ffprobe (useful for development on Mac/Linux)
    system_ffprobe = shutil.which("ffprobe")
    if system_ffprobe:
        return Path(system_ffprobe)
    
    # Return expected path even if not found (error will be shown later)
    return bundled


def get_desktop_path() -> Path:
    """
    Returns the user's Desktop path.
    Works on Windows, macOS, and Linux.
    """
    if sys.platform == "win32":
        import os
        desktop = Path(os.environ.get("USERPROFILE", "")) / "Desktop"
        if desktop.exists():
            return desktop
        # Fallback to OneDrive Desktop if exists
        onedrive_desktop = Path(os.environ.get("USERPROFILE", "")) / "OneDrive" / "Desktop"
        if onedrive_desktop.exists():
            return onedrive_desktop
        return desktop
    elif sys.platform == "darwin":
        return Path.home() / "Desktop"
    else:
        # Linux and others
        return Path.home() / "Desktop"


def get_default_output_folder() -> Path:
    """Returns the default output folder path."""
    return get_desktop_path() / "Audio2Video_Exports"


def ensure_output_folder(folder: Path) -> Path:
    """
    Ensures the output folder exists, creating it if necessary.
    Returns the folder path.
    """
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_unique_output_path(output_folder: Path, base_name: str, extension: str = ".mpg") -> Path:
    """
    Generates a unique output file path.
    If file exists, appends (1), (2), etc.
    
    Args:
        output_folder: The folder to save the file in
        base_name: The base name of the file (without extension)
        extension: The file extension (default: .mpg)
    
    Returns:
        A unique file path that doesn't exist yet
    """
    # Clean the base name
    base_name = base_name.strip()
    if not extension.startswith("."):
        extension = f".{extension}"
    
    # Try the base name first
    output_path = output_folder / f"{base_name}{extension}"
    if not output_path.exists():
        return output_path
    
    # If exists, try with counter
    counter = 1
    while True:
        output_path = output_folder / f"{base_name} ({counter}){extension}"
        if not output_path.exists():
            return output_path
        counter += 1


def is_supported_audio_file(file_path: Path) -> bool:
    """
    Checks if the file is a supported audio format.
    """
    supported_extensions = {
        '.m4a', '.mp3', '.wav', '.aac', '.flac', '.ogg',
        '.wma', '.opus', '.aiff', '.aif', '.mp2', '.mp4',
        '.webm', '.mkv', '.avi'  # Some video formats that contain audio
    }
    return file_path.suffix.lower() in supported_extensions


def is_supported_image_file(file_path: Path) -> bool:
    """
    Checks if the file is a supported image format.
    """
    supported_extensions = {
        '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff', '.tif'
    }
    return file_path.suffix.lower() in supported_extensions


def format_duration(seconds: float) -> str:
    """
    Formats duration in seconds to HH:MM:SS format.
    """
    if seconds < 0:
        return "00:00:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def safe_path_string(path: Path) -> str:
    """
    Returns a safely encoded path string for subprocess calls.
    """
    return str(path.resolve())
