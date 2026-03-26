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
    import os
    from omnipipe.core.pipeline import PipelineAPI
    
    api = PipelineAPI()
    
    # Smart OS Environment Warning for Windows users
    if sys.platform == "win32" and "STUDIO_ROOT" not in os.environ:
        typer.secho("\n[WARNING] You are running on Windows, but STUDIO_ROOT is missing from your .env file.", fg=typer.colors.YELLOW)
        typer.secho("The pipeline is temporarily falling back to a Linux path (/tmp/studio/).", fg=typer.colors.YELLOW)
        typer.secho("Please create an .env file and set a valid Windows drive (e.g., STUDIO_ROOT=Z:/Pipeline)\n", fg=typer.colors.YELLOW)
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

@app.command("test-dcc")
def test_dcc(dcc: str = typer.Argument("maya", help="The DCC software to test (e.g., maya, nuke)")):
    """
    Ping the Headless Integrations (Maya/Nuke) without needing to open the software!
    """
    from omnipipe.dcc import get_dcc
    
    loader = get_dcc(dcc)
    if not loader:
        typer.secho(f"Error: DCC '{dcc}' is not implemented.", fg=typer.colors.RED)
        raise typer.Exit(1)
        
    typer.secho(f"\n--- Pinging {dcc.upper()} Headless Integration ---", fg=typer.colors.CYAN)
    typer.echo(f"1. Current File Status: {loader.get_current_file()}")
    
    test_path_work = f"/tmp/studio/TEST_PROJ/work/{dcc.lower()}/test_scene_v01.ext"
    test_path_pub = f"/tmp/studio/TEST_PROJ/publish/{dcc.lower()}/test_scene_v01.ext"
    
    typer.echo(f"\n2. Simulating Save Hook...")
    loader.save_as(test_path_work)
    
    typer.echo(f"\n3. Simulating Publish Hook...")
    loader.publish(test_path_pub)
    
    typer.secho(f"\n--- {dcc.upper()} Testing Complete ---\n", fg=typer.colors.GREEN)

if __name__ == "__main__":
    app()
