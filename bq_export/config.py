"""
Configuration Management

This module handles configuration settings for the CLI application.
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Configuration settings for the CLI application."""
    api_url: str
    project_id: Optional[str] = None

def get_config() -> Config:
    """
    Get configuration settings from environment variables.
    
    Returns:
        Config: Configuration object
        
    Raises:
        ValueError: If required configuration is missing
    """
    api_url = os.getenv('BQ_EXPORT_API_URL')
    if not api_url:
        raise ValueError(
            "BQ_EXPORT_API_URL environment variable is required. "
            "Please set it to your Cloud Run service URL."
        )
    
    return Config(
        api_url=api_url,
        project_id=os.getenv('GOOGLE_CLOUD_PROJECT')
    ) 