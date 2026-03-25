import sys
from pathlib import Path

# Inject local vendor dependencies for zero-install workflows
VENDOR_DIR = Path(__file__).parent / "vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR.absolute()))

import typer

app = typer.Typer(help="OmniPipe Core CLI")

@app.callback()
def callback():
    """
    OmniPipe - A unified CLI for CG/VFX Workflows.
    """
    pass

@app.command()
def init():
    """
    Initialize the pipeline environment for a user or team.
    """
    typer.echo("Initializing OmniPipe...")

@app.command()
def login():
    """
    Authenticate with the central Asset Management System (Kitsu).
    """
    from omnipipe.core.pipeline import PipelineAPI
    api = PipelineAPI()
    typer.echo("Attempting to connect to Kitsu via API...")
    if api.login():
        typer.echo("Success! Connected to Asset Manager.")
    else:
        typer.echo("Failed to connect. Please check your .env credentials or ensure the server is running.")

@app.command()
def context(project: str, sequence: str = "seq01", shot: str = "sh010", task: str = "anim", version: str = "001", dcc: str = "maya"):
    """
    Test resolving the pipeline context paths against your schema.yaml
    """
    from omnipipe.core.pipeline import PipelineAPI
    
    api = PipelineAPI()
    ctx = api.build_context(project, sequence, shot, task, version, dcc)
    
    typer.echo(f"Resolving paths for Project: [ {project} ]")
    typer.echo("-" * 40)
    
    try:
        work_path = api.resolver.resolve(f"work_file_{dcc}", ctx)
        typer.echo(f"Work File: {work_path}")
        
        pub_path = api.resolver.resolve(f"publish_file_{dcc}", ctx)
        typer.echo(f"Publish File: {pub_path}")
    except Exception as e:
        typer.echo(f"Error resolving paths: {e}")

if __name__ == "__main__":
    app()
