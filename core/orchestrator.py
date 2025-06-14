from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from autogen_migration.agents.environment_setup_agent import EnvironmentSetupAgent
from autogen_migration.agents.schema_conversion_agent import SchemaConversionAgent
from autogen_migration.agents.data_migration_agent import DataMigrationAgent
from autogen_migration.agents.data_validation_agent import DataValidationAgent
from autogen_migration.agents.anomaly_detection_agent import AnomalyDetectionAgent
from autogen_migration.agents.performance_optimization_agent import PerformanceOptimizationAgent
from autogen_migration.config.settings import Config
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MigrationOrchestrator:
    def __init__(self):
        self.user_proxy = UserProxyAgent(
            name="Admin",
            system_message="A human admin. Interact with the agents to ensure the migration is successful. Provide feedback and approve steps.",
            code_execution_config={"last_n_messages": 3, "work_dir": "temp_code"},
            human_input_mode="ALWAYS", # Or "TERMINATE" for full automation
        )

        self.env_agent = EnvironmentSetupAgent(name="EnvironmentSetupAgent", llm_config={"config_list": [{"model": Config.LLM_CONFIG["model"], "api_key": Config.LLM_CONFIG["api_key"]}]})
        self.schema_agent = SchemaConversionAgent(name="SchemaConversionAgent", llm_config={"config_list": [{"model": Config.LLM_CONFIG["model"], "api_key": Config.LLM_CONFIG["api_key"]}]})
        self.data_agent = DataMigrationAgent(name="DataMigrationAgent", llm_config={"config_list": [{"model": Config.LLM_CONFIG["model"], "api_key": Config.LLM_CONFIG["api_key"]}]})
        self.validation_agent = DataValidationAgent(name="DataValidationAgent", llm_config={"config_list": [{"model": Config.LLM_CONFIG["model"], "api_key": Config.LLM_CONFIG["api_key"]}]})
        self.anomaly_agent = AnomalyDetectionAgent(name="AnomalyDetectionAgent", llm_config={"config_list": [{"model": Config.LLM_CONFIG["model"], "api_key": Config.LLM_CONFIG["api_key"]}]})
        self.perf_agent = PerformanceOptimizationAgent(name="PerformanceOptimizationAgent", llm_config={"config_list": [{"model": Config.LLM_CONFIG["model"], "api_key": Config.LLM_CONFIG["api_key"]}]})

        self.groupchat = GroupChat(
            agents=[
                self.user_proxy,
                self.env_agent,
                self.schema_agent,
                self.data_agent,
                self.validation_agent,
                self.anomaly_agent,
                self.perf_agent,
            ],
            messages=,
            max_round=50,
            speaker_selection_method="auto",
            allow_repeat_speaker=False,
        )
        self.manager = GroupChatManager(groupchat=self.groupchat, llm_config={"config_list": [{"model": Config.LLM_CONFIG["model"], "api_key": Config.LLM_CONFIG["api_key"]}]})

    def run_migration(self):
        logger.info("Starting automated database migration process...")
        self.user_proxy.initiate_chat(
            self.manager,
            message=f"""
            Automate the migration of a legacy MySQL database '{Config.LEGACY_MYSQL_DB}'
            on host '{Config.LEGACY_MYSQL_HOST}' to GCP Cloud SQL for MySQL.
            The target Cloud SQL instance ID should be '{Config.CLOUD_SQL_INSTANCE_ID}'.
            The migration should include both schema and data for the 'employees' table.
            After migration, validate data integrity, monitor for anomalies, and suggest performance optimizations.
            Use the provided sample employee dataset for implementation.
            Ensure all GCP best practices are followed, especially regarding private IP and secure credential management.
            Proceed with a one-time migration first, then discuss how CDC would be implemented.
            """
        )
