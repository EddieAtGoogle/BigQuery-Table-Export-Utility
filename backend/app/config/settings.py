"""
Application Configuration Settings

This module defines the configuration settings for the BigQuery Export service.
It uses Python's dataclasses to create a structured configuration object.

Dataclasses automatically generate special methods like __init__ and __repr__,
making it easier to create classes that primarily store data. They're perfect
for configuration objects because they:
1. Provide a clear structure for settings
2. Support type hints for better IDE support
3. Can validate data on initialization
4. Are more maintainable than plain dictionaries

For more information:
- Dataclasses: https://docs.python.org/3/library/dataclasses.html
- Cloud Run environment variables: https://cloud.google.com/run/docs/configuring/environment-variables
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class AppConfig:
    """
    Application configuration settings.
    
    This class uses the @dataclass decorator to automatically generate:
    - An __init__ method that sets all the fields
    - A __repr__ method for debugging
    - An __eq__ method for comparing configs
    
    Each field is defined with a type annotation and a default value.
    The default values are loaded from environment variables, with fallbacks
    for optional settings.
    """
    
    # Environment configuration
    # These settings determine how the application behaves in different environments
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'production')
    DEBUG: bool = os.getenv('DEBUG', '0') == '1'  # Convert string to boolean
    
    # Google Cloud configuration
    # Required settings for interacting with Google Cloud services
    PROJECT_ID: str = os.getenv('PROJECT_ID')  # Required
    EXPORT_BUCKET: str = os.getenv('EXPORT_BUCKET')  # Required
    
    # Application settings
    # These control the behavior of the export operations
    MAX_CONCURRENT_EXPORTS: int = int(os.getenv('MAX_CONCURRENT_EXPORTS', '5'))
    EXPORT_TIMEOUT_SECONDS: int = int(os.getenv('EXPORT_TIMEOUT_SECONDS', '3600'))
    MAX_FILE_SIZE_GB: float = float(os.getenv('MAX_FILE_SIZE_GB', '10.0'))
    
    # Optional BigQuery settings
    # These can be used to customize BigQuery behavior
    BIGQUERY_LOCATION: Optional[str] = os.getenv('BIGQUERY_LOCATION')
    BIGQUERY_JOB_PROJECT: Optional[str] = os.getenv('BIGQUERY_JOB_PROJECT')
    
    def __post_init__(self):
        """
        Validate configuration after initialization.
        
        This method is automatically called by the dataclass after __init__.
        It's a perfect place to add validation logic that depends on multiple fields.
        
        Raises:
            ValueError: If required environment variables are missing
        """
        required_vars = ['PROJECT_ID', 'EXPORT_BUCKET']
        missing_vars = [var for var in required_vars if not getattr(self, var)]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
            
    @property
    def is_development(self) -> bool:
        """
        Check if running in development environment.
        
        Properties provide a clean interface to derived values and
        ensure consistent behavior across the application.
        
        Returns:
            bool: True if in development mode
        """
        return self.ENVIRONMENT.lower() in ['development', 'dev']
        
    @property
    def is_production(self) -> bool:
        """
        Check if running in production environment.
        
        Using properties allows us to change the implementation details
        without affecting code that uses these checks.
        
        Returns:
            bool: True if in production mode
        """
        return self.ENVIRONMENT.lower() in ['production', 'prod'] 