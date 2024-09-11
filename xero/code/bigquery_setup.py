from google.cloud import bigquery
from config import CONFIG, ENDPOINTS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_external_tables():
    client = bigquery.Client(project=CONFIG['PROJECT_ID'])
    dataset_id = f"{CONFIG['PROJECT_ID']}.{CONFIG['CLIENT_NAME']}_ingestion"

    for endpoint, url in ENDPOINTS.items():
        table_id = f"{dataset_id}.xero_{endpoint}"
        
        external_config = bigquery.ExternalConfig("NEWLINE_DELIMITED_JSON")
        external_config.source_uris = [f"gs://{CONFIG['BUCKET_NAME']}/{endpoint}.json"]
        external_config.autodetect = True
        external_config.schema = [
            bigquery.SchemaField("ingestion_time", "TIMESTAMP", mode="REQUIRED"),
        ]
        external_config.hive_partitioning_mode = "CUSTOM"
        external_config.hive_partitioning_options = bigquery.HivePartitioningOptions(
            mode="CUSTOM",
            source_uri_prefix=f"gs://{CONFIG['BUCKET_NAME']}/",
            fields=["ingestion_time"],
        )

        table = bigquery.Table(table_id)
        table.external_data_configuration = external_config

        try:
            client.delete_table(table_id, not_found_ok=True)
            client.create_table(table)
            logger.info(f"Created external table {table_id}")
        except Exception as e:
            logger.error(f"Error creating table for {endpoint}: {str(e)}")

if __name__ == "__main__":
    create_external_tables()