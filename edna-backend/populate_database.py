#!/usr/bin/env python3
import asyncio
import aiohttp
import argparse
from pathlib import Path
import json
import os

class DatabasePopulator:
    def __init__(self, api_url, user_name, project_name):
        self.api_url = api_url
        self.user_name = user_name
        self.project_name = project_name
        
        # Find edna-data directory by going up one level from edna-backend
        self.base_path = Path(os.path.dirname(os.path.abspath(__file__))).parent / "edna-data"
        self.data_path = self.base_path / "users" / user_name / project_name / "raw_data"
        
        print(f"Looking for data in: {self.data_path}")
        
        if not self.data_path.exists():
            raise ValueError(f"Data directory not found: {self.data_path}")
            
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def check_existing_user(self):
        """Check if user already exists"""
        try:
            async with self.session.get(f"{self.api_url}/users/") as response:
                if response.status != 200:
                    print(f"Error checking users. Status: {response.status}")
                    return None
                users = await response.json()
                return next((user for user in users if user["name"] == self.user_name), None)
        except Exception as e:
            print(f"Error checking existing user: {e}")
            return None

    async def check_existing_project(self, user_id):
        """Check if project already exists for user"""
        try:
            async with self.session.get(f"{self.api_url}/projects/{user_id}") as response:
                if response.status != 200:
                    print(f"Error checking projects. Status: {response.status}")
                    return None
                projects = await response.json()
                return next((proj for proj in projects if proj["name"] == self.project_name), None)
        except Exception as e:
            print(f"Error checking existing project: {e}")
            return None

    async def create_user(self):
        """Create a new user"""
        try:
            async with self.session.post(
                f"{self.api_url}/users/",
                json={"name": self.user_name}
            ) as response:
                if response.status == 200:
                    user_data = await response.json()
                    print(f"User created successfully: {user_data}")
                    return user_data.get('id')
                else:
                    print(f"Failed to create user. Status: {response.status}")
                    response_text = await response.text()
                    print(f"Response: {response_text}")
                    return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    async def create_project(self, user_id):
        """Create a new project"""
        try:
            async with self.session.post(
                f"{self.api_url}/projects/{user_id}",
                params={"project_name": self.project_name}
            ) as response:
                if response.status == 200:
                    project_data = await response.json()
                    print(f"Project created successfully: {project_data}")
                    return project_data.get('id')
                else:
                    print(f"Failed to create project. Status: {response.status}")
                    response_text = await response.text()
                    print(f"Response: {response_text}")
                    return None
        except Exception as e:
            print(f"Error creating project: {e}")
            return None

    async def validate_files(self):
        """Validate that all required files exist"""
        required_files = {
            'otu_table.txt': 'OTU abundance matrix',
            'metadata.txt': 'Sample metadata',
            'sequences.fasta': 'Reference sequences',
            'tax_table.txt': 'Taxonomic assignments',
            'taxa_metadata.txt': 'Species metadata'
        }

        missing_files = []
        for filename, description in required_files.items():
            file_path = self.data_path / filename
            if not file_path.exists():
                missing_files.append(f"{filename} ({description})")
            else:
                print(f"Found file: {filename}")

        if missing_files:
            print("Missing required files:")
            for file in missing_files:
                print(f"- {file}")
            return False
        return True

    async def upload_files(self, project_id: int, force: bool = False):
        """Upload project files"""
        try:
            data = aiohttp.FormData()
            files = {
                'otu_table': 'otu_table.txt',
                'metadata': 'metadata.txt',
                'sequences': 'sequences.fasta',
                'tax_table': 'tax_table.txt',
                'taxa_metadata': 'taxa_metadata.txt'
            }

            for field_name, filename in files.items():
                file_path = self.data_path / filename
                if not file_path.exists():
                    raise FileNotFoundError(f"Required file not found: {file_path}")
                    
                print(f"Adding file to upload: {filename}")
                data.add_field(
                    field_name,
                    open(file_path, 'rb'),
                    filename=filename
                )

            # Add the force parameter to the request
            params = {'force': 'true'} if force else {}
            
            async with self.session.post(
                f"{self.api_url}/projects/{project_id}/upload",
                data=data,
                params=params
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("Files uploaded successfully")
                    return result
                else:
                    print(f"Failed to upload files. Status: {response.status}")
                    response_text = await response.text()
                    print(f"Response: {response_text}")
                    return None
        except Exception as e:
            print(f"Error uploading files: {e}")
            return None

async def main():
    parser = argparse.ArgumentParser(description='Populate database with user and project data')
    parser.add_argument('--user', required=True, help='User name')
    parser.add_argument('--project', required=True, help='Project name')
    parser.add_argument('--api', default='https://dnair-backend-781984095938.us-central1.run.app',
                       help='API URL (default: production URL)')
    parser.add_argument('--force', action='store_true', 
                       help='Force update if project exists')
    args = parser.parse_args()

    print(f"\nInitializing database population for:")
    print(f"User: {args.user}")
    print(f"Project: {args.project}")
    print(f"API URL: {args.api}")
    print("----------------------------------------")

    try:
        async with DatabasePopulator(args.api, args.user, args.project) as populator:
            # Validate files first
            if not await populator.validate_files():
                print("Aborting due to missing files")
                return

            # Check existing user
            existing_user = await populator.check_existing_user()
            if existing_user:
                print(f"User '{args.user}' already exists (ID: {existing_user['id']})")
                user_id = existing_user['id']
            else:
                print(f"Creating new user '{args.user}'...")
                user_id = await populator.create_user()
                if not user_id:
                    print("Failed to create user")
                    return

            # Check existing project
            existing_project = await populator.check_existing_project(user_id)
            if existing_project and not args.force:
                print(f"Project '{args.project}' already exists. Use --force to update")
                return
            elif existing_project:
                print(f"Updating existing project '{args.project}' (ID: {existing_project['id']})...")
                project_id = existing_project['id']
            else:
                print(f"Creating new project '{args.project}'...")
                project_id = await populator.create_project(user_id)
                if not project_id:
                    print("Failed to create project")
                    return

            # Upload files
            print("\nUploading project files...")
            result = await populator.upload_files(project_id, force=args.force)
            if result:
                print("\nDatabase population completed successfully!")
            else:
                print("\nFailed to upload project files")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())