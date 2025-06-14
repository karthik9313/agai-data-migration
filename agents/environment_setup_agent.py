from autogen import AssistantAgent, UserProxyAgent, ConversableAgent
from autogen_migration.core.utils import get_sql_admin_client, get_storage_client, get_gcp_credentials
from autogen_migration.config.settings import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnvironmentSetupAgent(ConversableAgent):
    def __init__(self, name, llm_config, **kwargs):
        super().__init__(name, llm_config=llm_config, **kwargs)
        self.register_function(
            function_map={
                "create_cloud_sql_instance": self._create_cloud_sql_instance,
                "create_gcs_bucket": self._create_gcs_bucket,
                # Add functions for VPC peering, IAM setup etc.
            }
        )
        self.gcp_credentials = get_gcp_credentials(Config.GCP_SERVICE_ACCOUNT_KEY_PATH)
        self.sql_client = get_sql_admin_client(self.gcp_credentials)
        self.storage_client = get_storage_client(self.gcp_credentials)

    def _create_cloud_sql_instance(self, project_id, instance_id, region, machine_type, storage_gb, root_password, db_version="MYSQL_8_0"):
        logger.info(f"Creating Cloud SQL instance {instance_id} in {region}...")
        instance_body = {
            "database_version": db_version,
            "settings": {
                "tier": machine_type,
                "data_disk_size_gb": storage_gb,
                "ip_configuration": {
                    "ipv4_enabled": False, # Prefer private IP
                    "private_network": f"projects/{project_id}/global/networks/{Config.VPC_NETWORK_NAME}"
                },
                "backup_configuration": {"enabled": True, "binary_log_enabled": True},
                "location_preference": {"zone": f"{region}-a"}, # Example zone
                "database_flags": [{"name": "innodb_buffer_pool_size", "value": "5368709120"}], # Example flag
            },
            "root_password": root_password,
        }
        operation = self.sql_client.instances.insert(project=project_id, body=instance_body)
        operation.wait()
        logger.info(f"Cloud SQL instance {instance_id} created successfully.")
        return {"status": "success", "instance_id": instance_id}

    def _create_gcs_bucket(self, project_id, bucket_name, region):
        logger.info(f"Creating GCS bucket {bucket_name} in {region}...")
        bucket = self.storage_client.bucket(bucket_name)
        if not bucket.exists():
            bucket.create(location=region, project=project_id)
            logger.info(f"Bucket {bucket_name} created.")
        else:
            logger.info(f"Bucket {bucket_name} already exists.")
        return {"status": "success", "bucket_name": bucket_name}

# Example usage in main.py or orchestrator.py
# env_agent = EnvironmentSetupAgent(name="EnvironmentSetupAgent", llm_config=Config.LLM_CONFIG)
# env_agent.send(
#     "Create a Cloud SQL instance and a GCS bucket.",
#     recipient=user_proxy_agent # Or direct call from orchestrator
# )
