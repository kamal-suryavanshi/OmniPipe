# Welcome to OmniPipe

**OmniPipe** is a generic, production-ready CG Studio Pipeline core designed to operate seamlessly across distributed, multi-site teams. 

It uses a fully decoupled architecture powered by Python and a custom Context System, allowing TDs and Developers to integrate DCC tools (Maya, Nuke, Blender) frictionlessly.

## Quick Start for Developers (Person B & C)

OmniPipe uses a **Vendorized Architecture**. This means 100% of the dependencies (like the CLI framework and Kitsu API) are pre-packaged in the `omnipipe/vendor/` folder. 

There are zero installations required.

1. Clone the repository:
   ```bash
   git clone https://github.com/kamal-suryavanshi/OmniPipe.git
   cd OmniPipe
   ```
2. Test the setup instantly using standard Python:
   ```bash
   python -m omnipipe --help
   ```

To explore the pipeline further, check out the **[CLI Cheatsheet](cheatsheet.md)**.
