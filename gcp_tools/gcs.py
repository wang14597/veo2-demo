import datetime
import os
from concurrent.futures import ThreadPoolExecutor

from google.cloud import storage
from google.cloud.storage import Blob, Bucket
from google.oauth2.service_account import Credentials

from log_tools.log import logger


class GCS:
    def __init__(self, service_account):
        service_account_credentials = Credentials.from_service_account_file(service_account)
        self.storage_client = storage.Client(credentials=service_account_credentials)

    def get_blob(self, bucket_name, destination_blob_name) -> Blob:
        bucket: Bucket = self.storage_client.bucket(bucket_name)
        return bucket.blob(destination_blob_name)

    def upload_stream(self, bucket_name, destination_blob_name, iter):
        blob: Blob = self.get_blob(bucket_name, destination_blob_name)
        with blob.open('wb', timeout=60000 * 60) as f:
            for chunk in iter:
                f.write(chunk)

    def upload(self, bucket_name, destination_blob_name, file_obj):
        self.get_blob(bucket_name, destination_blob_name).upload_from_string(file_obj)

    def upload_from_filename(self, bucket_name, destination_blob_name, local_file_path):
        logger.info(f"Uploading {local_file_path} to {destination_blob_name}")
        self.get_blob(bucket_name, destination_blob_name).upload_from_filename(local_file_path)

    def generate_signed_url(self, bucket_name, blob_name, expiration=30):
        blob = self.get_blob(bucket_name, blob_name)
        expiration = datetime.timedelta(minutes=expiration)
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="GET",
            response_disposition=f'attachment; filename="{blob_name.split("/")[-1]}"',
            response_type="video/mp4"  # 根据实际视频格式调整
        )
        print(signed_url)
        return signed_url

    def file_exists(self, bucket_name, destination_blob_name) -> bool:
        bucket: Bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.get_blob(destination_blob_name)
        return blob is not None

    def upload_folder(self, bucket_name, folder_path, file_prefix):
        gcs_file_path = []
        with ThreadPoolExecutor() as executor:
            futures = []
            for root, _, files in os.walk(folder_path):
                for file_name in files:
                    local_file_path = os.path.join(root, file_name)
                    gcs_blob_name = f"{file_prefix}/{file_name}"
                    gcs_file_path.append(f"gs://{bucket_name}/{gcs_blob_name}")
                    futures.append(
                        executor.submit(self.upload_from_filename, bucket_name, gcs_blob_name, local_file_path))
            for future in futures:
                future.result()
        return gcs_file_path

    def download_file(self, bucket_name, source_blob_name, destination_file_name):
        blob = self.get_blob(bucket_name, source_blob_name)
        blob.download_to_filename(destination_file_name)
        return destination_file_name

    def list_files(self, bucket_name):
        bucket = self.storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs()
        return [i.name for i in blobs]

