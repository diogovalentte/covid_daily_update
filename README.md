# Covid Daily Update
## OBJECTIVES: 
1. Create two tables on a PostgresSQL database.
2. Populate these two tables with available daily data about Covid-19 in Brazil and its states.
3. Create an Airflow DAG to daily update the tables data with new data from yesterday.
---
- The table "covid_brazil" contains daily data about Covid-19 in Brazil from 2020-02-26 to yesterday.
- The table "covid_states" contains daily data about Covid-19 in the brazilian states from 2020-05-19 to yesterday.
- We use the [covid-api](http://covid-api.com/api/) API to request the data.
 
---
## Tables schemas:

#### "covid_brazil": Daily data about Covid-19 in Brazil.

| date       | confirmed_accumulated                 | confirmated_difference                                 | deaths_accumulated                     | deaths_difference                                       | last_update       |
|------------|---------------------------------------|--------------------------------------------------------|----------------------------------------|---------------------------------------------------------|-------------------|

#### "covid_states": Daily data about Covid-19 in the brazilian states.

| state  | date       | confirmed_accumulated                 | confirmated_difference                                 | deaths_accumulated                     | deaths_difference                                       | last_update       |
|--------|------------|---------------------------------------|--------------------------------------------------------|----------------------------------------|---------------------------------------------------------|-------------------|
---
# How to use this project:

### Prerequisites:
- Have [Docker](https://www.docker.com) and [Docker Compose](https://docs.docker.com/compose/install/#install-compose) installed.
    - The Docker Compose original file is [here](https://airflow.apache.org/docs/apache-airflow/2.5.2/docker-compose.yaml).

---
1. Create the containers folders and add an environment variable:
```sh
mkdir -p ./dags ./logs ./plugins && echo -e "AIRFLOW_UID=$(id -u)" > .env
```
2. Run database migrations and create the first user account:
```sh
docker compose up airflow-init
```
3. Execute the bellow command to start the containers in the background.
```sh
docker compose up -d
```
- The Airflow webserver interface will be available in port 8080 (username and password are "airflow"). The PostgresSQL server will be available in port 5434 (the database name is "daily_covid", the username is "root" and the password is "password").
- You can use any program to connect to the PostgreSQL database or use psql with the bellow command:
```sh
docker exec -it covid-database psql -U root -d daily_covid
```
---
4. Execute the bellow command to:
   - Configure the Airflow container environment.
   - Creates the PostgreSQL database tables.
   - Populate the tables with ALL data available in the API until yesterday.
```sh
docker exec airflow-webserver /bin/bash /opt/airflow/run.sh
```
5. Execute the bellow command to activate the Airflow DAG to daily update the database data.
```sh
docker exec airflow-webserver airflow dags unpause daily_update_covid_tables
```
6. Now the day will daily update the data of the tables with yesterday data at 06:00 UTC.
---

## Additional commands:

#### Show all containers running:
```sh
docker ps
```
#### Stop the project containers:
```sh
docker compose down
``` 
#### Executes a command inside a container:
```sh
docker exec <container name/id> <command>
```
#### Show a container log:
```sh
docker logs <container name/id>
```
