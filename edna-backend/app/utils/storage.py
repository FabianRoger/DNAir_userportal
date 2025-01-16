# app/utils/storage.py
import os
from pathlib import Path
from google.cloud import storage
from fastapi import UploadFile

class StorageService:
    def __init__(self):
        self.is_cloud = os.getenv('ENVIRONMENT') == 'cloud'
        if self.is_cloud:
            self.client = storage.Client()
            self.bucket = self.client.bucket(os.getenv('BUCKET_NAME'))
        else:
            self.storage_dir = Path("local_storage")
            self.storage_dir.mkdir(exist_ok=True)

    async def upload_file(self, file: UploadFile, destination_path: str) -> str:
        """Upload file to either cloud storage or local filesystem"""
        if self.is_cloud:
            blob = self.bucket.blob(destination_path)
            content = await file.read()
            blob.upload_from_string(content)
            return destination_path
        else:
            save_path = self.storage_dir / destination_path
            save_path.parent.mkdir(parents=True, exist_ok=True)
            content = await file.read()
            with open(save_path, "wb") as f:
                f.write(content)
            return str(save_path)

    async def read_file(self, file_path: str, file_type: str = 'txt'):
        """Read file from either cloud storage or local filesystem"""
        if self.is_cloud:
            blob = self.bucket.blob(file_path)
            return blob.download_as_string()
        else:
            with open(self.storage_dir / file_path, 'rb') as f:
                return f.read()