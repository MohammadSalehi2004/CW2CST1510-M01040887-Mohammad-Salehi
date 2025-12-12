import pandas as pd
import os
from datetime import datetime
from app.data.db import connect_database

# CRUD functions

#create function
def add_ticket(ticket_id, priority, status, category, subject, description, resolved_date, assigned_to, created_at=None):
    """
    Insert a new IT ticket that will work since now the datetimes are normalized.
    """
    # Normalize inputs
    ticket_id = ticket_id.strip() if ticket_id else None
    category = category.strip() if category else None
    subject = subject.strip() if subject else None
    description = description.strip() if description else None
    assigned_to = assigned_to.strip() if assigned_to else None

    # Ensure created_at is always a formatted string
    if created_at is None:
        created_at = datetime.now().strftime("%Y-%m-%d")

    # Normalize resolved_date to YYYY-MM-DD or None
    if resolved_date:
        try:
            if hasattr(resolved_date, "strftime"):
                resolved_date = resolved_date.strftime("%Y-%m-%d")
            else:
                resolved_date = pd.to_datetime(resolved_date, errors="coerce")
                resolved_date = resolved_date.strftime("%Y-%m-%d") if not pd.isna(resolved_date) else None
        except Exception:
            resolved_date = None
    else:
        resolved_date = None

    conn = connect_database()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO it_tickets
        (ticket_id, priority, status, category, subject, description, resolved_date, assigned_to, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id,
        priority,
        status,
        category,
        subject,
        description,
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
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM it_tickets WHERE id = ?", conn, params=(id,))
    conn.close()
    return df


def get_ticket_by_ticket_id(ticket_id):
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM it_tickets WHERE ticket_id = ?", conn, params=(ticket_id,))
    conn.close()
    return df

#update
def change_ticket_status(id, status, resolved_date=None):
    if resolved_date:
        try:
            if hasattr(resolved_date, "strftime"):
                resolved_date = resolved_date.strftime("%Y-%m-%d")
            else:
                resolved_date = pd.to_datetime(resolved_date, errors="coerce")
                resolved_date = resolved_date.strftime("%Y-%m-%d") if not pd.isna(resolved_date) else None
        except Exception:
            resolved_date = None
    else:
        resolved_date = None

    conn = connect_database()
    cur = conn.cursor()
    if resolved_date is not None:
        cur.execute("UPDATE it_tickets SET status = ?, resolved_date = ? WHERE id = ?", (status, resolved_date, id))
    else:
        cur.execute("UPDATE it_tickets SET status = ? WHERE id = ?", (status, id))
    conn.commit()
    updated_rows = cur.rowcount
    conn.close()
    return updated_rows

#delete
def remove_ticket(id):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM it_tickets WHERE id = ?", (id,))
    conn.commit()
    deleted_rows = cur.rowcount
    conn.close()
    return deleted_rows

#some sql quries
def get_open_tickets():
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM it_tickets WHERE LOWER(status) = 'open' ORDER BY id DESC", conn)
    conn.close()
    return df


def get_closed_tickets():
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM it_tickets WHERE LOWER(status) = 'closed' ORDER BY id DESC", conn)
    conn.close()
    return df


def get_pending_tickets():
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM it_tickets WHERE LOWER(status) = 'resolved' ORDER BY id DESC", conn)
    conn.close()
    return df

#csv loader function
def load_csv_to_table(conn, csv_path, table_name):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Normalize created_at
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
        df["created_at"] = df["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Normalize resolved_date
    if "resolved_date" in df.columns:
        df["resolved_date"] = pd.to_datetime(df["resolved_date"], errors="coerce")
        df["resolved_date"] = df["resolved_date"].dt.strftime("%Y-%m-%d")

    # fix for filling created at dates
    if "created_at" in df.columns:
        df["created_at"] = df["created_at"].fillna(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    df.to_sql(
        name=table_name,
        con=conn,
        if_exists="append",
        index=False
    )

    return len(df)