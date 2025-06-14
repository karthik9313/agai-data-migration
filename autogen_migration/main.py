from autogen_migration.core.orchestrator import MigrationOrchestrator
from autogen_migration.config.settings import Config
import os

if __name__ == "__main__":
    # Ensure GCP_PROJECT_ID and GCP_SERVICE_ACCOUNT_KEY_PATH are set as environment variables
    # For local testing, you might hardcode them in settings.py or load from.env
    os.environ = Config.PROJECT_ID
    os.environ = Config.GCP_SERVICE_ACCOUNT_KEY_PATH
    # Ensure secrets are set in GCP Secret Manager or mocked for local dev

    orchestrator = MigrationOrchestrator()
    orchestrator.run_migration()
