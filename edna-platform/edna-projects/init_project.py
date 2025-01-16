import os
import shutil
from datetime import datetime

def create_project(user_id, project_name):
    # Create sanitized project folder name
    timestamp = datetime.now().strftime("%Y%m%d")
    project_folder = f"{user_id}_{project_name}_{timestamp}"
    
    # Copy template structure
    project_path = os.path.join(".", project_folder)
    shutil.copytree("project_template", project_path)
    
    print(f"Created project: {project_folder}")
    print("Required files:")
    print("1. raw_data/otu_table.txt")
    print("2. raw_data/metadata.txt")
    print("3. raw_data/sequences.fasta")
    print("4. raw_data/tax_table.txt")
    print("5. raw_data/taxa_metadata.txt")
    
    return project_path

if __name__ == "__main__":
    user_id = input("Enter user ID: ")
    project_name = input("Enter project name: ")
    project_path = create_project(user_id, project_name)
