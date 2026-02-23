# Home Assignment No. 4

## Task

## Solution

This home assignment was done similarly to the official [tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/pipeline.html).

`docker-compose.yml` was downloaded using the following command:

```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'
```

Then, the necessary files should be created:

1. Airflow config at `/config` (otherwise, the `airflow-init` container will create default config, which is not following the assignment, e.g. it creates default DAGs and uses UTC time).
2. SSL certificates at `/ssl`.
3. DAG at `/dags`.

Then, Airflow can be started using:

```bash
make up
```

The UI can be accessed at `http://localhost:8080`. Log in with username and password set to `airflow`.

Then, a database connection should be registered inside the Airflow UI so it can be accessed inside the DAG.
