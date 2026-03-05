SPARK_CONNECTION_ID = "spark_conn"
SPARK_MASTER="spark://spark-master:7077"
SPARK_CONF = {
    "spark.jars.packages": (
        "org.apache.hadoop:hadoop-aws:3.3.4"
        ",com.amazonaws:aws-java-sdk-bundle:1.12.262"
        ",org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3"
    ),
    "spark.sql.csv.parser.columnPruning.enabled": "true",
    "spark.sql.legacy.timeParserPolicy": "LEGACY",
    "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    "spark.sql.catalog.bank": "org.apache.iceberg.spark.SparkCatalog",
    "spark.sql.catalog.bank.type": "hive",
    "spark.sql.catalog.bank.uri": "thrift://hive-metastore:9083",
    "spark.sql.catalog.bank.warehouse": "s3a://bank/warehouse",
    "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
    "spark.hadoop.fs.s3a.endpoint": "http://minio:9000",
    "spark.hadoop.fs.s3a.access.key": "minio-user",
    "spark.hadoop.fs.s3a.secret.key": "minio-password",
    "spark.hadoop.fs.s3a.path.style.access": "true",
    "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
    "spark.hadoop.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
    "spark.hadoop.fs.s3a.endpoint.region": "us-east-1",
    "spark.hadoop.fs.s3a.signer.override.scheme": "http",
    "spark.hadoop.fs.s3a.bucket.bank-csv-files.endpoint": "http://minio:9000",
}
