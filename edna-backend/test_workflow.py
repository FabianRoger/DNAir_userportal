import asyncio
import aiohttp
import os
from pathlib import Path

class EDNAWorkflowTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_data_path = Path("edna-projects/user_1234_testproject_20250115/raw_data")
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def test_health(self):
        """Test health check endpoint"""
        async with self.session.get(f"{self.base_url}/health") as response:
            print(f"\nHealth check status: {response.status}")
            print(await response.json())

    async def create_user(self):
        """Create a test user"""
        async with self.session.post(
            f"{self.base_url}/users/",
            json={"name": "test_user"}
        ) as response:
            print(f"\nCreate user status: {response.status}")
            user_data = await response.json()
            print(f"User created: {user_data}")
            return user_data.get('id')

    async def create_project(self, user_id: int):
        """Create a test project"""
        async with self.session.post(
            f"{self.base_url}/projects/{user_id}",
            params={"project_name": "test_project"}
        ) as response:
            print(f"\nCreate project status: {response.status}")
            project_data = await response.json()
            print(f"Project created: {project_data}")
            return project_data.get('id')

    async def upload_test_files(self, project_id: int):
        """Upload the test data files"""
        # Prepare the files
        data = aiohttp.FormData()
        files = {
            'otu_table': 'otu_table.txt',
            'metadata': 'metadata.txt',
            'sequences': 'sequences.fasta',
            'tax_table': 'tax_table.txt',
            'taxa_metadata': 'taxa_metadata.txt'
        }
        
        print("\nUploading files...")
        for field_name, filename in files.items():
            file_path = self.test_data_path / filename
            if not file_path.exists():
                print(f"Warning: File {filename} not found at {file_path}")
                continue
            
            data.add_field(
                field_name,
                open(file_path, 'rb'),
                filename=filename
            )

        async with self.session.post(
            f"{self.base_url}/projects/{project_id}/upload",
            data=data
        ) as response:
            print(f"Upload status: {response.status}")
            result = await response.json()
            print(f"Upload result: {result}")
            return result

async def main():
    async with EDNAWorkflowTester() as tester:
        print("Starting workflow test...")
        
        # Test health endpoint
        await tester.test_health()
        
        try:
            # Create user
            user_id = await tester.create_user()
            if not user_id:
                print("Failed to create user")
                return

            # Create project
            project_id = await tester.create_project(user_id)
            if not project_id:
                print("Failed to create project")
                return

            # Upload test files
            upload_result = await tester.upload_test_files(project_id)
            if not upload_result:
                print("Failed to upload files")
                return

            print("\nWorkflow test completed successfully!")
            
        except Exception as e:
            print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())