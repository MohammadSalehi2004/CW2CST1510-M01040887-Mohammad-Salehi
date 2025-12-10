import pandas as pd
import os
from app.data.db import connect_database

# CRUD FUNCTIONS

# CREATE function
def create_dataset(dataset_name, category, source, last_updated, record_count, file_size_mb, created_at):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO datasets_metadata
        (dataset_name, category, source, last_updated, record_count, file_size_mb, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (dataset_name, category, source, last_updated, record_count, file_size_mb, created_at)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

# READ

# reading one with id
def get_dataset(dataset_id):
    """Return a single dataset by ID as a DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM datasets_metadata WHERE id = ?",
        conn,
        params=(dataset_id,)
    )
    conn.close()
    return df

# reading all
def list_datasets():
    """Return all datasets as a DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM datasets_metadata ORDER BY id DESC", conn)
    conn.close()
    return df

# UPDATE
def update_dataset(dataset_id, dataset_name, category, source, last_updated, record_count, file_size_mb):
    """Update fields for a dataset by ID."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE datasets_metadata
        SET dataset_name = ?, category = ?, source = ?, last_updated = ?, record_count = ?, file_size_mb = ?
        WHERE id = ?
        """,
        (dataset_name, category, source, last_updated, record_count, file_size_mb, dataset_id)
    )
    conn.commit()
    updated_rows = cur.rowcount
    conn.close()
    return updated_rows

# DELETE
def delete_dataset(dataset_id):
    """Delete a dataset by ID."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM datasets_metadata WHERE id = ?", (dataset_id,))
    conn.commit()
    deleted_rows = cur.rowcount
    conn.close()
    return deleted_rows

# SQL queries
def large_datasets(min_size=100):
    """Return datasets larger than min_size MB."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM datasets_metadata WHERE file_size_mb >= ? ORDER BY file_size_mb DESC",
        conn,
        params=(min_size,)
    )
    conn.close()
    return df

def outdated_datasets(threshold_date):
    """Return datasets older than threshold_date."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM datasets_metadata WHERE last_updated < ? ORDER BY last_updated ASC",
        conn,
        params=(threshold_date,)
    )
    conn.close()
    return df

# loading the dataset csv
def load_csv_to_table(conn, csv_path, table_name):
    """
    Load a CSV file into a database table using pandas.
    Keeps 'id' column from CSV so IDs match exactly.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Ensure 'id' is integer type
    if "id" in df.columns:
        df["id"] = df["id"].astype(int)

    # Insert rows including the CSV's IDs
    df.to_sql(
        name=table_name,
        con=conn,
        if_exists="append",
        index=False
    )

    return len(df)
