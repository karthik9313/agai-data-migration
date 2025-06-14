from autogen import AssistantAgent, UserProxyAgent, ConversableAgent
from autogen_migration.core.utils import get_gcp_credentials
from autogen_migration.config.settings import Config
from google.cloud import datamigration_v1
import logging
import time

logger = logging.getLogger(__name__)

class DataMigrationAgent(ConversableAgent):
    def __init__(self, name, llm_config, **kwargs):
        super().__init__(name, llm_config=llm_config, **kwargs)
        self.register_function(
            function_map={
                "create_dms_connection_profile": self._create_dms_connection_profile,
                "create_dms_migration_job": self._create_dms_migration_job,
                "start_dms_migration_job": self._start_dms_migration_job,
                "monitor_dms_job": self._monitor_dms_job,
            }
        )
        self.gcp_credentials = get_gcp_credentials(Config.GCP_SERVICE_ACCOUNT_KEY_PATH)
        self.dms_client = datamigration_v1.DataMigrationServiceClient(credentials=self.gcp_credentials)

    def _create_dms_connection_profile(self, project_id, region, profile_id, host, port, user, password):
        logger.info(f"Creating DMS connection profile {profile_id}...")
        parent = f"projects/{project_id}/locations/{region}"
        connection_profile = datamigration_v1.ConnectionProfile()
        connection_profile.display_name = profile_id
        connection_profile.mysql.host = host
        connection_profile.mysql.port = int(port)
        connection_profile.mysql.username = user
        connection_profile.mysql.password = password
        connection_profile.mysql.ssl_config.type_ = datamigration_v1.SslConfig.SslType.NONE # For simplicity, adjust for production

        operation = self.dms_client.create_connection_profile(
            parent=parent, connection_profile_id=profile_id, connection_profile=connection_profile
        )
        operation.result()
        logger.info(f"DMS connection profile {profile_id} created.")
        return {"status": "success", "profile_id": profile_id}

    def _create_dms_migration_job(self, project_id, region, job_id, source_profile_id, dest_instance_id, job_type="ONE_TIME"):
        logger.info(f"Creating DMS migration job {job_id} of type {job_type}...")
        parent = f"projects/{project_id}/locations/{region}"
        migration_job = datamigration_v1.MigrationJob()
        migration_job.display_name = job_id
        migration_job.type_ = datamigration_v1.MigrationJob.Type.ONE_TIME if job_type == "ONE_TIME" else datamigration_v1.MigrationJob.Type.CONTINUOUS
        migration_job.source.connection_profile = f"projects/{project_id}/locations/{region}/connectionProfiles/{source_profile_id}"
        migration_job.destination.cloud_sql.cloud_sql_instance = dest_instance_id
        migration_job.destination.cloud_sql.database_version = "MYSQL_8_0" # Or appropriate version
        migration_job.destination.cloud_sql.private_ip = True # Assuming private IP setup

        operation = self.dms_client.create_migration_job(
            parent=parent, migration_job_id=job_id, migration_job=migration_job
        )
        operation.result()
        logger.info(f"DMS migration job {job_id} created.")
        return {"status": "success", "job_id": job_id}

    def _start_dms_migration_job(self, project_id, region, job_id):
        logger.info(f"Starting DMS migration job {job_id}...")
        name = f"projects/{project_id}/locations/{region}/migrationJobs/{job_id}"
        operation = self.dms_client.start_migration_job(name=name)
        operation.result()
        logger.info(f"DMS migration job {job_id} started.")
        return {"status": "success", "job_id": job_id}

    def _monitor_dms_job(self, project_id, region, job_id):
        logger.info(f"Monitoring DMS migration job {job_id}...")
        name = f"projects/{project_id}/locations/{region}/migrationJobs/{job_id}"
        job = self.dms_client.get_migration_job(name=name)
        while job.state not in:
            logger.info(f"Job {job_id} current state: {job.state.name}. Waiting...")
            time.sleep(30) # Wait for 30 seconds
            job = self.dms_client.get_migration_job(name=name)
        logger.info(f"Job {job_id} finished with state: {job.state.name}")
        return {"status": job.state.name, "job_id": job_id}

# Example usage in main.py or orchestrator.py
# data_migration_agent = DataMigrationAgent(name="DataMigrationAgent", llm_config=Config.LLM_CONFIG)
# data_migration_agent.send(
#     "Create DMS connection profile and a one-time migration job for employees_db.",
#     recipient=user_proxy_agent
# )
