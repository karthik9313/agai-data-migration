from autogen import AssistantAgent, UserProxyAgent, ConversableAgent
from autogen_migration.core.utils import get_monitoring_client, get_sql_admin_client, get_gcp_credentials, get_cloud_sql_metrics
from autogen_migration.config.settings import Config
import logging

logger = logging.getLogger(__name__)

class PerformanceOptimizationAgent(ConversableAgent):
    def __init__(self, name, llm_config, **kwargs):
        super().__init__(name, llm_config=llm_config, **kwargs)
        self.register_function(
            function_map={
                "analyze_performance_metrics": self._analyze_performance_metrics,
                "recommend_optimizations": self._recommend_optimizations,
                "apply_instance_scaling": self._apply_instance_scaling,
                # Add functions for query insights analysis, index suggestions etc.
            }
        )
        self.gcp_credentials = get_gcp_credentials(Config.GCP_SERVICE_ACCOUNT_KEY_PATH)
        self.monitoring_client = get_monitoring_client(self.gcp_credentials)
        self.sql_client = get_sql_admin_client(self.gcp_credentials)

    def _analyze_performance_metrics(self, project_id, instance_id):
        logger.info(f"Analyzing performance metrics for Cloud SQL instance {instance_id}...")
        cpu_util = get_cloud_sql_metrics(project_id, instance_id, "cloudsql.googleapis.com/database/cpu/utilization", days=1, credentials=self.gcp_credentials)
        memory_util = get_cloud_sql_metrics(project_id, instance_id, "cloudsql.googleapis.com/database/memory/utilization", days=1, credentials=self.gcp_credentials)

        avg_cpu = sum([m['value'] for m in cpu_util]) / len(cpu_util) if cpu_util else 0
        avg_memory = sum([m['value'] for m in memory_util]) / len(memory_util) if memory_util else 0

        report = {
            "avg_cpu_utilization": f"{avg_cpu*100:.2f}%",
            "avg_memory_utilization": f"{avg_memory*100:.2f}%",
            # Add more metrics like IOPS, connections etc.
        }
        logger.info(f"Performance metrics report for {instance_id}: {report}")
        return {"status": "success", "report": report}

    def _recommend_optimizations(self, performance_report):
        logger.info("Generating optimization recommendations based on performance report...")
        recommendations =
        # Use LLM for more sophisticated recommendations based on the report
        # Example: self.llm_client.generate(prompt=f"Given this performance report: {performance_report}, suggest Cloud SQL optimizations.")

        if float(performance_report["avg_cpu_utilization"].strip('%')) > 70:
            recommendations.append("Consider increasing vCPUs or optimizing queries.")
        if float(performance_report["avg_memory_utilization"].strip('%')) > 80:
            recommendations.append("Consider increasing memory or optimizing buffer pool size.")

        if not recommendations:
            recommendations.append("Current performance looks good, no immediate optimizations needed.")

        logger.info(f"Recommendations: {recommendations}")
        return {"status": "success", "recommendations": recommendations}

    def _apply_instance_scaling(self, project_id, instance_id, new_cpu, new_memory_gb):
        logger.info(f"Scaling Cloud SQL instance {instance_id} to {new_cpu} vCPUs and {new_memory_gb} GB memory...")
        instance_body = {
            "settings": {
                "tier": f"db-n1-standard-{new_cpu}", # Assuming n1-standard family
                "memory_limit_gb": new_memory_gb
            }
        }
        operation = self.sql_client.instances.patch(project=project_id, instance=instance_id, body=instance_body)
        operation.wait()
        logger.info(f"Cloud SQL instance {instance_id} scaled successfully.")
        return {"status": "success", "message": f"Instance scaled to {new_cpu} vCPUs, {new_memory_gb} GB."}

# Example usage in main.py or orchestrator.py
# perf_agent = PerformanceOptimizationAgent(name="PerformanceOptimizationAgent", llm_config=Config.LLM_CONFIG)
# perf_agent.send(
#     "Analyze Cloud SQL performance and suggest optimizations.",
#     recipient=user_proxy_agent
# )
