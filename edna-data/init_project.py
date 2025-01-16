#!/usr/bin/env python3
import os
import shutil
import argparse
from pathlib import Path

def create_project_structure(user_name: str, project_name: str):
    """Create a new project directory structure."""
    # Base path in users directory
    base_path = Path("users") / user_name / project_name
    
    # Create directories
    directories = [
        base_path / "raw_data",
        base_path / "processed_data",
        base_path / "results"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create empty .gitkeep files to track empty directories
    for directory in directories[1:]:  # Skip raw_data as it will have files
        (directory / ".gitkeep").touch()
    
    # Copy file requirements
    shutil.copy("file_requirements.txt", base_path / "file_requirements.txt")
    
    print(f"\nProject structure created at: {base_path}")
    print("\nRequired files in raw_data/:")
    with open("file_requirements.txt", "r") as f:
        print(f.read())

def main():
    parser = argparse.ArgumentParser(description="Initialize new eDNA project structure")
    parser.add_argument("--user", required=True, help="User name")
    parser.add_argument("--project", required=True, help="Project name")
    
    args = parser.parse_args()
    create_project_structure(args.user, args.project)

if __name__ == "__main__":
    main()