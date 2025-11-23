import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        database='inventory_manager',
        user='postgres',
        password='root',
        port=5432
    )
    print("✅ Connected to database!")
    
    cur = conn.cursor()
    
    # List all tables
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = cur.fetchall()
    print("Tables in database:", tables)
    
    # Check if inventory table exists and has data
    if ('inventory',) in tables:
        print("✅ Inventory table exists!")
        cur.execute("SELECT COUNT(*) FROM inventory;")
        count = cur.fetchone()[0]
        print(f"Records in inventory table: {count}")
        
        # Show table structure
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'inventory';")
        columns = cur.fetchall()
        print("Inventory table columns:")
        for column in columns:
            print(f"  - {column[0]}: {column[1]}")
            
        # Show sample data if any exists
        if count > 0:
            cur.execute("SELECT * FROM inventory LIMIT 5;")
            rows = cur.fetchall()
            print("Sample data:")
            for row in rows:
                print(f"  {row}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
