"""
Authentication Utilities

This module handles Google Cloud authentication for the CLI application.
"""

import subprocess
import click
from typing import List
from google.auth.exceptions import DefaultCredentialsError
from google.auth import default
from google.auth.transport import requests
from rich.console import Console

# Define required scopes
SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/bigquery.readonly'
]

console = Console()

def check_auth() -> bool:
    """
    Check if the user is authenticated with Google Cloud.
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    try:
        # Attempt to get default credentials with required scopes
        credentials, project = default(scopes=SCOPES)
        
        # Refresh token if needed
        auth_req = requests.Request()
        credentials.refresh(auth_req)
        
        return True
    except DefaultCredentialsError:
        return False
    except Exception as e:
        console.print(f"[yellow]Warning: Error checking authentication: {str(e)}[/yellow]")
        return False

def ensure_auth() -> bool:
    """
    Ensure the user is authenticated by prompting for login if needed.
    
    Returns:
        bool: True if authentication successful, False otherwise
    """
    if check_auth():
        return True
        
    console.print("[yellow]You need to authenticate with Google Cloud.[/yellow]")
    if click.confirm("Would you like to login now?", default=True):
        try:
            # Run gcloud auth application-default login with scopes
            scopes_arg = "--scopes=" + ",".join(SCOPES)
            result = subprocess.run(
                ["gcloud", "auth", "application-default", "login", scopes_arg],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                console.print("[green]Authentication successful![/green]")
                return True
            else:
                console.print(f"[red]Authentication failed: {result.stderr}[/red]")
                return False
                
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error running gcloud login: {str(e)}[/red]")
            return False
        except FileNotFoundError:
            console.print("[red]Error: gcloud CLI not found. Please install the Google Cloud SDK.[/red]")
            return False
    
    return False 