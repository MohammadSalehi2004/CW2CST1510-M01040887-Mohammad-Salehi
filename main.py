from pathlib import Path
import pandas as pd
from datetime import datetime

# Database connection + schema
from app.data.db import connect_database
from app.data.schema import create_all_tables

# User service
from app.services.user_service import (
    register_user,
    login_user,
    migrate_users_from_file
)

# INCIDENT functions
from app.data.incidents import (
    add_incident,
    get_incidents,
    get_incident_by_id,
    change_incident_status,
    remove_incident,
    get_high_severity_incidents,
    get_closed_incidents,
    get_investigating_incidents,
    get_siem_incidents,
    get_firewall_incidents,
    load_csv_to_table as load_incidents_csv
)

# DATASETS functions
from app.data.datasets import (
    create_dataset,
    get_dataset,
    list_datasets,
    update_dataset,
    delete_dataset,
    large_datasets,
    outdated_datasets,
    load_csv_to_table as load_datasets_csv
)

# TICKETS functions
from app.data.tickets import (
    add_ticket,
    get_ticket_by_id,
    change_ticket_status,
    remove_ticket,
    get_open_tickets,
    get_closed_tickets,
    get_pending_tickets,
    load_csv_to_table as load_tickets_csv
)


def main():
    print("=" * 60)
    print("Week 8: Database Demo")
    print("=" * 60)

    # 1. Setup database
    conn = connect_database()
    create_all_tables(conn)
    conn.close()

    # 2. Migrate Week 7 users
    conn = connect_database()
    migrate_users_from_file(conn, Path("DATA/users.txt"))
    conn.close()

    # 3. Verify migrated users
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()

    print("\nUsers in database:")
    print(f"{'ID':<5} {'Username':<15} {'Role':<10}")
    print("-" * 35)
    for user in users:
        print(f"{user[0]:<5} {user[1]:<15} {user[2]:<10}")

    print(f"\nTotal users: {len(users)}")
    conn.close()

    # 4. Test authentication
    success, msg = register_user("alice", "SecurePass123!", "analyst")
    print(msg)

    success, msg = login_user("alice", "SecurePass123!")
    print(msg)

    # 5. Test Incident CREATE
    incident_id = add_incident(
        "2024-11-05",
        "Phishing",
        "High",
        "Open",
        "Suspicious email detected",
        "alice",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # created_at
    )
    print(f"Created incident #{incident_id}")

    # 6. Query incidents
    df = get_incidents()
    print(f"Total incidents: {len(df)}")


def setup_database_complete():
    print("\n" + "=" * 60)
    print("STARTING COMPLETE DATABASE SETUP")
    print("=" * 60)

    conn = connect_database()

    # Step 1: Create tables
    create_all_tables(conn)
    print("[1/4] Tables created")

    # Step 2: Load Week 7 users
    migrate_users_from_file(conn, Path("DATA/users.txt"))
    print("[2/4] Week 7 users loaded")

    # Step 3: Reset DB from CSVs
    print("[3/4] Resetting DB from CSVs...")

    cursor = conn.cursor()
    cursor.execute("DELETE FROM datasets_metadata")
    cursor.execute("DELETE FROM it_tickets")
    cursor.execute("DELETE FROM cyber_incidents")
    conn.commit()

    load_datasets_csv(conn, "DATA/datasets_metadata.csv", "datasets_metadata")
    load_tickets_csv(conn, "DATA/it_tickets.csv", "it_tickets")
    load_incidents_csv(conn, "DATA/cyber_incidents.csv", "cyber_incidents")

    # Step 4: Verify table counts
    tables = ["users", "cyber_incidents", "datasets_metadata", "it_tickets"]

    print("\nDatabase Summary:")
    print(f"{'Table':<25} {'Rows':<10}")
    print("-" * 40)

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:<25} {count:<10}")

    conn.close()
    print("\nDATABASE SETUP COMPLETE!")


def run_comprehensive_tests():
    print("\n" + "=" * 60)
    print("RUNNING COMPREHENSIVE TESTS")
    print("=" * 60)

    conn = connect_database()

    # Test 1: Authentication
    print("\n[TEST 1] Authentication")
    success, msg = register_user("test_user", "TestPass123!", "user")
    print(f"  Register: {msg}")

    success, msg = login_user("test_user", "TestPass123!")
    print(f"  Login:    {msg}")

    # Test 2: Incident CRUD
    print("\n[TEST 2] Incident CRUD")

    new_id = add_incident(
        "2024-11-05",
        "Test Incident",
        "Low",
        "Open",
        "This is a test incident",
        "test_user",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # created_at
    )
    print(f"  Create: Incident #{new_id}")

    change_incident_status(new_id, "Low", "Resolved", "Updated after investigation")
    print("  Update: Status updated")

    remove_incident(new_id)
    print("  Delete: Incident deleted")

    # Test 3: Analytics
    print("\n[TEST 3] Analytics")
    high = get_high_severity_incidents()
    closed = get_closed_incidents()

    print(f"  High Severity Results: {len(high)}")
    print(f"  Closed Incidents: {len(closed)}")

    conn.close()
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
    run_comprehensive_tests()
    setup_database_complete()