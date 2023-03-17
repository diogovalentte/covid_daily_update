import logging
import requests
import datetime
import pandas as pd


logging.basicConfig(
    # encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s :: %(levelname)-8s :: %(name)s :: %(message)s",
)
logger = logging.getLogger("database")


def query_database(
    host, db_name, user, password, query: str, port: int = 5432, query_args=()
):
    """Execute a query that do not retrieve data on a PostgreSQL database.

    Args:
        host (str): Database hostname.
        db_name (str): Database name.
        user (str): Database username.
        password (str): User password.
        query (str): Query to execute in the database.
        port (int): Database Port. Default is 5432.
        query_args (tuple): Query arguments. Default is (), no arguments.
    """
    import psycopg2

    with psycopg2.connect(
        host=host, dbname=db_name, user=user, password=password, port=port
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, vars=query_args)

    return None


def create_tables_if_not_exists(database_connection_configs: dict):
    """Creates the "covid_states" and "covid_brazil" tables if not exist.

    Args:
      database_connection_configs (dict): The database connection configs.
    """
    sql = """
        CREATE TABLE IF NOT EXISTS covid_brazil (
            date DATE PRIMARY KEY,
            confirmed_accumulated INTEGER,
            confirmated_difference INTEGER,
            deaths_accumulated INTEGER,
            deaths_difference INTEGER,
            last_update TIMESTAMP
        );
    """
    logger.info(
        "create_tables_if_not_exists :: Creating table covid_brazil if not exists"
    )
    query_database(
        host=database_connection_configs["host"],
        db_name=database_connection_configs["db_name"],
        port=database_connection_configs["port"],
        user=database_connection_configs["user"],
        password=database_connection_configs["password"],
        query=sql,
    )

    logger.info(
        "create_tables_if_not_exists :: Creating table covid_states if not exists"
    )
    sql = """
        CREATE TABLE IF NOT EXISTS covid_states (
            state VARCHAR(100),
            date DATE,
            confirmed_accumulated INTEGER,
            confirmated_difference INTEGER,
            deaths_accumulated INTEGER,
            deaths_difference INTEGER,
            last_update TIMESTAMP
        );
    """
    query_database(
        host=database_connection_configs["host"],
        db_name=database_connection_configs["db_name"],
        port=database_connection_configs["port"],
        user=database_connection_configs["user"],
        password=database_connection_configs["password"],
        query=sql,
    )

    return None


def insert_into_covid_brazil_table(
    database_connection_configs: dict,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
):
    """Populates the "covid_brazil" table with daily Covid data of Brazil.

    Args:
      database_connection_configs (dict): The database connection configs.
      start_date (datetime.datetime): Start date to insert data in database.
      end_date (datetime.datetime): End date to insert data in database (included).

    Obs:
        start_date and end_date arguments can be the same to get data from one day.
    """
    API_URL = "http://covid-api.com/api/reports/total"
    date_list = pd.date_range(start=start_date, end=end_date).tolist()

    for date in date_list:
        date = str(date)[:10]
        query = {"date": date, "q": "Brazil", "region_name": "Brazil", "iso": "BRA"}
        response_json = requests.request("GET", API_URL, params=query).json()["data"]
        if len(response_json) > 0:
            logger.info(
                f"insert_into_covid_brazil_table :: Inserting data from date {date}"
            )

            confirmed = response_json["confirmed"]
            confirmed_diff = response_json["confirmed_diff"]
            deaths_diff = response_json["deaths_diff"]
            deaths = response_json["deaths"]
            last_update = response_json["last_update"]

            sql = """
                INSERT INTO
                    covid_brazil
                VALUES
                    (%s, %s, %s, %s, %s, %s);
            """
            query_database(
                host=database_connection_configs["host"],
                db_name=database_connection_configs["db_name"],
                port=database_connection_configs["port"],
                user=database_connection_configs["user"],
                password=database_connection_configs["password"],
                query=sql,
                query_args=(
                    date,
                    confirmed,
                    confirmed_diff,
                    deaths,
                    deaths_diff,
                    last_update,
                ),
            )
        else:
            logger.info(
                f"insert_into_covid_brazil_table :: Empty response from API for date: {date}"
            )

    return None


def insert_into_covid_states_table(
    database_connection_configs: dict,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
):
    """Populates the "covid_states" table with daily Covid data for each brazilian state.

    Args:
      database_connection_configs (dict): The database connection configs.
      start_date (datetime.datetime): Start date to insert data in database.
      end_date (datetime.datetime): End date to insert data in database (included).

    Obs:
        start_date and end_date arguments can be the same to get data from one day.
    """
    API_URL = "http://covid-api.com/api/reports"
    date_list = pd.date_range(start=start_date, end=end_date).tolist()

    for date in date_list:
        date = str(date)[:10]
        query = {"date": date, "q": "Brazil", "region_name": "Brazil", "iso": "BRA"}
        response_json = requests.request("GET", API_URL, params=query).json()["data"]
        if len(response_json) > 0:
            logger.info(
                f"insert_into_covid_states_table :: Inserting data from date {date}"
            )

            for state_data in response_json:
                if state_data["region"]["province"] != "":
                    state = state_data["region"]["province"]
                    confirmed = state_data["confirmed"]
                    confirmed_diff = state_data["confirmed_diff"]
                    deaths = state_data["deaths"]
                    deaths_diff = state_data["deaths_diff"]
                    last_update = state_data["last_update"]

                    sql = """
                        INSERT INTO
                            covid_states
                        VALUES
                            (%s, %s, %s, %s, %s, %s, %s);
                    """
                    query_database(
                        host=database_connection_configs["host"],
                        db_name=database_connection_configs["db_name"],
                        port=database_connection_configs["port"],
                        user=database_connection_configs["user"],
                        password=database_connection_configs["password"],
                        query=sql,
                        query_args=(
                            state,
                            date,
                            confirmed,
                            confirmed_diff,
                            deaths,
                            deaths_diff,
                            last_update,
                        ),
                    )
        else:
            logger.info(
                f"insert_into_covid_states_table :: Empty response from API for date: {date}"
            )

    return None
