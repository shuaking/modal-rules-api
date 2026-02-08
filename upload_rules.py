import subprocess
import sys
import os
from pathlib import Path

def main():
    """
    Utility script to upload rules to Modal Volume.
    Wraps the 'modal volume put' CLI command.
    """
    print("🚀 Starting rules upload to Modal Volume 'ai-rules'...")

    # Define paths
    project_root = Path(__file__).parent
    rules_dir = project_root / "rules"

    if not rules_dir.exists():
        print(f"❌ Error: Rules directory not found at {rules_dir}")
        sys.exit(1)

    # Construct the command
    # modal volume put <volume_name> <local_path> <remote_path>
    # We upload the whole directory contents to the root of the volume
    cmd = ["modal", "volume", "put", "-f", "ai-rules", str(rules_dir), "/"]

    print(f"📦 Executing: {' '.join(cmd)}")
    
    try:
        # Run the command
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print(result.stdout)
        print("\n✨ Success! Rules uploaded.")
        print("📋 Verify with: modal volume ls ai-rules")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error uploading rules:")
        print(e.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("\n❌ Error: 'modal' command not found. Please install it with 'pip install modal'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
