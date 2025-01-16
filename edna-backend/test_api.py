import asyncio
import aiohttp
import os
from pathlib import Path

class EDNAApiTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_data_path = Path("edna-projects/user_1234_testproject_20250115/raw_data")
        
    async def test_create_user(self):
        """Test user creation endpoint"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/users/",
                json={"name": "test_user"}
            ) as response:
                print(f"Create user status: {response.status}")
                user_data = await response.json()
                print(f"User created: {user_data}")
                return user_data['id']

    async def test_create_project(self, user_id: int):
        """Test project creation endpoint"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/projects/{user_id}",
                params={"project_name": "test_project"}
            ) as response:
                print(f"Create project status: {response.status}")
                project_data = await response.json()
                print(f"Project created: {project_data}")
                return project_data['id']

    async def test_upload_files(self, project_id: int):
        """Test file upload endpoint"""
        files = {
            'otu_table': open(self.test_data_path / 'otu_table.txt', 'rb'),
            'metadata': open(self.test_data_path / 'metadata.txt', 'rb'),
            'sequences': open(self.test_data_path / 'sequences.fasta', 'rb'),
            'tax_table': open(self.test_data_path / 'tax_table.txt', 'rb'),
            'taxa_metadata': open(self.test_data_path / 'taxa_metadata.txt', 'rb')
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                # Create FormData object for file upload
                data = aiohttp.FormData()
                for key, file in files.items():
                    data.add_field(key, file)
                
                async with session.post(
                    f"{self.base_url}/projects/{project_id}/upload",
                    data=data
                ) as response:
                    print(f"Upload files status: {response.status}")
                    result = await response.json()
                    print(f"Upload result: {result}")
                    return result
            finally:
                # Close all opened files
                for file in files.values():
                    file.close()

    async def run_tests(self):
        """Run all tests in sequence"""
        try:
            # Create user
            user_id = await self.test_create_user()
            if not user_id:
                print("Failed to create user")
                return
            
            # Create project
            project_id = await self.test_create_project(user_id)
            if not project_id:
                print("Failed to create project")
                return
            
            # Upload files
            upload_result = await self.test_upload_files(project_id)
            if not upload_result:
                print("Failed to upload files")
                return
            
            print("\nAll tests completed successfully!")
            
        except Exception as e:
            print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    # Create tester instance
    tester = EDNAApiTester()
    
    # Run tests
    asyncio.run(tester.run_tests())