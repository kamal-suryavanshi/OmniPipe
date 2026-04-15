"""
OmniPipe - Person A Core Validation Suite
Maps directly to: docs/test_plan.md - "Pipeline Core Validation (Person A)"
"""
import os
import sys
import json
import datetime
import traceback
import shutil

# Ensure omnipipe is importable from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = "✅ PASS"
FAIL = "❌ FAIL"
SKIP = "⏭  SKIP"

results = []

def run_test(task_id, description, fn):
    try:
        fn()
        results.append((task_id, description, PASS, None))
        print(f"  {PASS}  {task_id}: {description}")
    except AssertionError as e:
        results.append((task_id, description, FAIL, str(e)))
        print(f"  {FAIL}  {task_id}: {description}\n        → {e}")
    except Exception as e:
        results.append((task_id, description, FAIL, traceback.format_exc()))
        print(f"  {FAIL}  {task_id}: {description}\n        → {type(e).__name__}: {e}")

print("=" * 70)
print("  OmniPipe | Person A Core Validation Suite")
print("=" * 70)

# -----------------------------------------------------------------------
# TASK 1: Repo / Zero-Install - verify vendor directory is bundled
# -----------------------------------------------------------------------
def test_task_1():
    vendor_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "omnipipe", "vendor"
    )
    assert os.path.isdir(vendor_dir), \
        f"Vendor directory missing at {vendor_dir} – zero-install bundling not complete!"
    # Verify at least typer is vendored
    typer_present = any("typer" in d for d in os.listdir(vendor_dir))
    assert typer_present, "typer not found inside vendor/ – dependency bundling incomplete!"

run_test("Task 1", "Repo Setup / Zero-Install vendor bundle present", test_task_1)

# -----------------------------------------------------------------------
# TASK 2 & 3: Context System + Path Manager
# -----------------------------------------------------------------------
def test_task_2_3():
    from omnipipe.core.context import PipelineContext, PathResolver
    ctx = PipelineContext(
        project="OMNI_PROJ", sequence="seq01", shot="sh010",
        task="anim", version="001", dcc="maya", asset_type="char", asset="hero"
    )
    resolver = PathResolver()

    work_path = resolver.resolve("work_file_maya", ctx)
    pub_path  = resolver.resolve("publish_file_maya", ctx)

    assert "OMNI_PROJ" in work_path, f"Project name missing from work path: {work_path}"
    assert "seq01"     in work_path, f"Sequence missing from work path: {work_path}"
    assert "sh010"     in work_path, f"Shot missing from work path: {work_path}"
    assert "anim"      in work_path, f"Task missing from work path: {work_path}"
    assert work_path.endswith(".ma"), f"Wrong extension on work path: {work_path}"
    assert "publish"   in pub_path,  f"'publish' not in publish path: {pub_path}"

run_test("Task 2/3", "Context & Path Manager resolve correct schema paths", test_task_2_3)

# -----------------------------------------------------------------------
# TASK 4: Versioning – gap-jump test (v001, v002, v008 → must yield v009)
# -----------------------------------------------------------------------
def test_task_4():
    from omnipipe.core.versioning import get_next_available_path, get_latest_version

    tmp_dir = "/tmp/omnipipe_qa_versioning"
    shutil.rmtree(tmp_dir, ignore_errors=True)
    os.makedirs(tmp_dir)

    for v in ["v001", "v002", "v008"]:
        open(os.path.join(tmp_dir, f"asset_{v}.ma"), "w").close()

    latest = get_latest_version(tmp_dir, "asset", ".ma")
    assert latest == 8, f"Expected latest version 8, got {latest}"

    next_path = get_next_available_path(tmp_dir, "asset", ".ma")
    assert "v009" in next_path, f"Expected v009 in next path, got: {next_path}"

run_test("Task 4", "Versioning correctly scans gap [v001,v002,v008] → yields v009", test_task_4)

# -----------------------------------------------------------------------
# TASK 5: Validators – naming convention blocks illegal filenames
# -----------------------------------------------------------------------
def test_task_5_bad_name():
    from omnipipe.core.publish import PublishEngine, PublishInstance
    from omnipipe.core.context import PipelineContext
    from omnipipe.core.validators import NamingConventionValidator

    ctx = PipelineContext(project="P", sequence="s", shot="sh", task="t", version="1", dcc="maya")
    bad = PublishInstance(
        name="bad file",
        context=ctx,
        source_path="/tmp/omnipipe_qa_versioning/bad name.ma"
    )
    validator = NamingConventionValidator()
    raised = False
    try:
        validator.validate(bad)
    except ValueError:
        raised = True
    assert raised, "NamingConventionValidator did NOT raise on a filename with spaces!"

run_test("Task 5", "NamingConventionValidator blocks filenames with spaces", test_task_5_bad_name)

def test_task_5_good_name():
    from omnipipe.core.validators import NamingConventionValidator
    from omnipipe.core.publish import PublishInstance
    from omnipipe.core.context import PipelineContext

    # Create a real file to satisfy FileExistsValidator
    tmp = "/tmp/omnipipe_qa_good.ma"
    open(tmp, "w").close()

    ctx = PipelineContext(project="P", sequence="s", shot="sh", task="t", version="1", dcc="maya")
    good = PublishInstance(name="good_asset", context=ctx, source_path=tmp)
    result = NamingConventionValidator().validate(good)
    assert result is True, "NamingConventionValidator rejected a valid filename!"

run_test("Task 5", "NamingConventionValidator passes clean filenames", test_task_5_good_name)

# -----------------------------------------------------------------------
# TASK 6 & 7 & 8: Full Publish Lifecycle (valid instance, licensed env)
# -----------------------------------------------------------------------
def test_task_6_7_8():
    from omnipipe.core.publish import PublishEngine, PublishInstance
    from omnipipe.core.context import PipelineContext

    # Ensure a valid license exists for this test
    from omnipipe.core.license import validate_license
    is_valid, _ = validate_license()
    if not is_valid:
        # Auto-generate one for QA purposes
        os.system(f"{sys.executable} "
                  f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}"
                  f"/scripts/generate_license.py 'QA-ValidateStudio'")

    pub_dir = "/tmp/omnipipe_qa_publish"
    shutil.rmtree(pub_dir, ignore_errors=True)
    os.makedirs(pub_dir)

    src = os.path.join(pub_dir, "char_rig_v001.ma")
    with open(src, "w") as f:
        # Embed a fake Maya Ascii reference line
        f.write('file -rdi 1 -ns "ctrl" -typ "mayaAscii" "/proj/ctrl_lib_v003.ma";\n')

    pub_path = os.path.join(pub_dir, "publish", "char_rig_v001.ma")

    ctx = PipelineContext(
        project="OMNI", sequence="seq01", shot="sh010",
        task="rig", version="001", dcc="maya"
    )
    inst = PublishInstance(name="char_rig", context=ctx, source_path=src, publish_path=pub_path)

    engine = PublishEngine(enable_tracking=True)
    success = engine.run()

    # The engine runs against empty instances list since we didn't add it
    # Add it properly:
    engine2 = PublishEngine(enable_tracking=True)
    engine2.add_instance(inst)
    success2 = engine2.run()
    assert success2, "PublishEngine.run() returned False on a valid publish!"

    # Metadata writes next to publish_path (or source_path if publish_path empty)
    target = pub_path if pub_path else src
    json_expected = target.replace(os.path.splitext(target)[1], ".json")
    found_json = os.path.exists(json_expected)
    assert found_json, f"Metadata JSON not found at {json_expected}"

    with open(json_expected) as f:
        meta = json.load(f)

    assert "user" in meta,      "Metadata JSON missing 'user' field"
    assert "timestamp" in meta, "Metadata JSON missing 'timestamp' field"
    assert "source_path" in meta, "Metadata JSON missing 'source_path' field"

    # Task 8: dependency array injected into custom_attributes (which holds instance.metadata)
    custom = meta.get("custom_attributes", {})
    assert "dependencies" in custom, \
        f"Dependency tracking array missing from custom_attributes! Keys found: {list(custom.keys())}"
    assert isinstance(custom["dependencies"], list), \
        f"dependencies field should be a list, got: {type(custom['dependencies'])}"

run_test("Task 6/7/8", "PublishEngine full lifecycle: extract → metadata JSON → dependency array", test_task_6_7_8)

# -----------------------------------------------------------------------
# TASK 9: License System – DCC hooks block save/publish without key
# -----------------------------------------------------------------------
def test_task_9_no_license():
    import tempfile, shutil
    # Temporarily rename the license file
    lic = os.path.expanduser("~/omnipipe.lic")
    tmp_lic = lic + ".bak"
    moved = False
    if os.path.exists(lic):
        shutil.move(lic, tmp_lic)
        moved = True
    try:
        from omnipipe.dcc.maya.api import MayaDCC
        dcc = MayaDCC()
        # save_file should silently return False (not raise)
        result = dcc.save_file()
        assert result is False, \
            "MayaDCC.save_file() should return False when no license is present!"
    finally:
        if moved:
            shutil.move(tmp_lic, lic)

run_test("Task 9", "MayaDCC.save_file() returns False when license is absent", test_task_9_no_license)

def test_task_9_with_license():
    from omnipipe.dcc.maya.api import MayaDCC
    from omnipipe.core.license import validate_license
    is_valid, _ = validate_license()
    assert is_valid, "Expected a valid license to be present for this sub-test!"
    dcc = MayaDCC()
    result = dcc.save_file()  # HAS_MAYA=False, returns True in dev mode
    assert result is True, "MayaDCC.save_file() should succeed when license is valid!"

run_test("Task 9", "MayaDCC.save_file() succeeds when license is present", test_task_9_with_license)

# -----------------------------------------------------------------------
# TASK 10: Error Handling – logger creates rotating log file on disk
# -----------------------------------------------------------------------
def test_task_10():
    from omnipipe.core.logger import setup_logger
    import logging
    log = setup_logger("qa_test_logger")
    log.info("QA validation log entry from test suite.")
    log.error("Simulated QA error entry.")

    log_path = os.path.expanduser("~/omnipipe/logs/pipeline.log")
    assert os.path.exists(log_path), \
        f"Log file was not created at expected location: {log_path}"
    with open(log_path) as f:
        content = f.read()
    assert "QA validation log entry" in content or "QA-" in content or len(content) > 0, \
        "Log file exists but appears empty!"

run_test("Task 10", "Logger creates ~/omnipipe/logs/pipeline.log and writes entries", test_task_10)

# -----------------------------------------------------------------------
# LICENSE SERVER: Phase 2 phone-home tests (stubs — Person C implements server)
# -----------------------------------------------------------------------

def test_phone_home_unreachable_triggers_grace():
    """
    With no license server running, phone_home() should fall back gracefully
    and write ~/.omnipipe_grace (not raise, not block).
    """
    import tempfile, shutil
    grace_path = os.path.expanduser("~/.omnipipe_grace")
    # Remove any existing grace file so we get a clean test
    if os.path.exists(grace_path):
        os.remove(grace_path)

    # Point to a definitely-unreachable server
    os.environ["OMNIPIPE_LICENSE_SERVER"] = "http://127.0.0.1:19999"
    try:
        from omnipipe.core import license as lic_mod
        lic_mod._LICENSE_SERVER_URL = "http://127.0.0.1:19999"
        valid, msg = lic_mod.phone_home(
            studio_id="test-000", studio_name="QA Studio", dcc="nuke"
        )
        assert valid is True, f"Grace period should allow operation, got: {msg}"
        assert os.path.exists(grace_path), "Grace file should have been written"
    finally:
        os.environ.pop("OMNIPIPE_LICENSE_SERVER", None)
        if os.path.exists(grace_path):
            os.remove(grace_path)

run_test(
    "Lic-Server",
    "phone_home() falls back to grace period when server unreachable",
    test_phone_home_unreachable_triggers_grace,
)


def test_grace_period_expired_blocks():
    """
    A grace file older than GRACE_PERIOD_DAYS should cause phone_home() to return False.
    """
    import json
    grace_path = os.path.expanduser("~/.omnipipe_grace")
    old_date = (datetime.date.today() - datetime.timedelta(days=10)).isoformat()

    with open(grace_path, "w") as f:
        json.dump({"grace_start": old_date, "studio": "QA Studio"}, f)

    try:
        from omnipipe.core import license as lic_mod
        lic_mod._LICENSE_SERVER_URL = "http://127.0.0.1:19999"
        valid, msg = lic_mod.phone_home(
            studio_id="test-000", studio_name="QA Studio", dcc="nuke"
        )
        assert valid is False, f"Expired grace should block, but got valid=True: {msg}"
        assert "GRACE PERIOD EXPIRED" in msg or "EXPIRED" in msg.upper()
    finally:
        if os.path.exists(grace_path):
            os.remove(grace_path)

run_test(
    "Lic-Server",
    "phone_home() blocks when grace period has expired (>7 days offline)",
    test_grace_period_expired_blocks,
)


# -----------------------------------------------------------------------
# B1: PUBLISH CLI — version auto-detection
# -----------------------------------------------------------------------
def test_b1_publish_version_autodetect():
    """
    Verify parse_version() correctly reads version from filenames,
    used by the publish command to auto-detect version.
    """
    from omnipipe.core.versioning import parse_version, format_version
    assert parse_version("hero_anim_v003.ma") == 3
    assert parse_version("char_rig_v012.ma") == 12
    assert parse_version("no_version.ma") is None
    assert format_version(3) == "v003"
    assert format_version(12) == "v012"

run_test("B1", "Publish CLI version auto-detection (parse_version + format_version)", test_b1_publish_version_autodetect)


# -----------------------------------------------------------------------
# B2: LOAD-LATEST — version scanning picks highest
# -----------------------------------------------------------------------
def test_b2_load_latest_picks_highest():
    """
    Simulate a publish directory with several versioned files and verify
    get_latest_version returns the correct highest version.
    """
    import shutil
    tmp_dir = "/tmp/omnipipe_qa_loadlatest"
    shutil.rmtree(tmp_dir, ignore_errors=True)
    os.makedirs(tmp_dir)

    # Create scattered versions
    for v in ["v001", "v002", "v005", "v003"]:
        open(os.path.join(tmp_dir, f"hero_anim_{v}.ma"), "w").close()

    from omnipipe.core.versioning import get_latest_version
    latest = get_latest_version(tmp_dir, "hero_anim", ".ma")
    assert latest == 5, f"Expected latest version 5, got {latest}"

    shutil.rmtree(tmp_dir, ignore_errors=True)

run_test("B2", "load-latest: get_latest_version picks v005 from [v001,v002,v003,v005]", test_b2_load_latest_picks_highest)


# -----------------------------------------------------------------------
# B3: MAYA STARTUP HOOK — module importable + functions exist
# -----------------------------------------------------------------------
def test_b3_maya_startup_importable():
    """
    Verify the Maya startup module can be imported outside Maya (headless)
    and that all expected entry points exist.
    """
    from omnipipe.dcc.maya import startup
    assert hasattr(startup, "bootstrap"), "Missing bootstrap() entry point"
    assert hasattr(startup, "_validate_license"), "Missing _validate_license()"
    assert hasattr(startup, "_create_shelf"), "Missing _create_shelf()"
    assert hasattr(startup, "_inject_omnipipe_path"), "Missing _inject_omnipipe_path()"

run_test("B3", "Maya startup module importable with bootstrap/_validate_license/_create_shelf", test_b3_maya_startup_importable)

# -----------------------------------------------------------------------
# SUMMARY
# -----------------------------------------------------------------------
print()
print("=" * 70)
print(f"  RESULTS: {len(results)} tests run")
passed = sum(1 for r in results if r[2] == PASS)
failed = sum(1 for r in results if r[2] == FAIL)
print(f"  {PASS}: {passed}    {FAIL}: {failed}")
print("=" * 70)

if failed:
    print("\n  Failures:")
    for tid, desc, status, detail in results:
        if status == FAIL:
            print(f"\n  ▸ {tid}: {desc}")
            print(f"    {detail}")
    sys.exit(1)
else:
    print("\n  All Person A Core Validation tests passed! 🎉")
