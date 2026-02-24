# mkdir -p $1
# cd $1
# openssl req -x509 -newkey rsa:4096 \
#     -keyout key.pem \
#     -out cert.pem \
#     -days 365 \
#     -nodes \
#     -subj "/C=RU/ST=Moscow/L=Moscow/O=Airflow/CN=localhost" 2> /dev/null
# chmod 600 key.pem
# chmod 644 cert.pem

# mkdir -p $1
# cd $1
# cat > san.cnf <<EOF
# [req]
# distinguished_name = req_distinguished_name
# x509_extensions = v3_req
# prompt = no

# [req_distinguished_name]
# C = RU
# ST = Moscow
# L = Moscow
# O = Airflow
# CN = localhost

# [v3_req]
# keyUsage = keyEncipherment, dataEncipherment
# extendedKeyUsage = serverAuth
# subjectAltName = @alt_names

# [alt_names]
# DNS.1 = localhost
# DNS.2 = airflow-webserver
# DNS.3 = airflow-apiserver
# DNS.4 = 127.0.0.1
# IP.1 = 127.0.0.1
# EOF
# openssl req -x509 -newkey rsa:4096 \
#     -keyout key.pem \
#     -out cert.pem \
#     -days 365 \
#     -nodes \
#     -config san.cnf \
#     -extensions v3_req 2>/dev/null
# chmod 600 key.pem
# chmod 644 cert.pem
# rm san.cnf

mkdir -p $1
cd $1
cat > san.cnf <<EOF
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
C = RU
ST = Moscow
L = Moscow
O = Airflow
CN = localhost

[v3_req]
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = airflow-webserver
DNS.3 = airflow-apiserver
DNS.4 = 127.0.0.1
IP.1 = 127.0.0.1
EOF
openssl req -x509 -newkey rsa:4096 \
    -keyout key.pem \
    -out cert.pem \
    -days 365 \
    -nodes \
    -config san.cnf \
    -extensions v3_req
chmod 600 key.pem
chmod 644 cert.pem
rm san.cnf