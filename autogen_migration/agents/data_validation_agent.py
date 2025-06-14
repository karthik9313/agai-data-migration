from autogen import AssistantAgent, UserProxyAgent, ConversableAgent
from autogen_migration.core.utils import get_mysql_connection
from autogen_migration.config.settings import Config
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class DataValidationAgent(ConversableAgent):
    def __init__(self, name, llm_config, **kwargs):
        super().__init__(name, llm_config=llm_config, **kwargs)
        self.register_function(
            function_map={
                "compare_row_counts": self._compare_row_counts,
                "compare_checksums": self._compare_checksums,
                "sample_data_comparison": self._sample_data_comparison,
            }
        )

    def _get_db_data(self, host, port, user, password, db_name, table_name):
        conn = get_mysql_connection(host, port, user, password, db_name)
        try:
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
            return df
        finally:
            conn.close()

    def _compare_row_counts(self, legacy_db_config, cloud_sql_config, table_name="employees"):
        logger.info(f"Comparing row counts for table {table_name}...")
        legacy_conn = get_mysql_connection(**legacy_db_config)
        cloud_sql_conn = get_mysql_connection(**cloud_sql_config)
        try:
            with legacy_conn.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                legacy_count = cursor.fetchone()
            with cloud_sql_conn.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                cloud_sql_count = cursor.fetchone()

            if legacy_count == cloud_sql_count:
                logger.info(f"Row counts match for {table_name}: {legacy_count}")
                return {"status": "success", "match": True, "count": legacy_count}
            else:
                logger.warning(f"Row counts mismatch for {table_name}: Legacy={legacy_count}, Cloud SQL={cloud_sql_count}")
                return {"status": "failure", "match": False, "legacy_count": legacy_count, "cloud_sql_count": cloud_sql_count}
        finally:
            legacy_conn.close()
            cloud_sql_conn.close()

    def _compare_checksums(self, legacy_db_config, cloud_sql_config, table_name="employees"):
        logger.info(f"Comparing checksums for table {table_name}...")
        # Note: CHECKSUM TABLE can be slow for large tables. Consider sampling or other methods.
        legacy_conn = get_mysql_connection(**legacy_db_config)
        cloud_sql_conn = get_mysql_connection(**cloud_sql_config)
        try:
            with legacy_conn.cursor() as cursor:
                cursor.execute(f"CHECKSUM TABLE {table_name}")
                legacy_checksum = cursor.fetchone()
            with cloud_sql_conn.cursor() as cursor:
                cursor.execute(f"CHECKSUM TABLE {table_name}")
                cloud_sql_checksum = cursor.fetchone()

            if legacy_checksum == cloud_sql_checksum:
                logger.info(f"Checksums match for {table_name}: {legacy_checksum}")
                return {"status": "success", "match": True, "checksum": legacy_checksum}
            else:
                logger.warning(f"Checksums mismatch for {table_name}: Legacy={legacy_checksum}, Cloud SQL={cloud_sql_checksum}")
                return {"status": "failure", "match": False, "legacy_checksum": legacy_checksum, "cloud_sql_checksum": cloud_sql_checksum}
        finally:
            legacy_conn.close()
            cloud_sql_conn.close()

    def _sample_data_comparison(self, legacy_db_config, cloud_sql_config, table_name="employees", sample_size=100):
        logger.info(f"Performing sample data comparison for table {table_name}...")
        legacy_df = self._get_db_data(**legacy_db_config, table_name=table_name).sample(n=min(sample_size, len(self._get_db_data(**legacy_db_config, table_name=table_name))))
        cloud_sql_df = self._get_db_data(**cloud_sql_config, table_name=table_name).sample(n=min(sample_size, len(self._get_db_data(**cloud_sql_config, table_name=table_name))))

        # For simplicity, convert to dicts and compare. For real-world, use deep comparison.
        legacy_records = legacy_df.to_dict(orient='records')
        cloud_sql_records = cloud_sql_df.to_dict(orient='records')

        mismatched_records = [rec for rec in legacy_records if rec not in cloud_sql_records]
        if not mismatched_records:
            logger.info(f"Sample data matches for {table_name}.")
            return {"status": "success", "match": True}
        else:
            logger.warning(f"Sample data mismatch found for {table_name}. Mismatched records: {mismatched_records[:5]}")
            return {"status": "failure", "match": False, "mismatched_records_count": len(mismatched_records)}

# Example usage in main.py or orchestrator.py
# validation_agent = DataValidationAgent(name="DataValidationAgent", llm_config=Config.LLM_CONFIG)
# validation_agent.send(
#     "Compare data between legacy and Cloud SQL for employees table.",
#     recipient=user_proxy_agent
# )
