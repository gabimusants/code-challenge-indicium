import airflow
import psycopg2
import csv
import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

load_dotenv()

# Function to get all the table names
def get_table_names():
	# Connection to the database Northwind
	con = psycopg2.connect(
        database='northwind',
        user='northwind_user',
        password='thewindisblowing',
        host='localhost',
    )
	
	cursor = con.cursor()
	cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
	table_names = [row[0] for row in cursor.fetchall()]

	cursor.close()
	con.close()
	return table_names

# Function to extract the data from the csv file and write locally
def extract_write_csv(date):
	# Date of the execution of the task
	date_csv = date
	# Path to the folder where the data is going to be saved, gets the path in a .env file and add the date
	folder_csv = os.getenv("folder_csv") + date_csv.strftime('%Y-%m-%d')
	# Create the directory if it doesn't exist
	os.makedirs(folder_csv, exist_ok = True)
	csv_data = []

	# Write the data in the right place	
	file_path = os.path.join(folder_csv, 'extracted_order_csv.csv')
	with open(os.getenv("path_order_csv_file"), 'r', newline='') as order_details_file, open(file_path, 'w', newline='') as extract_file_csv:
		reader = csv.reader(order_details_file)
		writer = csv.writer(extract_file_csv)

		for row in reader:
			writer.writerow(row)

# Function to extract the data from the postgres database and write locally
def extract_write_postgres(date):
	# Get all the tables name
	table_names = get_table_names()
	date_postgres = date

	# Connection to the database Northwind
	con = psycopg2.connect(
		database = "northwind",
		user = "northwind_user",
		password = "thewindisblowing",
		host = "localhost"
	)

	cursor = con.cursor()

	# Saves the data from the tables in different folders
	for table in table_names:
		cursor.execute(f'SELECT * FROM {table};')
		table_data = cursor.fetchall()
		folder_postgres = os.getenv("folder_postgres") + f'{table}/' + date_postgres.strftime('%Y-%m-%d')
		os.makedirs(folder_postgres, exist_ok = True)

		file_path = os.path.join(folder_postgres, 'extracted_' + f'{table}' + '_postgres.csv')
		with open(file_path, 'w') as extract_file_postgres:
			writer = csv.writer(extract_file_postgres)
			writer.writerow([info[0] for info in cursor.description])
			writer.writerows(table_data)

	cursor.close()
	con.close()

# Function that will call both functions responsibles for the task 1
def extract_write_local(**kwargs):
	date = kwargs['execution_date']
	extract_write_postgres(date)
	extract_write_csv(date)

# Function that will save the data stored locally in the final database 
def write_second_db(**kwargs):
	db_date = kwargs['execution_date']
	# Store all the table names in the variable table_names
	table_names = get_table_names()
	con_db = create_engine(
        'postgresql://postgres:123456@localhost:5460/final_db'
    )

	# Saves the csv file in database
	file_path_csv = os.getenv("file_path_csv") + db_date.strftime('%Y-%m-%d') + '/extracted_order_csv.csv'
	df = pd.read_csv(file_path_csv)
	df.to_sql('order_details', con=con_db, if_exists="replace", index=False)

	# Saves all the tables in database
	for table in table_names:
		file_path_postgres = os.getenv("file_path_postgres") + f'{table}/' + db_date.strftime('%Y-%m-%d') + '/extracted_' + f'{table}' + '_postgres.csv'
		df = pd.read_csv(file_path_postgres)
		df.to_sql(table, con=con_db, if_exists="replace", index=False)
	con_db.dispose()

	# Call the function that will return the final query with the orders and its details
	final_query()

# Function responsible to get the final query with the orders and its details
def final_query():
	con_db = create_engine(
        'postgresql://postgres:123456@localhost:5460/final_db'
    )

	final_query = """ SELECT ord.*, ord_d.*
					  FROM orders ord JOIN order_details ord_d
					  ON ord.order_id = ord_d.order_id
					  ORDER BY ord.order_id, ord_d.order_id;
				  """

	df = pd.read_sql_query(final_query, con_db)
	con_db.dispose()

	# Saves the final query
	file_path_final_query = os.getenv("file_path_final_query")
	df.to_csv(file_path_final_query, index = False)

# Default arguments of the DAG
default_args = {
	'owner': 'gabi',
	'retries': 3,
	'retry_delay': timedelta(minutes=1)
}

dag_name = "LH_ED_GABRIELLEMUNIZ"

with DAG(dag_name, default_args = default_args, schedule = "@daily", 
		  start_date = datetime(2023, 1, 1), catchup = False) as dag:

	extract_write_local = PythonOperator (
		task_id = 'extract_write_local',
		python_callable = extract_write_local,
	)

	write_second_db = PythonOperator (
		task_id = 'write_second_db',
		python_callable = write_second_db
	)

	extract_write_local >> write_second_db