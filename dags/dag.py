import os
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from src.database.database import (
    create_tables_if_not_exists,
    insert_into_covid_brazil_table,
    insert_into_covid_states_table,
)

DATABASE_CONNECTION_CONFIGS = {
    "host": "postgres-covid",
    "port": "5432",
    "db_name": "daily_covid",
    "user": "root",
    "password": "password",
}
YESTERDAY_DATE = str((datetime.today() - timedelta(days=1)))[0:10]


with DAG(
    dag_id="daily_update_covid_tables",
    start_date=datetime.now(),
    schedule_interval="0 6 * * *",
) as dag:
    create_tables_if_not_exists = PythonOperator(
        task_id="create_tables",
        python_callable=create_tables_if_not_exists,
        op_kwargs={
            "database_connection_configs": DATABASE_CONNECTION_CONFIGS,
        },
    )

    update_brazil_table = PythonOperator(
        task_id="update_brazil_table",
        python_callable=insert_into_covid_brazil_table,
        op_kwargs={
            "database_connection_configs": DATABASE_CONNECTION_CONFIGS,
            "start_date": YESTERDAY_DATE,
            "end_date": YESTERDAY_DATE,
        },
    )

    update_states_table = PythonOperator(
        task_id="update_states_table",
        python_callable=insert_into_covid_states_table,
        op_kwargs={
            "database_connection_configs": DATABASE_CONNECTION_CONFIGS,
            "start_date": YESTERDAY_DATE,
            "end_date": YESTERDAY_DATE,
        },
    )

    #! Organizes the dependency
    create_tables_if_not_exists >> [update_brazil_table, update_states_table]
