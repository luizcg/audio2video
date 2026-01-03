"""
FFmpeg conversion logic with progress parsing.
Handles audio-to-video conversion using a cover image.
"""

import subprocess
import re
from pathlib import Path
from typing import Optional, Callable, Tuple
from dataclasses import dataclass

from utils import get_ffmpeg_path, get_ffprobe_path, safe_path_string


@dataclass
class ConversionResult:
    """Result of a conversion operation."""
    success: bool
    output_path: Optional[Path] = None
    error_message: Optional[str] = None


def get_audio_duration(audio_path: Path) -> Optional[float]:
    """
    Gets the duration of an audio file in seconds using ffprobe.
    Returns None if duration cannot be determined.
    """
    ffprobe_path = get_ffprobe_path()
    
    if not ffprobe_path.exists():
        # Try fallback using ffmpeg
        return get_audio_duration_ffmpeg(audio_path)
    
    try:
        cmd = [
            safe_path_string(ffprobe_path),
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            safe_path_string(audio_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError):
        pass
    
    return get_audio_duration_ffmpeg(audio_path)


def get_audio_duration_ffmpeg(audio_path: Path) -> Optional[float]:
    """
    Fallback method to get audio duration using ffmpeg.
    """
    ffmpeg_path = get_ffmpeg_path()
    
    if not ffmpeg_path.exists():
        return None
    
    try:
        cmd = [
            safe_path_string(ffmpeg_path),
            "-i", safe_path_string(audio_path),
            "-f", "null", "-"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        # Parse duration from stderr
        duration_pattern = r"Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})"
        match = re.search(duration_pattern, result.stderr)
        
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            seconds = int(match.group(3))
            centiseconds = int(match.group(4))
            
            return hours * 3600 + minutes * 60 + seconds + centiseconds / 100
    except subprocess.SubprocessError:
        pass
    
    return None


def convert_audio_to_video(
    audio_path: Path,
    cover_image_path: Path,
    output_path: Path,
    progress_callback: Optional[Callable[[float], None]] = None,
    cancel_check: Optional[Callable[[], bool]] = None,
    resolution: Tuple[int, int] = (1280, 720),
    fps: int = 30,
    video_bitrate: str = "4000k",
    audio_bitrate: str = "192k"
) -> ConversionResult:
    """
    Converts an audio file to an MPEG video using a cover image.
    
    Args:
        audio_path: Path to the audio file
        cover_image_path: Path to the cover image
        output_path: Path for the output .mpg file
        progress_callback: Optional callback for progress updates (0.0 to 1.0)
        cancel_check: Optional callback that returns True if conversion should be cancelled
        resolution: Output video resolution (width, height)
        fps: Frames per second
        video_bitrate: Video bitrate (e.g., "4000k")
        audio_bitrate: Audio bitrate (e.g., "192k")
    
    Returns:
        ConversionResult with success status and output path or error message
    """
    ffmpeg_path = get_ffmpeg_path()
    
    if not ffmpeg_path.exists():
        return ConversionResult(
            success=False,
            error_message=f"FFmpeg não encontrado em: {ffmpeg_path}"
        )
    
    if not audio_path.exists():
        return ConversionResult(
            success=False,
            error_message=f"Arquivo de áudio não encontrado: {audio_path}"
        )
    
    if not cover_image_path.exists():
        return ConversionResult(
            success=False,
            error_message=f"Imagem de capa não encontrada: {cover_image_path}"
        )
    
    # Get audio duration for progress calculation
    duration = get_audio_duration(audio_path)
    duration_ms = duration * 1000 if duration else None
    
    # Build FFmpeg command
    width, height = resolution
    cmd = [
        safe_path_string(ffmpeg_path),
        "-y",  # Overwrite output file
        "-loop", "1",  # Loop the image
        "-i", safe_path_string(cover_image_path),
        "-i", safe_path_string(audio_path),
        "-c:v", "mpeg2video",
        "-c:a", "mp2",
        "-b:v", video_bitrate,
        "-b:a", audio_bitrate,
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
        "-r", str(fps),
        "-shortest",  # End when audio ends
        "-progress", "pipe:1",
        "-nostats",
        safe_path_string(output_path)
    ]
    
    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Start FFmpeg process
        creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=creationflags
        )
        
        # Parse progress from stdout
        current_time_ms = 0
        
        while True:
            # Check for cancellation
            if cancel_check and cancel_check():
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                # Clean up partial file
                if output_path.exists():
                    try:
                        output_path.unlink()
                    except OSError:
                        pass
                
                return ConversionResult(
                    success=False,
                    error_message="Conversão cancelada pelo usuário"
                )
            
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            
            line = line.strip()
            if "=" in line:
                key, value = line.split("=", 1)
                
                if key == "out_time_us" and duration_ms:
                    # out_time_us is in microseconds
                    try:
                        current_time_us = int(value)
                        current_time_ms = current_time_us / 1000
                        progress = min(current_time_ms / duration_ms, 1.0)
                        if progress_callback:
                            progress_callback(progress)
                    except ValueError:
                        pass
                elif key == "out_time" and duration_ms:
                    # out_time is in HH:MM:SS.microseconds format
                    try:
                        time_parts = value.split(":")
                        if len(time_parts) == 3:
                            hours = int(time_parts[0])
                            minutes = int(time_parts[1])
                            seconds = float(time_parts[2])
                            current_time_ms = (hours * 3600 + minutes * 60 + seconds) * 1000
                            progress = min(current_time_ms / duration_ms, 1.0)
                            if progress_callback:
                                progress_callback(progress)
                    except (ValueError, IndexError):
                        pass
                elif key == "progress" and value == "end":
                    if progress_callback:
                        progress_callback(1.0)
        
        # Get the return code
        return_code = process.wait()
        
        # Read any remaining stderr
        stderr_output = process.stderr.read()
        
        if return_code != 0:
            return ConversionResult(
                success=False,
                error_message=f"FFmpeg retornou código de erro {return_code}:\n{stderr_output[-500:]}"
            )
        
        if not output_path.exists():
            return ConversionResult(
                success=False,
                error_message="O arquivo de saída não foi criado"
            )
        
        return ConversionResult(
            success=True,
            output_path=output_path
        )
        
    except subprocess.SubprocessError as e:
        return ConversionResult(
            success=False,
            error_message=f"Erro ao executar FFmpeg: {str(e)}"
        )
    except Exception as e:
        return ConversionResult(
            success=False,
            error_message=f"Erro inesperado: {str(e)}"
        )
