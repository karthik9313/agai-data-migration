from autogen import AssistantAgent, UserProxyAgent, ConversableAgent
from autogen_migration.core.utils import export_mysql_schema, import_mysql_dump, get_mysql_connection
from autogen_migration.config.settings import Config
import logging

logger = logging.getLogger(__name__)

class SchemaConversionAgent(ConversableAgent):
    def __init__(self, name, llm_config, **kwargs):
        super().__init__(name, llm_config=llm_config, **kwargs)
        self.register_function(
            function_map={
                "export_legacy_schema": self._export_legacy_schema,
                "analyze_and_convert_schema": self._analyze_and_convert_schema,
                "apply_cloud_sql_schema": self._apply_cloud_sql_schema,
            }
        )

    def _export_legacy_schema(self, host, port, user, password, db_name, output_file="data/employees_schema.sql"):
        logger.info(f"Exporting schema from legacy MySQL {db_name}...")
        export_mysql_schema(host, port, user, password, db_name, output_file)
        return {"status": "success", "schema_file": output_file}

    def _analyze_and_convert_schema(self, schema_file_path):
        logger.info(f"Analyzing and converting schema from {schema_file_path}...")
        with open(schema_file_path, 'r') as f:
            schema_content = f.read()

        # This is where LLM interaction would happen for complex conversions.
        # For this example, we'll assume direct compatibility or simple adjustments.
        # In a real scenario, the LLM would be prompted with schema_content
        # and asked to provide a Cloud SQL compatible DDL.
        # Example: self.llm_client.generate(prompt=f"Convert this MySQL schema to Cloud SQL compatible DDL:\n{schema_content}")

        converted_schema = schema_content.replace("DEFINER=`root`@`localhost`", "SQL SECURITY INVOKER") # Example conversion
        output_converted_file = "data/employees_schema_cloudsql.sql"
        with open(output_converted_file, 'w') as f:
            f.write(converted_schema)
        logger.info(f"Schema converted and saved to {output_converted_file}")
        return {"status": "success", "converted_schema_file": output_converted_file}

    def _apply_cloud_sql_schema(self, host, port, user, password, db_name, schema_file_path):
        logger.info(f"Applying schema to Cloud SQL {db_name} from {schema_file_path}...")
        import_mysql_dump(host, port, user, password, db_name, schema_file_path)
        return {"status": "success", "message": "Schema applied to Cloud SQL."}

# Example usage in main.py or orchestrator.py
# schema_agent = SchemaConversionAgent(name="SchemaConversionAgent", llm_config=Config.LLM_CONFIG)
# schema_agent.send(
#     "Export legacy schema, convert it, and apply to Cloud SQL.",
#     recipient=user_proxy_agent
# )
