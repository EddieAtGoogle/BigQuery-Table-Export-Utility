#!/usr/bin/env python3
"""
BigQuery Table Export CLI

A command-line interface for exporting BigQuery tables to CSV files in Google Cloud Storage.
For more information, see: https://cloud.google.com/bigquery/docs/exporting-data
"""

import sys
from typing import Optional, Dict, Any
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import IntPrompt, Confirm

from .api import APIClient, APIError
from .auth import check_auth, ensure_auth
from .config import get_config

# Initialize Rich console for pretty output
console = Console()

def select_from_list(prompt: str, max_value: int) -> int:
    """Get a valid selection from the user."""
    while True:
        try:
            value = IntPrompt.ask(
                prompt,
                console=console,
                show_default=False
            )
            if 1 <= value <= max_value:
                return value
            console.print(f"[red]Please enter a number between 1 and {max_value}[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")

def format_size(size_bytes: int) -> str:
    """Format size in bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """BigQuery Table Export Utility - Export tables to CSV files in Google Cloud Storage."""
    pass

@cli.command()
def interactive():
    """Start an interactive session to export BigQuery tables."""
    try:
        # Ensure user is authenticated
        if not check_auth():
            if not ensure_auth():
                console.print("[red]Authentication required. Please run 'gcloud auth login' first.[/red]")
                sys.exit(1)
        
        # Initialize API client
        config = get_config()
        client = APIClient(config.api_url)
        
        while True:
            try:
                # Step 1: List and select dataset
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    progress.add_task(description="Fetching datasets...", total=None)
                    datasets = client.list_datasets()
                
                if not datasets:
                    console.print("[yellow]No datasets found or no access to any datasets.[/yellow]")
                    sys.exit(1)
                
                # Display datasets
                table = Table(title="Available Datasets")
                table.add_column("Number", justify="right", style="cyan")
                table.add_column("Dataset ID", style="green")
                table.add_column("Location", style="blue")
                
                for idx, dataset in enumerate(datasets, 1):
                    table.add_row(
                        str(idx),
                        dataset['id'],
                        dataset['location']
                    )
                
                console.print(table)
                
                # Get dataset selection
                dataset_idx = select_from_list(
                    "\nEnter the number of the dataset to export from",
                    len(datasets)
                )
                selected_dataset = datasets[dataset_idx - 1]
                
                # Step 2: List and select table
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    progress.add_task(
                        description=f"Fetching tables from {selected_dataset['id']}...",
                        total=None
                    )
                    tables = client.list_tables(selected_dataset['id'])
                
                if not tables:
                    console.print(f"[yellow]No tables found in dataset {selected_dataset['id']}[/yellow]")
                    if Confirm.ask("Would you like to select a different dataset?"):
                        continue
                    sys.exit(0)
                
                # Display tables
                table = Table(title=f"Tables in {selected_dataset['id']}")
                table.add_column("Number", justify="right", style="cyan")
                table.add_column("Table ID", style="green")
                table.add_column("Type", style="blue")
                table.add_column("Size", style="magenta")
                table.add_column("Rows", style="yellow")
                
                for idx, table_info in enumerate(tables, 1):
                    table.add_row(
                        str(idx),
                        table_info['id'],
                        table_info['type'],
                        format_size(table_info['size_bytes']) if table_info['size_bytes'] else "Unknown",
                        f"{table_info['num_rows']:,}" if table_info['num_rows'] else "Unknown"
                    )
                
                console.print(table)
                
                # Get table selection
                table_idx = select_from_list(
                    "\nEnter the number of the table to export",
                    len(tables)
                )
                selected_table = tables[table_idx - 1]
                
                # Step 3: Configure and start export
                # console.print("\n[bold]Export Configuration[/bold]")
                # compression = Confirm.ask(
                #     "Would you like to compress the output file?",
                #     default=True
                # )

                # Disable compression by default because compressed CSV files cannot be merged in single file
                compression = False
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    # Start export
                    task = progress.add_task(
                        description="Exporting table...",
                        total=None
                    )
                    
                    export_result = client.export_table(
                        dataset_id=selected_dataset['id'],
                        table_id=selected_table['id'],
                        compression=compression
                    )
                    
                    # If multiple files were created, merge them and compress the output file
                    if len(export_result['files']) > 1:
                        progress.update(task, description="Merging exported files...")
                        merge_result = client.merge_files(
                            source_prefix=export_result['destination_prefix'],
                            destination_filename=f"{selected_table['id']}.csv",
                            compress_output=True
                        )
                        final_file = merge_result['merged_file']
                    else:
                        final_file = export_result['files'][0]
                    
                    # Generate download URL
                    progress.update(task, description="Generating download URL...")
                    download_url = client.get_download_url(final_file)
                
                # Display results
                console.print("\n[green]Export completed successfully![/green]")
                console.print("\nThe exported file is available in Google Cloud Storage.")
                console.print("You can access it through:")
                console.print("1. [blue]Google Cloud Console[/blue]: " + download_url)
                console.print("2. [blue]gsutil[/blue] command:")
                console.print(f"   [yellow]gsutil cp gs://{export_result['files'][0]} ./[/yellow]")
                console.print("\n[yellow]Note: You need to be authenticated to Google Cloud to access the file.[/yellow]")
                console.print("To authenticate:")
                console.print("- Browser: Log in to Google Cloud Console")
                console.print("- Command line: Run [yellow]gcloud auth login[/yellow]")
                
                # Ask if user wants to export another table
                if not Confirm.ask("\nWould you like to export another table?"):
                    console.print("[green]Goodbye![/green]")
                    break
                
            except APIError as e:
                console.print(f"[red]API Error: {str(e)}[/red]")
                if not Confirm.ask("Would you like to try again?"):
                    break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
                if not Confirm.ask("Would you like to try again?"):
                    break
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    cli() 