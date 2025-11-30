import pandas as pd
import os
from app.data.db import connect_database

# CRUD FUNCTIONS

# CREATE function
def add_incident(date, incident_type, severity, status, description, reported_by, created_at):
    """Insert a new incident entry and return its ID."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO cyber_incidents
        (date, incident_type, severity, status, description, reported_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (date, incident_type, severity, status, description, reported_by, created_at)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

# READ
def get_incidents():
    """Return all cyber incidents as a DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM cyber_incidents ORDER BY id DESC", conn)
    conn.close()
    return df

def get_incident_by_id(incident_id):
    """Return a single incident by ID as a DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents WHERE id = ?",
        conn,
        params=(incident_id,)
    )
    conn.close()
    return df

# UPDATE
def change_incident_status(incident_id, status):
    """Update the status of a specific incident."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("UPDATE cyber_incidents SET status = ? WHERE id = ?", (status, incident_id))
    conn.commit()
    updated_rows = cur.rowcount
    conn.close()
    return updated_rows

# DELETE
def remove_incident(incident_id):
    """Delete an incident by ID."""
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM cyber_incidents WHERE id = ?", (incident_id,))
    conn.commit()
    deleted_rows = cur.rowcount
    conn.close()
    return deleted_rows

# SQL queries
def get_high_severity_incidents():
    """Return all incidents with severity 'high'."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents WHERE severity = 'high' ORDER BY id DESC",
        conn
    )
    conn.close()
    return df

def get_closed_incidents():
    """Return all incidents with status 'closed'."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents WHERE status = 'closed' ORDER BY id DESC",
        conn
    )
    conn.close()
    return df

def get_investigating_incidents():
    """Return all incidents with status 'investigating'."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents WHERE status = 'investigating' ORDER BY id DESC",
        conn
    )
    conn.close()
    return df

def get_siem_incidents():
    """Return all incidents reported by SIEM."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents WHERE reported_by = 'SIEM' ORDER BY id DESC",
        conn
    )
    conn.close()
    return df

def get_firewall_incidents():
    """Return all incidents reported by Firewall."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents WHERE reported_by = 'Firewall' ORDER BY id DESC",
        conn
    )
    conn.close()
    return df

# loading the cyber incident csv
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