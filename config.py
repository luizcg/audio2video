"""
Configuration management for the audio-to-video converter.
Handles saving and loading user preferences (JSON).
"""

import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict

from utils import get_app_dir, get_default_output_folder


def get_config_path() -> Path:
    """Returns the path to the config file."""
    import sys
    if sys.platform == "win32":
        # Windows: use AppData/Local
        import os
        app_data = Path(os.environ.get("LOCALAPPDATA", ""))
        if app_data.exists():
            config_dir = app_data / "Audio2Video"
        else:
            config_dir = get_app_dir()
    elif sys.platform == "darwin":
        # macOS: use ~/Library/Application Support
        config_dir = Path.home() / "Library" / "Application Support" / "Audio2Video"
    else:
        # Linux: use ~/.config
        config_dir = Path.home() / ".config" / "audio2video"
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"


@dataclass
class AppConfig:
    """Application configuration."""
    last_output_folder: Optional[str] = None
    last_cover_image: Optional[str] = None
    open_folder_on_finish: bool = False
    window_width: int = 900
    window_height: int = 700
    logs_panel_visible: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        """Create from dictionary."""
        return cls(
            last_output_folder=data.get("last_output_folder"),
            last_cover_image=data.get("last_cover_image"),
            open_folder_on_finish=data.get("open_folder_on_finish", False),
            window_width=data.get("window_width", 900),
            window_height=data.get("window_height", 700),
            logs_panel_visible=data.get("logs_panel_visible", False),
        )


def load_config() -> AppConfig:
    """Load configuration from file."""
    config_path = get_config_path()
    
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return AppConfig.from_dict(data)
        except (json.JSONDecodeError, IOError):
            pass
    
    return AppConfig()


def save_config(config: AppConfig) -> bool:
    """Save configuration to file. Returns True on success."""
    config_path = get_config_path()
    
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False
