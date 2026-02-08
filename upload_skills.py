import subprocess
import sys
import os
from pathlib import Path

def main():
    """
    Utility script to upload skills to Modal Volume.
    Wraps the 'modal volume put' CLI command.
    """
    print("🚀 Starting skills upload to Modal Volume 'ai-skills'...")

    # Define paths
    project_root = Path(__file__).parent
    skills_dir = project_root / "skills"

    if not skills_dir.exists():
        print(f"❌ Error: Skills directory not found at {skills_dir}")
        sys.exit(1)

    # Construct the command
    # modal volume put <volume_name> <local_path> <remote_path>
    # We upload the whole directory contents to the root of the volume
    # Changed volume name to 'ai-skills'
    cmd = ["modal", "volume", "put", "-f", "ai-skills", str(skills_dir), "/"]

    print(f"📦 Executing: {' '.join(cmd)}")
    
    try:
        # Run the command
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print(result.stdout)
        print("\n✨ Success! Skills uploaded.")
        print("📋 Verify with: modal volume ls ai-skills")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error uploading skills:")
        print(e.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("\n❌ Error: 'modal' command not found. Please install it with 'pip install modal'.")
        sys.exit(1)

if __name__ == "__main__":
    main()