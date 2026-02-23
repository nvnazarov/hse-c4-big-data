mkdir -p $1
cd $1
openssl req -x509 -newkey rsa:4096 \
    -keyout key.pem \
    -out cert.pem \
    -days 365 \
    -nodes \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=Airflow/CN=localhost" 2> /dev/null
chmod 600 key.pem
chmod 644 cert.pem
