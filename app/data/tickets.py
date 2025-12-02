import pandas as pd
import os
from app.data.db import connect_database

#CRUD functions

#creat
def add_ticket(ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to, created_at):
    """Insert a new IT ticket with full details."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO it_tickets
        (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id,
        priority,
        status,
        category,
        subject,
        description,
        created_date,
        resolved_date,
        assigned_to,
        created_at
    ))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

#read
def get_ticket_by_id(id):
    """Return a single ticket by primary key ID as a DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets WHERE id = ?",
        conn,
        params=(id,)
    )
    conn.close()
    return df


def get_ticket_by_ticket_id(ticket_id):
    """Return a single ticket by external ticket_id as a DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets WHERE ticket_id = ?",
        conn,
        params=(ticket_id,)
    )
    conn.close()
    return df

#update
def change_ticket_status(id, status):
    """Update the status of an IT ticket by primary key ID."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("UPDATE it_tickets SET status = ? WHERE id = ?", (status, id))
    conn.commit()
    updated_rows = cur.rowcount
    conn.close()
    return updated_rows

#delete
def remove_ticket(id):
    """Delete an IT ticket by primary key ID."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM it_tickets WHERE id = ?", (id,))
    conn.commit()
    deleted_rows = cur.rowcount
    conn.close()
    return deleted_rows

#a bit of sql queries

def get_open_tickets():
    """Return tickets with status 'open'."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets WHERE status = 'open' ORDER BY id DESC",
        conn
    )
    conn.close()
    return df


def get_closed_tickets():
    """Return tickets with status 'closed'."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets WHERE status = 'closed' ORDER BY id DESC",
        conn
    )
    conn.close()
    return df


def get_pending_tickets():
    """Return tickets with status 'resolved'."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets WHERE status = 'resolved' ORDER BY id DESC",
        conn
    )
    conn.close()
    return df

#CSV loader

def load_csv_to_table(conn, csv_path, table_name):
    """
    Load a CSV file into a database table using pandas.
    Drops only 'id' column if present to avoid UNIQUE constraint errors.
    Preserves 'ticket_id' so imported tickets keep their identifiers.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Drop primary key column if present
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    df.to_sql(
        name=table_name,
        con=conn,
        if_exists="append",
        index=False
    )

    return len(df)