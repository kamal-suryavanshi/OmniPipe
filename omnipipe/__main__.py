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


@app.command("create-shot")
def create_shot(
    studio_root: str = typer.Argument(..., help="Studio NAS root path (e.g. /mnt/nas/projects)"),
    project_code: str = typer.Argument(..., help="Project code (e.g. ACME_PROJ_2026)"),
    sequence: str = typer.Argument(..., help="Sequence name (e.g. sq001)"),
    shot: str = typer.Argument(..., help="Shot name (e.g. sh0030)"),
    config: str = typer.Option(None, "--config", help="Optional path to client_intake.yaml for dept/DCC lists"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview folders without creating them"),
):
    """
    Add a NEW shot to an existing project without re-running init_studio.

    Creates the full work/publish/render/cache tree for a single shot.
    Safe to run multiple times — skips folders that already exist.

    Example:
      omnipipe create-shot /mnt/nas ACME_PROJ sq003 sh0050
    """
    import sys
    from pathlib import Path

    # Load custom dept/DCC lists from intake form if provided
    DCCS       = ["maya", "nuke", "houdini", "blender"]
    SHOT_TASKS = ["anim", "comp", "fx", "lighting", "lookdev", "model", "render", "rig"]

    if config:
        try:
            import yaml
            with open(config, "r") as f:
                raw = yaml.safe_load(f)
            DCCS       = raw.get("dcc_software", DCCS)
            SHOT_TASKS = raw.get("departments",  SHOT_TASKS)
            typer.echo(f"  Loaded config: {config}")
        except Exception as e:
            typer.secho(f"  Warning: could not load config — using defaults: {e}", fg=typer.colors.YELLOW)

    shot_root = Path(studio_root) / project_code / "sequences" / sequence / shot

    if shot_root.exists() and not dry_run:
        typer.secho(f"  ⚠️  Shot folder already exists: {shot_root}", fg=typer.colors.YELLOW)

    folders_to_create = [shot_root / "_editorial"]
    for task in SHOT_TASKS:
        for dcc in DCCS:
            folders_to_create.append(shot_root / "work"    / dcc / task)
            folders_to_create.append(shot_root / "publish" / dcc / task)
        folders_to_create.append(shot_root / "render" / task)
        folders_to_create.append(shot_root / "cache"  / task)

    created = 0
    for folder in folders_to_create:
        if not folder.exists():
            if not dry_run:
                folder.mkdir(parents=True, exist_ok=True)
            created += 1

    mode = "[DRY RUN] Would create" if dry_run else "Created"
    typer.secho(f"\n  ✅  {mode} {created} folder(s) for {project_code}/{sequence}/{shot}", fg=typer.colors.GREEN)
    typer.echo(f"  Shot root: {shot_root}\n")


@app.command("doctor")
def doctor(
    studio_root: str = typer.Option(None, "--studio-root", help="NAS root to check mount/write access"),
    project_code: str = typer.Option(None, "--project", help="Project code to check stamp and license"),
):
    """
    Run a full post-deploy health check on this machine.
    """
    import sys, time
    from pathlib import Path
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn

    console = Console()
    issues = []

    console.print()
    console.print(Panel(f"[bold cyan]Platform:[/bold cyan] {sys.platform}  |  [bold cyan]Python:[/bold cyan] {sys.version.split()[0]}", title="[bold]OmniPipe Doctor — Environment Health Check[/bold]", border_style="cyan"))
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Status", style="dim", width=4)
    table.add_column("Check", min_width=30)
    table.add_column("Details")

    # ── 1. Python version ────────────────────────────────────────────────────
    v = sys.version_info
    if v >= (3, 10):
        table.add_row("✅", "Python Version", f"3.10+ ({v.major}.{v.minor})")
    else:
        msg = f"Python {v.major}.{v.minor} below required 3.10"
        table.add_row("❌", "Python Version", f"[red]{msg}[/red]")
        issues.append(msg)

    # ── 2. Core imports ──────────────────────────────────────────────────────
    for mod_name in ["omnipipe.core.context", "omnipipe.core.publish",
                     "omnipipe.core.license", "omnipipe.core.versioning"]:
        try:
            __import__(mod_name)
            table.add_row("✅", "Import", mod_name)
        except ImportError as e:
            msg = f"Cannot import {mod_name}: {e}"
            table.add_row("❌", "Import", f"[red]{msg}[/red]")
            issues.append(msg)

    # ── 3. License ───────────────────────────────────────────────────────────
    lic_path = Path.home() / "omnipipe.lic"
    if lic_path.exists():
        try:
            from omnipipe.core.license import validate_license
            ok, msg = validate_license()
            if ok:
                table.add_row("✅", "License Valid", f"[green]{msg}[/green]")
            else:
                table.add_row("❌", "License Invalid", f"[red]{msg}[/red]")
                issues.append(f"License invalid: {msg}")
        except Exception as e:
            table.add_row("⚠️", "License Error", f"[yellow]{e}[/yellow]")
    else:
        msg = f"No license file at {lic_path}"
        table.add_row("❌", "License Missing", f"[red]{msg}[/red]")
        issues.append(msg)

    # ── 4. Schema YAML ───────────────────────────────────────────────────────
    repo_root   = Path(__file__).parent.parent
    schema_path = repo_root / "configs" / "schema.yaml"
    if schema_path.exists():
        try:
            import yaml
            yaml.safe_load(schema_path.read_text())
            table.add_row("✅", "Schema YAML", "Parseable")
        except Exception as e:
            msg = f"schema.yaml parse error: {e}"
            table.add_row("❌", "Schema YAML", f"[red]{msg}[/red]")
            issues.append(msg)
    else:
        msg = f"schema.yaml missing at {schema_path}"
        table.add_row("❌", "Schema YAML", f"[red]{msg}[/red]")
        issues.append(msg)

    # ── 5. NAS root mount + write check ──────────────────────────────────────
    if studio_root:
        nas_path = Path(studio_root)
        if nas_path.exists():
            probe = nas_path / ".omnipipe_probe"
            try:
                probe.write_text("probe")
                probe.unlink()
                table.add_row("✅", "NAS Mount", f"Mounted & Writable: {nas_path}")
            except OSError as e:
                msg = f"NAS not writable: {e}"
                table.add_row("❌", "NAS Mount", f"[red]{msg}[/red]")
                issues.append(msg)
        else:
            msg = f"NAS root NOT mounted: {nas_path}"
            table.add_row("❌", "NAS Mount", f"[red]{msg}[/red]")
            issues.append(msg)
    else:
        table.add_row("⚠️", "NAS Mount", "[yellow]Skipped (use --studio-root)[/yellow]")

    # ── 6. Studio stamp ───────────────────────────────────────────────────────
    if studio_root and project_code:
        stamp = Path(studio_root) / project_code / ".omnipipe_stamp"
        if stamp.exists():
            table.add_row("✅", "Studio Stamp", f"Found: {stamp}")
        else:
            msg = f"Stamp missing (run init_studio.py first)"
            table.add_row("⚠️", "Studio Stamp", f"[yellow]{msg}[/yellow]")

    console.print(table)
    
    # ── Summary ───────────────────────────────────────────────────────────────
    if not issues:
        console.print("\n[bold green]🎉 All checks PASSED — this machine is pipeline-healthy![/bold green]\n")
        raise typer.Exit(0)
    else:
        console.print(f"\n[bold red]❌ {len(issues)} issue(s) found:[/bold red]")
        for i, issue in enumerate(issues, 1):
            console.print(f"  {i}. {issue}")
        console.print()
        raise typer.Exit(1)

@app.command("publish")
def publish(
    source: str = typer.Argument(..., help="Path to the source file to publish"),
    project: str = typer.Option(..., "--project", "-p", help="Project code"),
    sequence: str = typer.Option(..., "--sequence", "-sq", help="Sequence name"),
    shot: str = typer.Option(..., "--shot", "-sh", help="Shot name"),
    task: str = typer.Option(..., "--task", "-t", help="Task name (e.g. anim, comp)"),
    dcc: str = typer.Option("maya", "--dcc", "-d", help="DCC name (maya, nuke, silhouette)"),
    version: str = typer.Option(None, "--version", "-v", help="Version string (auto-detected if omitted)"),
    enable_tracking: bool = typer.Option(False, "--track-deps", help="Enable upstream dependency scanning"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate only — do not copy or write metadata"),
):
    """
    Publish a file through the full OmniPipe pipeline.

    Runs: License check → Validators → Extractors → Dependency Tracking → Metadata JSON.
    """
    import os, time
    from pathlib import Path as P
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    
    console = Console()

    # ── Validate source file exists ───────────────────────────────────────
    if not os.path.isfile(source):
        console.print(Panel(f"[bold red]❌ Source file not found:[/bold red]\n{source}", border_style="red"))
        raise typer.Exit(1)

    # ── License check (Layer 1) ───────────────────────────────────────────
    from omnipipe.core.license import validate_license
    with console.status("[cyan]Verifying OmniPipe license...", spinner="dots"):
        is_valid, lic_msg = validate_license()
        time.sleep(0.5) # subtle UX delay for checking
    
    if not is_valid:
        console.print(Panel(f"[bold red]❌ License Invalid:[/bold red] {lic_msg}\n[yellow]Publishing requires a valid license.[/yellow]", border_style="red"))
        raise typer.Exit(1)

    # ── Build context ─────────────────────────────────────────────────────
    from omnipipe.core.context import PipelineContext, PathResolver
    from omnipipe.core.versioning import get_latest_version, format_version, parse_version

    if not version:
        filename = os.path.basename(source)
        v = parse_version(filename)
        version = format_version(v) if v else "v001"

    ctx = PipelineContext(
        project=project, sequence=sequence, shot=shot,
        task=task, version=version.lstrip("v"), dcc=dcc,
    )

    # ── Resolve publish path from schema ──────────────────────────────────
    try:
        resolver = PathResolver()
        publish_path = resolver.resolve(f"publish_file_{dcc}", ctx)
    except Exception as e:
        console.print(Panel(f"[bold red]❌ Context Error:[/bold red] Could not resolve publish path:\n{e}", border_style="red"))
        raise typer.Exit(1)

    console.print(f"[bold blue]Pipeline Context:[/bold blue] {project} ⟩ {sequence} ⟩ {shot} ⟩ {task} ({dcc} {version})")
    console.print(f"  [dim]Source:[/dim] {source}")
    console.print(f"  [dim]Target:[/dim] {publish_path}")

    if dry_run:
        console.print("\n[bold yellow]⚠️ [DRY RUN] Validation passed. No files were written.[/bold yellow]\n")
        raise typer.Exit(0)

    # ── Run PublishEngine ─────────────────────────────────────────────────
    from omnipipe.core.publish import PublishEngine, PublishInstance

    inst = PublishInstance(
        name=os.path.splitext(os.path.basename(source))[0],
        context=ctx,
        source_path=source,
        publish_path=publish_path,
    )

    engine = PublishEngine(enable_tracking=enable_tracking)
    engine.add_instance(inst)

    console.print("\n[bold magenta]🚀 Executing Publish Pipeline...[/bold magenta]")
    
    # Fake progress wrapper to display beautiful UX over the exact engine.run() hook
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task1 = progress.add_task("[cyan]Validating and executing plugins...", total=None)
        success = engine.run()
        progress.update(task1, completed=100)

    if success:
        console.print(Panel(f"[bold green]🎉 Published successfully![/bold green]\nTarget: {publish_path}", title="Success", border_style="green"))
    else:
        console.print(Panel(f"[bold red]❌ Publish FAILED[/bold red]\nCheck logs for details.", border_style="red"))
        raise typer.Exit(1)


# -----------------------------------------------------------------------
# B2: LOAD-LATEST — Resolve the latest published version of a shot/task
# -----------------------------------------------------------------------
@app.command("load-latest")
def load_latest(
    project: str = typer.Argument(..., help="Project code"),
    sequence: str = typer.Argument(..., help="Sequence name (e.g. sq001)"),
    shot: str = typer.Argument(..., help="Shot name (e.g. sh0010)"),
    task: str = typer.Argument(..., help="Task name (e.g. anim, comp, fx)"),
    dcc: str = typer.Option("maya", "--dcc", "-d", help="DCC name (maya, nuke, silhouette)"),
):
    """
    Find and print the latest published file for a given shot/task/DCC.

    Scans the publish directory resolved from schema.yaml, finds the highest
    versioned file, and prints the full path. Useful for loaders and references.

    Example:
      omnipipe load-latest PROJ sq001 sh0010 anim --dcc maya
    """
    import os, glob
    from pathlib import Path as P
    from omnipipe.core.context import PipelineContext, PathResolver
    from omnipipe.core.versioning import get_latest_version, format_version

    # ── Resolve the publish directory from schema ─────────────────────────
    ctx = PipelineContext(
        project=project, sequence=sequence, shot=shot,
        task=task, version="001", dcc=dcc,
    )

    try:
        resolver = PathResolver()
        # Resolve a versioned publish path, then strip to get directory
        sample_path = resolver.resolve(f"publish_file_{dcc}", ctx)
        publish_dir = str(P(sample_path).parent)
    except Exception as e:
        typer.secho(f"\n  ❌  Could not resolve publish directory: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)

    typer.echo(f"  Publish dir: {publish_dir}")

    # ── Check directory exists ────────────────────────────────────────────
    if not os.path.isdir(publish_dir):
        typer.secho(f"  ⚠️   Directory does not exist yet — no publishes found.", fg=typer.colors.YELLOW)
        typer.echo(f"  (Expected at: {publish_dir})\n")
        raise typer.Exit(1)

    # ── Scan for latest versioned file ────────────────────────────────────
    # DCC extension map
    EXT_MAP = {
        "maya": ".ma", "nuke": ".nk", "houdini": ".hip",
        "blender": ".blend", "silhouette": ".sfx",
    }
    ext = EXT_MAP.get(dcc.lower(), ".*")

    files = sorted([
        f for f in os.listdir(publish_dir)
        if f.endswith(ext) or ext == ".*"
    ])

    if not files:
        typer.secho(f"  ⚠️   No published files found in: {publish_dir}", fg=typer.colors.YELLOW)
        raise typer.Exit(1)

    # Find highest version among the files
    from omnipipe.core.versioning import parse_version
    best_file = None
    best_ver  = 0
    for f in files:
        v = parse_version(f)
        if v and v > best_ver:
            best_ver  = v
            best_file = f

    if not best_file:
        typer.secho(f"  ⚠️   Files found but none match version pattern (_vNNN): {files}", fg=typer.colors.YELLOW)
        raise typer.Exit(1)

    latest_path = os.path.join(publish_dir, best_file)
    typer.secho(f"\n  📦  Latest publish: {best_file}  (v{best_ver:03d})", fg=typer.colors.CYAN, bold=True)
    typer.echo(f"  Full path: {latest_path}\n")


if __name__ == "__main__":
    app()
