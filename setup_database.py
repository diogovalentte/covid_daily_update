import os
import dags.src.database.database as database
from datetime import datetime, timedelta


DATABASE_CONNECTION_CONFIGS = {
    "host": "covid-database",
    "port": "5432",
    "db_name": "daily_covid",
    "user": "root",
    "password": "password",
}


#! Set up database
database.create_tables_if_not_exists(DATABASE_CONNECTION_CONFIGS)
database.insert_into_covid_brazil_table(
    DATABASE_CONNECTION_CONFIGS,
    # datetime(2020, 2, 26),
    datetime(2023, 2, 1),
    (datetime.today() - timedelta(days=1)),
)
database.insert_into_covid_states_table(
    DATABASE_CONNECTION_CONFIGS,
    # datetime(2020, 5, 19),
    datetime(2023, 2, 1),
    (datetime.today() - timedelta(days=1)),
)
