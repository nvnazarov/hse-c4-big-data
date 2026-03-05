ARG HIVE_METASTORE__IMAGE__TAG=4.0.0

# Builds Hive Metastore with all necessary dependencies.
FROM apache/hive:${HIVE_METASTORE__IMAGE__TAG}

# Some Java packages are required for Hive Metastore
# to work properly with Minio and Iceberg.
USER root
ADD https://jdbc.postgresql.org/download/postgresql-42.7.5.jar /opt/hive/lib/postgresql-42.7.5.jar
RUN cp /opt/hive/lib/postgresql-42.7.5.jar /opt/hadoop/share/hadoop/common/lib/postgresql-42.7.5.jar \
    && cp /opt/hadoop/share/hadoop/tools/lib/hadoop-aws-3.3.6.jar /opt/hadoop/share/hadoop/common/lib/hadoop-aws-3.3.6.jar \
    && cp /opt/hadoop/share/hadoop/tools/lib/aws-java-sdk-bundle-1.12.367.jar /opt/hadoop/share/hadoop/common/lib/aws-java-sdk-bundle-1.12.367.jar \
    && cp /opt/hadoop/share/hadoop/tools/lib/wildfly-openssl-1.1.3.Final.jar /opt/hadoop/share/hadoop/common/lib/wildfly-openssl-1.1.3.Final.jar \
    && cp /opt/hadoop/share/hadoop/common/lib/hadoop-aws-3.3.6.jar /opt/hive/lib/hadoop-aws-3.3.6.jar \
    && cp /opt/hadoop/share/hadoop/common/lib/aws-java-sdk-bundle-1.12.367.jar /opt/hive/lib/aws-java-sdk-bundle-1.12.367.jar \
    && cp /opt/hadoop/share/hadoop/common/lib/wildfly-openssl-1.1.3.Final.jar /opt/hive/lib/wildfly-openssl-1.1.3.Final.jar

COPY core-site.xml /opt/hive/conf/core-site.xml
COPY core-site.xml /opt/hadoop/etc/hadoop/core-site.xml
