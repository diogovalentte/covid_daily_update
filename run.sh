#!/bin/bash
# This script set the environment within the container

# Installs the python libraries
pip install -r /opt/airflow/requirements.txt

# Setup database tables and data
python -u /opt/airflow/setup_database.py
