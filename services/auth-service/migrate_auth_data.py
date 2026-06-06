import os
import psycopg2

MONOLITH_URL = "postgres://postgres:postgres@localhost:5432/handcrafts_db"
AUTH_URL = "postgres://postgres:postgres@localhost:5432/auth_db"

def migrate_data():
    print("Connecting to monolith database...")
    monolith_conn = psycopg2.connect(MONOLITH_URL)
    monolith_cursor = monolith_conn.cursor()
    
    print("Connecting to auth database...")
    auth_conn = psycopg2.connect(AUTH_URL)
    auth_cursor = auth_conn.cursor()
    
    # Enable auth_service schema search path
    auth_cursor.execute("SET search_path TO auth_service, public;")
    
    tables_to_migrate = [
        "accounts_role",
        "accounts_user",
        "accounts_user_groups",
        "accounts_user_user_permissions",
        "accounts_user_roles",
        "accounts_address",
        "accounts_customertier",
        "accounts_customer",
        "accounts_supplier",
        "accounts_delivery",
        "accounts_admin",
    ]
    
    for table in tables_to_migrate:
        print(f"Migrating table {table}...")
        monolith_cursor.execute(f"SELECT * FROM {table}")
        rows = monolith_cursor.fetchall()
        if not rows:
            print(f"  No rows found in {table}.")
            continue
            
        columns = [desc[0] for desc in monolith_cursor.description]
        col_names = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        
        insert_query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
        
        try:
            auth_cursor.executemany(insert_query, rows)
            auth_conn.commit()
            print(f"  Migrated {len(rows)} rows into {table}.")
        except Exception as e:
            print(f"  Error migrating {table}: {e}")
            auth_conn.rollback()

    monolith_cursor.close()
    monolith_conn.close()
    auth_cursor.close()
    auth_conn.close()
    print("Auth data migration complete!")

if __name__ == "__main__":
    migrate_data()
