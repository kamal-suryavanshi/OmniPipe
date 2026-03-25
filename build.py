import os
import sys
import subprocess
import shutil
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent
ENTRY_POINT = ROOT_DIR / "omnipipe" / "__main__.py"
BIN_DIR = ROOT_DIR / "bin"
BUILD_DIR = ROOT_DIR / "builds"
VENDOR_DIR = ROOT_DIR / "omnipipe" / "vendor"

# OS Detection and Naming
if sys.platform == "win32":
    os_name = "win"
    binary_name = "omnipipe-win.exe"
elif sys.platform == "darwin":
    os_name = "mac"
    binary_name = "omnipipe-mac"
else:
    os_name = "linux"
    binary_name = "omnipipe-linux"

def compile_nuitka():
    print(f"Starting Nuitka C++ compilation for {os_name.upper()}...")
    BIN_DIR.mkdir(exist_ok=True)
    
    # We must inject our vendor folder into the PYTHONPATH so Nuitka's static 
    # analyzer can find 'typer' and 'gazu' during C-translation!
    env = os.environ.copy()
    env["PYTHONPATH"] = str(VENDOR_DIR.absolute()) + os.pathsep + env.get("PYTHONPATH", "")
    
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--assume-yes-for-downloads",
        f"--output-dir={BUILD_DIR}",
        f"--output-filename={binary_name}",
        str(ENTRY_POINT)
    ]
    
    try:
        # Run Nuitka Compiler
        subprocess.run(cmd, env=env, check=True)
        print(f"Compilation successful! Raw binary built at: {BUILD_DIR}/{binary_name}")
        
        # Copy to the final bin/ directory for distribution
        compiled_file = BUILD_DIR / binary_name
        dest_file = BIN_DIR / binary_name
        
        if compiled_file.exists():
            shutil.copy2(compiled_file, dest_file)
            print(f"Successfully deployed to {dest_file}")
            print(f"---> You can now share {dest_file} with your clients safely!")
            
    except subprocess.CalledProcessError as e:
        print(f"Compilation failed. Make sure you have a C-compiler installed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    compile_nuitka()
