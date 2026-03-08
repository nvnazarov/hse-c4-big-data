#!/bin/bash
set -e
envsubst < /opt/airflow/config/airflow.cfg.template > /opt/airflow/config/airflow.cfg
exec /entrypoint "${@}"
