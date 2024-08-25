import os

import pandas as pd
import re
import psycopg2

# This script was used to create the Database tables and columns

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)
cursor = conn.cursor()

# Read CSV file into a Pandas DataFrame
df = pd.read_csv(os.path.join('data', 'data.csv'))

# Replace column name spaces with underscores and remove non-alphanumeric characters (except underscores)
df.columns = [re.sub(r'\W+', '_', col) for col in df.columns]

# Function to map DataFrame column types to SQL types
def map_dtype(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return 'INTEGER'
    elif pd.api.types.is_float_dtype(dtype):
        return 'NUMERIC'
    elif pd.api.types.is_bool_dtype(dtype):
        return 'BOOLEAN'
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return 'TIMESTAMP'
    else:
        return 'VARCHAR'


def create_table(cursor, table_name, df, unique_columns):
    columns = []
    for col, dtype in zip(df.columns, df.dtypes):
        pg_type = map_dtype(dtype)
        columns.append(f"{col} {pg_type}")

    # add unique columns
    unique_constraint = f", UNIQUE({', '.join(unique_columns)})" if unique_columns else ""

    create_stmt = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join(columns)}
        {unique_constraint}
    );
    """
    cursor.execute(create_stmt)



create_table(cursor, 'joukkuedata', df, unique_columns=['gameid', 'teamid'])
create_table(cursor, 'pelaajadata', df, unique_columns=['gameid', 'playerid'])


conn.commit()
cursor.close()
conn.close()

