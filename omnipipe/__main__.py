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
def context():
    """
    View or set the current pipeline context (e.g., Project, Shot, Task).
    """
    typer.echo("Current context: None")

if __name__ == "__main__":
    app()
