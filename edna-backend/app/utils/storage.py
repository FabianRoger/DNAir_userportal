# app/utils/storage.py

import os
from pathlib import Path
from google.cloud import storage
from fastapi import UploadFile
import logging

class StorageService:
    def __init__(self):
        # Add debug logging
        logging.basicConfig(level=logging.DEBUG)
        self.is_cloud = os.getenv('ENVIRONMENT') == 'cloud'
        bucket_name = os.getenv('BUCKET_NAME')
        
        logging.debug(f"Environment: {os.getenv('ENVIRONMENT')}")
        logging.debug(f"Bucket Name: {bucket_name}")
        logging.debug(f"Is Cloud: {self.is_cloud}")
        
        if self.is_cloud:
            try:
                if not bucket_name:
                    raise ValueError("BUCKET_NAME environment variable is not set")
                
                self.client = storage.Client()
                self.bucket = self.client.bucket(bucket_name)
                logging.debug(f"Successfully initialized bucket: {bucket_name}")
                
            except Exception as e:
                logging.error(f"Error initializing storage: {str(e)}")
                raise
        else:
            self.storage_dir = Path("local_storage")
            self.storage_dir.mkdir(exist_ok=True)
            logging.debug(f"Using local storage: {self.storage_dir}")

    async def upload_file(self, file: UploadFile, destination_path: str) -> str:
        """Upload file to either cloud storage or local filesystem"""
        if self.is_cloud:
            try:
                logging.debug(f"Attempting to upload {destination_path} to cloud storage")
                blob = self.bucket.blob(destination_path)
                content = await file.read()
                blob.upload_from_string(content)
                
                url = f"gs://{self.bucket.name}/{destination_path}"
                logging.debug(f"Successfully uploaded to {url}")
                return url
                
            except Exception as e:
                logging.error(f"Error uploading file: {str(e)}")
                raise
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
            try:
                logging.debug(f"Attempting to read {file_path} from cloud storage")
                blob = self.bucket.blob(file_path)
                return blob.download_as_string()
            except Exception as e:
                logging.error(f"Error reading file: {str(e)}")
                raise
        else:
            with open(self.storage_dir / file_path, 'rb') as f:
                return f.read()