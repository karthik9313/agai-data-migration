import pymysql
from google.cloud import sql_admin_v1, storage, monitoring_v3, logging_v2
from google.oauth2 import service_account
from google.protobuf.timestamp_pb2 import Timestamp
import datetime

def get_mysql_connection(host, port, user, password, db):
    """Establishes a connection to a MySQL database."""
    return pymysql.connect(host=host, port=int(port), user=user, password=password, database=db)

def get_gcp_credentials(key_path):
    """Loads GCP service account credentials."""
    return service_account.Credentials.from_service_account_file(key_path)

def get_sql_admin_client(credentials):
    """Returns a Cloud SQL Admin API client."""
    return sql_admin_v1.SqlAdminServiceClient(credentials=credentials)

def get_storage_client(credentials):
    """Returns a Cloud Storage client."""
    return storage.Client(credentials=credentials)

def get_monitoring_client(credentials):
    """Returns a Cloud Monitoring client."""
    return monitoring_v3.MetricServiceClient(credentials=credentials)

def get_logging_client(credentials):
    """Returns a Cloud Logging client."""
    return logging_v2.LoggingServiceV2Client(credentials=credentials)

def export_mysql_schema(host, port, user, password, db_name, output_file):
    """Exports MySQL schema using mysqldump."""
    cmd = f"mysqldump -h {host} -P {port} -u {user} -p'{password}' --no-data {db_name} > {output_file}"
    os.system(cmd)
    print(f"Schema exported to {output_file}")

def export_mysql_data(host, port, user, password, db_name, output_file):
    """Exports MySQL data using mysqldump."""
    cmd = f"mysqldump -h {host} -P {port} -u {user} -p'{password}' --single-transaction --set-gtid-purged=OFF {db_name} > {output_file}"
    os.system(cmd)
    print(f"Data exported to {output_file}")

def import_mysql_dump(host, port, user, password, db_name, input_file):
    """Imports MySQL dump into a database."""
    cmd = f"mysql -h {host} -P {port} -u {user} -p'{password}' {db_name} < {input_file}"
    os.system(cmd)
    print(f"Data imported from {input_file}")

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name, credentials):
    """Uploads a file to Google Cloud Storage."""
    storage_client = get_storage_client(credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to gs://{bucket_name}/{destination_blob_name}")

def download_from_gcs(bucket_name, source_blob_name, destination_file_name, credentials):
    """Downloads a file from Google Cloud Storage."""
    storage_client = get_storage_client(credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(f"File gs://{bucket_name}/{source_blob_name} downloaded to {destination_file_name}")

def get_cloud_sql_metrics(project_id, instance_id, metric_type, days=7, credentials=None):
    """Fetches Cloud SQL metrics from Cloud Monitoring."""
    client = get_monitoring_client(credentials)
    project_name = f"projects/{project_id}"
    interval = monitoring_v3.TimeInterval(
        end_time=Timestamp(seconds=int(datetime.datetime.now().timestamp())),
        start_time=Timestamp(seconds=int((datetime.datetime.now() - datetime.timedelta(days=days)).timestamp())),
    )
    query = f'metric.type = "{metric_type}" AND resource.type = "cloudsql_database" AND resource.labels.database_id = "{instance_id}"'
    results = client.list_time_series(
        name=project_name,
        filter=query,
        interval=interval,
        view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
    )
    data =
    for series in results:
        for point in series.points:
            data.append({
                "timestamp": point.interval.end_time.seconds,
                "value": point.value.double_value if point.value.value_type == monitoring_v3.TypedValue.ValueType.DOUBLE else point.value.int64_value
            })
    return data

def get_cloud_sql_logs(project_id, instance_id, log_filter, hours=1, credentials=None):
    """Fetches Cloud SQL logs from Cloud Logging."""
    client = get_logging_client(credentials)
    resource_names = [f"projects/{project_id}"]
    now = datetime.datetime.utcnow()
    start_time = (now - datetime.timedelta(hours=hours)).isoformat("T") + "Z"
    end_time = now.isoformat("T") + "Z"
    filter_string = f'resource.type="cloudsql_database" AND resource.labels.database_id="{instance_id}" AND timestamp>="{start_time}" AND timestamp<="{end_time}" {log_filter}'
    entries = client.list_log_entries(resource_names=resource_names, filter=filter_string)
    logs =
    for entry in entries:
        logs.append(entry.json_payload.copy() if entry.json_payload else entry.text_payload)
    return logs
