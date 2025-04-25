import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
load_dotenv()
# #from config import STORAGE_CONNECTION_STRING
CONTAINER_NAME = "legal-documents-rania"


def upload_file_to_blob(local_path, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    try:
        container_client.create_container()
    except:
        pass
    blob_client = container_client.get_blob_client(blob_name)
    if blob_client.exists():
        print(f"{blob_name} already exists. Skipping upload.")
        return
    with open(local_path, "rb") as f:
        blob_client.upload_blob(f)
    print(f"Uploaded {blob_name} to Azure Blob Storage.")

