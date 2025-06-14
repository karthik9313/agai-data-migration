from autogen import AssistantAgent, UserProxyAgent, ConversableAgent
from autogen_migration.core.utils import get_monitoring_client, get_logging_client, get_gcp_credentials, get_cloud_sql_metrics, get_cloud_sql_logs
from autogen_migration.config.settings import Config
import logging
import json

logger = logging.getLogger(__name__)

class AnomalyDetectionAgent(ConversableAgent):
    def __init__(self, name, llm_config, **kwargs):
        super().__init__(name, llm_config=llm_config, **kwargs)
        self.register_function(
            function_map={
                "monitor_cloud_sql_health": self._monitor_cloud_sql_health,
                "analyze_logs_for_errors": self._analyze_logs_for_errors,
            }
        )
        self.gcp_credentials = get_gcp_credentials(Config.GCP_SERVICE_ACCOUNT_KEY_PATH)
        self.monitoring_client = get_monitoring_client(self.gcp_credentials)
        self.logging_client = get_logging_client(self.gcp_credentials)

    def _monitor_cloud_sql_health(self, project_id, instance_id):
        logger.info(f"Monitoring Cloud SQL instance {instance_id} for anomalies...")
        cpu_metrics = get_cloud_sql_metrics(project_id, instance_id, "cloudsql.googleapis.com/database/cpu/utilization", days=0.1, credentials=self.gcp_credentials)
        memory_metrics = get_cloud_sql_metrics(project_id, instance_id, "cloudsql.googleapis.com/database/memory/utilization", days=0.1, credentials=self.gcp_credentials)

        # Simple anomaly detection logic (can be enhanced with ML models or LLM)
        high_cpu_spikes = [m for m in cpu_metrics if m['value'] > 0.9] # >90% CPU usage [span_47](start_span)[span_47](end_span)
        high_memory_usage = [m for m in memory_metrics if m['value'] > 0.9] # >90% memory usage [span_48](start_span)[span_48](end_span)

        anomalies =
        if high_cpu_spikes:
            anomalies.append(f"High CPU utilization detected: {len(high_cpu_spikes)} spikes above 90%.")
        if high_memory_usage:
            anomalies.append(f"High memory utilization detected: {len(high_memory_usage)} instances above 90%.")

        if anomalies:
            logger.warning(f"Anomalies detected for {instance_id}: {'; '.join(anomalies)}")
            return {"status": "anomalies_detected", "details": anomalies}
        else:
            logger.info(f"No significant anomalies detected for {instance_id} based on health metrics.")
            return {"status": "no_anomalies"}

    def _analyze_logs_for_errors(self, project_id, instance_id):
        logger.info(f"Analyzing Cloud SQL logs for errors on {instance_id}...")
        error_logs = get_cloud_sql_logs(project_id, instance_id, 'severity=ERROR OR severity=CRITICAL', hours=1, credentials=self.gcp_credentials)

        if error_logs:
            logger.warning(f"Error logs found for {instance_id}. Sample: {json.dumps(error_logs)}")
            # LLM can be prompted to analyze log patterns for deeper understanding
            # response = self.llm_client.generate(prompt=f"Analyze these logs for root cause: {json.dumps(error_logs)}")
            return {"status": "errors_found", "count": len(error_logs), "sample_log": error_logs}
        else:
            logger.info(f"No error logs found for {instance_id} in the last hour.")
            return {"status": "no_errors"}

# Example usage in main.py or orchestrator.py
# anomaly_agent = AnomalyDetectionAgent(name="AnomalyDetectionAgent", llm_config=Config.LLM_CONFIG)
# anomaly_agent.send(
#     "Check Cloud SQL health and logs for errors.",
#     recipient=user_proxy_agent
# )
