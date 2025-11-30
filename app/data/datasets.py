import pandas as pd
from pathlib import Path
from app.data.db import connect_database
import os

# CRUD FUNCTIONS

#creat function

def create_dataset(dataset_name, category, source, last_updated,
                   record_count, file_size_mb):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO datasets_metadata
        (dataset_name, category, source, last_updated, record_count, file_size_mb)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dataset_name, category, source, last_updated, record_count, file_size_mb))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

#read function

def get_dataset(dataset_id):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("SELECT * FROM datasets_metadata WHERE id = ?", (dataset_id,))
    row = cur.fetchone()
    conn.close()
    return row


def list_datasets(limit=500):
    conn = connect_database()
    df = pd.read_sql_query(
        f"SELECT * FROM datasets_metadata ORDER BY last_updated DESC LIMIT {limit}",
        conn
    )
    conn.close()
    return df.to_dict(orient="records")

#update function

def update_dataset(dataset_id, **fields):
    if not fields:
        return False

    conn = connect_database()
    cur = conn.cursor()

    updates = ", ".join(f"{k}=?" for k in fields.keys())
    values = list(fields.values()) + [dataset_id]

    cur.execute(f"UPDATE datasets_metadata SET {updates} WHERE id = ?", values)
    conn.commit()
    rows = cur.rowcount
    conn.close()
    return rows > 0

#delete function

def delete_dataset(dataset_id):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM datasets_metadata WHERE id = ?", (dataset_id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted


#sql queries

def large_datasets(min_size=100):
    """WHERE, ORDER BY"""
    conn = connect_database()
    df = pd.read_sql_query("""
        SELECT *
        FROM datasets_metadata
        WHERE file_size_mb >= ?
        ORDER BY file_size_mb DESC
    """, conn, params=(min_size,))
    conn.close()
    return df


def outdated_datasets(threshold_date):
    """WHERE date < some threshold"""
    conn = connect_database()
    df = pd.read_sql_query("""
        SELECT *
        FROM datasets_metadata
        WHERE last_updated < ?
        ORDER BY last_updated ASC
    """, conn, params=(threshold_date,))
    conn.close()
    return df

#loading csv file function
def load_csv_to_table(conn, csv_path, table_name):
    """
    Load a CSV file into a database table using pandas.
    Drops 'id' or 'ticket_id' column if present to avoid UNIQUE constraint errors.
    """
    import os
    import pandas as pd

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Drop primary key columns if present
    for col in ["id", "ticket_id"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    df.to_sql(
        name=table_name,
        con=conn,
        if_exists="append",
        index=False
    )

    return len(df)