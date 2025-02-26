"""
Test Configuration and Fixtures

This module contains pytest fixtures and configuration for testing.
Fixtures are reusable test components that provide test data or state.
"""

import pytest
from flask import Flask
from app.main import create_app
from app.config.settings import AppConfig

class TestConfig(AppConfig):
    """Test configuration that overrides production settings."""
    
    # Use test project settings
    PROJECT_ID = "test-project"
    EXPORT_BUCKET = "test-bucket"
    ENVIRONMENT = "test"
    DEBUG = True

@pytest.fixture
def app() -> Flask:
    """
    Create a Flask application for testing.
    
    This fixture provides a test instance of the Flask app
    with test configuration.
    """
    app = create_app(TestConfig())
    return app

@pytest.fixture
def client(app):
    """
    Create a test client for making requests.
    
    This fixture provides a test client that can make
    requests to our API endpoints.
    """
    return app.test_client()

@pytest.fixture
def runner(app):
    """
    Create a test CLI runner.
    
    This fixture provides a runner for testing
    command-line interface commands.
    """
    return app.test_cli_runner() 