import os
from google.cloud import secretmanager

def get_secret(secret_id, project_id):
    """Access secrets from Google Cloud Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

class Config:
    PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-gcp-project-id")
    REGION = os.getenv("GCP_REGION", "us-central1")
    LEGACY_MYSQL_HOST = os.getenv("LEGACY_MYSQL_HOST", "your-legacy-mysql-ip")
    LEGACY_MYSQL_PORT = os.getenv("LEGACY_MYSQL_PORT", "3306")
    LEGACY_MYSQL_DB = os.getenv("LEGACY_MYSQL_DB", "legacy_employees_db")
    CLOUD_SQL_INSTANCE_ID = os.getenv("CLOUD_SQL_INSTANCE_ID", "cloud-sql-employees-instance")
    CLOUD_SQL_DB_NAME = os.getenv("CLOUD_SQL_DB_NAME", "employees_db")
    CLOUD_SQL_MACHINE_TYPE = os.getenv("CLOUD_SQL_MACHINE_TYPE", "db-n1-standard-2") # 2 vCPU, 7.5 GiB
    CLOUD_SQL_STORAGE_GB = int(os.getenv("CLOUD_SQL_STORAGE_GB", "20"))
    VPC_NETWORK_NAME = os.getenv("VPC_NETWORK_NAME", "default")

    # Retrieve sensitive credentials from Secret Manager
    LEGACY_MYSQL_USER = get_secret("legacy-mysql-user", PROJECT_ID)
    LEGACY_MYSQL_PASSWORD = get_secret("legacy-mysql-password", PROJECT_ID)
    CLOUD_SQL_ROOT_PASSWORD = get_secret("cloud-sql-root-password", PROJECT_ID)
    GCP_SERVICE_ACCOUNT_KEY_PATH = os.getenv("GCP_SERVICE_ACCOUNT_KEY_PATH", "/path/to/your/key.json")

    # LLM Configuration
    LLM_CONFIG = {
        "model": "gemini-1.5-pro", # Or another suitable model
        "api_key": get_secret("gemini-api-key", PROJECT_ID),
        # "base_url": "..." # If using a self-hosted LLM or specific endpoint
    }
