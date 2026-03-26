import os
import hmac
import hashlib
import argparse

# The administrator master key. This file is NEVER shipped to clients!
_SECRET_KEY = b"OMNI_SECURE_DEV_KEY_992_X_ALPHA"

def create_license(studio_name: str, output_path: str):
    """Generates a cryptographically signed omnipipe.lic file using the Master Key."""
    
    # Build mathematical signature
    signature = hmac.new(_SECRET_KEY, studio_name.encode('utf-8'), hashlib.sha256).hexdigest()
    
    # Securely write to disk
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"{studio_name}\n")
        f.write(f"{signature}\n")
        
    print(f"✅ Cryptographically Secure License mathematically generated for '{studio_name}' at {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Admin Security Tool: Generate OmniPipe License File")
    parser.add_argument("studio", type=str, help="Name of the exact internal Studio or Client")
    parser.add_argument("--out", type=str, default=os.path.join(os.path.expanduser("~"), "omnipipe.lic"), help="Output file physical path")
    args = parser.parse_args()
    
    create_license(args.studio, args.out)
