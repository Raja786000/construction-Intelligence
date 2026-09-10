import zipfile
import os
from pathlib import Path

def create_project_zip():
    # Base directory is project root
    base_dir = Path(__file__).resolve().parent.parent
    zip_output_path = base_dir / "construction_risk_platform.zip"
    
    # Also create zip in workspace root parent directory if applicable
    parent_zip_path = base_dir.parent / "construction_risk_platform.zip"

    print("=" * 65)
    print(" 📦 PACKAGING COMPLETE PROJECT ZIP DELIVERABLE")
    print("=" * 65)
    print(f"Source Folder: {base_dir}")

    # Exclude temporary cache / venv folders
    exclude_dirs = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", ".idea", ".vscode", "data"}
    exclude_files = {".DS_Store", "construction_risk_platform.zip"}

    for zip_target in [zip_output_path, parent_zip_path]:
        with zipfile.ZipFile(zip_target, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(base_dir):
                # Filter out excluded dirs in-place
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    if file in exclude_files or file.endswith('.pyc'):
                        continue
                    
                    file_path = Path(root) / file
                    # Relative path inside the zip file
                    arcname = file_path.relative_to(base_dir)
                    zipf.write(file_path, arcname)

        print(f"✅ Generated ZIP Archive: {zip_target}")
        print(f"   Size: {os.path.getsize(zip_target) / (1024*1024):.2f} MB")

    print("\nProject ZIP folder created successfully!")

if __name__ == "__main__":
    create_project_zip()
