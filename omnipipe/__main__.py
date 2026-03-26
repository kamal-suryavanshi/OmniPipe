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

    Validates:
      • Python version
      • pip dependencies importable
      • License file present and cryptographically valid
      • NAS root is mounted and writable (if --studio-root provided)
      • schema.yaml is parseable
      • Studio stamp file exists (if --project provided)

    Exit code 0 = fully healthy. Non-zero = at least one check failed.
    """
    import sys
    from pathlib import Path

    issues = []

    typer.echo()
    typer.secho("  OmniPipe Doctor — Environment Health Check", bold=True)
    typer.echo(f"  Platform : {sys.platform}  |  Python {sys.version.split()[0]}")
    typer.echo("  " + "─" * 60)

    # ── 1. Python version ────────────────────────────────────────────────────
    v = sys.version_info
    if v >= (3, 10):
        typer.secho(f"  ✅  Python {v.major}.{v.minor} — OK", fg=typer.colors.GREEN)
    else:
        msg = f"Python {v.major}.{v.minor} below required 3.10"
        typer.secho(f"  ❌  {msg}", fg=typer.colors.RED)
        issues.append(msg)

    # ── 2. Core imports ──────────────────────────────────────────────────────
    for mod_name in ["omnipipe.core.context", "omnipipe.core.publish",
                     "omnipipe.core.license", "omnipipe.core.versioning"]:
        try:
            __import__(mod_name)
            typer.secho(f"  ✅  Import {mod_name}", fg=typer.colors.GREEN)
        except ImportError as e:
            msg = f"Cannot import {mod_name}: {e}"
            typer.secho(f"  ❌  {msg}", fg=typer.colors.RED)
            issues.append(msg)

    # ── 3. License ───────────────────────────────────────────────────────────
    lic_path = Path.home() / "omnipipe.lic"
    if lic_path.exists():
        try:
            from omnipipe.core.license import validate_license
            ok, msg = validate_license()
            if ok:
                typer.secho(f"  ✅  License: {msg}", fg=typer.colors.GREEN)
            else:
                typer.secho(f"  ❌  License INVALID: {msg}", fg=typer.colors.RED)
                issues.append(f"License invalid: {msg}")
        except Exception as e:
            typer.secho(f"  ⚠️   License check error: {e}", fg=typer.colors.YELLOW)
    else:
        msg = f"No license file at {lic_path}"
        typer.secho(f"  ❌  {msg}", fg=typer.colors.RED)
        issues.append(msg)

    # ── 4. Schema YAML ───────────────────────────────────────────────────────
    repo_root   = Path(__file__).parent.parent
    schema_path = repo_root / "configs" / "schema.yaml"
    if schema_path.exists():
        try:
            import yaml
            yaml.safe_load(schema_path.read_text())
            typer.secho(f"  ✅  schema.yaml parseable", fg=typer.colors.GREEN)
        except Exception as e:
            msg = f"schema.yaml parse error: {e}"
            typer.secho(f"  ❌  {msg}", fg=typer.colors.RED)
            issues.append(msg)
    else:
        msg = f"schema.yaml missing at {schema_path}"
        typer.secho(f"  ❌  {msg}", fg=typer.colors.RED)
        issues.append(msg)

    # ── 5. NAS root mount + write check ──────────────────────────────────────
    if studio_root:
        nas_path = Path(studio_root)
        if nas_path.exists():
            # Check writable
            probe = nas_path / ".omnipipe_probe"
            try:
                probe.write_text("probe")
                probe.unlink()
                typer.secho(f"  ✅  NAS root mounted and writable: {nas_path}", fg=typer.colors.GREEN)
            except OSError as e:
                msg = f"NAS not writable: {e}"
                typer.secho(f"  ❌  {msg}", fg=typer.colors.RED)
                issues.append(msg)
        else:
            msg = f"NAS root NOT mounted: {nas_path}"
            typer.secho(f"  ❌  {msg}", fg=typer.colors.RED)
            issues.append(msg)
    else:
        typer.secho("  ⚠️   NAS root not supplied — skipping mount check (use --studio-root)", fg=typer.colors.YELLOW)

    # ── 6. Studio stamp ───────────────────────────────────────────────────────
    if studio_root and project_code:
        stamp = Path(studio_root) / project_code / ".omnipipe_stamp"
        if stamp.exists():
            typer.secho(f"  ✅  Studio stamp found: {stamp}", fg=typer.colors.GREEN)
        else:
            msg = f"Studio stamp missing — run init_studio.py first: {stamp}"
            typer.secho(f"  ⚠️   {msg}", fg=typer.colors.YELLOW)

    # ── Summary ───────────────────────────────────────────────────────────────
    typer.echo("  " + "─" * 60)
    if not issues:
        typer.secho("\n  🎉  All checks PASSED — this machine is pipeline-healthy!\n", fg=typer.colors.GREEN)
        raise typer.Exit(0)
    else:
        typer.secho(f"\n  ❌  {len(issues)} issue(s) found:\n", fg=typer.colors.RED)
        for i, issue in enumerate(issues, 1):
            typer.echo(f"     {i}. {issue}")
        typer.echo()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
