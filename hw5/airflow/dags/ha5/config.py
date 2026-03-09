MINIO_CONNECTION_ID = "minio"
MINIO_CSV_BUCKET = "bank"
MINIO_CSV_KEY_PREFIX = "csv"
MINIO_ICEBERG_BUCKET = "bank"
MINIO_ICEBERG_KEY_PREFIX = "iceberg"

SPARK_CONNECTION_ID = "spark"
SPARK_MASTER = "spark://spark-master:7070"
SPARK_CONF = {
    "spark.jars": (
        "/opt/spark/jars/iceberg-spark-runtime-3.5_2.12-1.4.3.jar,"
        "/opt/spark/jars/hadoop-aws-3.3.4.jar,"
        "/opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar"
    ),
    "spark.sql.csv.parser.columnPruning.enabled": "true",
    "spark.sql.legacy.timeParserPolicy": "LEGACY",
    "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    "spark.sql.catalog.bank": "org.apache.iceberg.spark.SparkCatalog",
    "spark.sql.catalog.bank.type": "hive",
    "spark.sql.catalog.bank.uri": "thrift://metastore:9083",
    "spark.sql.catalog.bank.warehouse": "s3a://bank/iceberg",
    "spark.sql.catalog.bank.debug": "true",
    "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
    "spark.hadoop.fs.s3a.endpoint": "http://minio:9000",
    "spark.hadoop.fs.s3a.access.key": "minio-user",
    "spark.hadoop.fs.s3a.secret.key": "minio-password",
    "spark.hadoop.fs.s3a.path.style.access": "true",
    "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
    "spark.hadoop.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
    "spark.hadoop.fs.s3a.endpoint.region": "us-east-1",
    "spark.hadoop.fs.s3a.signer.override.scheme": "http",
    # These configuration settings fix weird JVM bugs with Arrow.
    "spark.sql.shuffle.partitions": "1",
    "spark.sql.parquet.enableVectorizedReader": "false",
    "spark.sql.inMemoryColumnarStorage.enableVectorizedReader": "false",
    "spark.sql.iceberg.vectorization.enabled": "false",
}
ICEBERG_SCHEMA = "bank.iceberg"
