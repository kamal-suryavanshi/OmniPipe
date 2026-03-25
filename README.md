# OmniPipe Core

A generic, production-ready CG Studio Pipeline core designed for distributed teams.

## Features
- Fully Decoupled Architecture
- Context-Driven API
- Agnostic Asset Management (Kitsu enabled by default)
- **100% Secure Nuitka Compilation (AOT C++)**
- **Cross-OS Compatibility (Windows / Mac / Linux)**

## Getting Started (For End Users / Artists)

End users **do not need Python or Poetry or PIP**. They simply run the wrapper script designed for their OS! It automatically executes the mathematically secure C++ binary in the background.

- **Windows:** Double-click `omnipipe.bat` or run it in CMD:
  ```cmd
  omnipipe.bat login
  ```
- **Mac / Linux:** Run the shell script:
  ```bash
  ./omnipipe.sh login
  ```

---

## Getting Started (For Pipeline Developers)

If you modify the raw Python code centrally, you must recompile the binaries to deploy securely to clients.

1. **Install Compiler Dependencies:**
   Ensure you have a C-Compiler (Visual Studio on Win, GCC/Clang on Mac/Linux).
   ```bash
   pip install nuitka zstandard
   ```
2. **Compile the Binary:**
   Run the build script on the operating system you want to generate a secure `.exe`/binary for:
   ```bash
   python build.py
   ```
   *This automatically translates your Python code into C++ and outputs the secure binary straight into the `bin/` folder!*
