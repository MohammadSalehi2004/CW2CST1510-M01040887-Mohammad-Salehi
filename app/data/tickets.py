import pandas as pd
import os
from app.data.db import connect_database

# CRUD FUNCTIONS


# crud functuin for creat
def add_ticket(user_id, issue, status, opened_at):
    """Insert a new IT ticket and return its ID."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO it_tickets
        (user_id, issue, status, opened_at)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, issue, status, opened_at)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


# crud function for read

def get_ticket_by_id(ticket_id):
    """Return a single ticket by ID as a DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets WHERE id = ?",
        conn,
        params=(ticket_id,)
    )
    conn.close()
    return df


# crud function for update
def change_ticket_status(ticket_id, status):
    """Update the status of an IT ticket."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("UPDATE it_tickets SET status = ? WHERE id = ?", (status, ticket_id))
    conn.commit()
    updated_rows = cur.rowcount
    conn.close()
    return updated_rows


# delete crud function
def remove_ticket(ticket_id):
    """Delete an IT ticket by ID."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM it_tickets WHERE id = ?", (ticket_id,))
    conn.commit()
    deleted_rows = cur.rowcount
    conn.close()
    return deleted_rows



# sql queries

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


#loading csv function

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