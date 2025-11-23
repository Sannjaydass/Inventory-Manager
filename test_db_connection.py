import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        database='inventory_manager',
        user='root',
        password='root',
        port=5432
    )
    print("✅ Successfully connected to PostgreSQL!")
    
    # Test query to see your data
    cur = conn.cursor()
    cur.execute("SELECT * FROM inventory;")
    rows = cur.fetchall()
    print(f"✅ Found {len(rows)} records in inventory table")
    
    # Show column names and sample data
    if rows:
        print("Sample data:")
        for row in rows[:3]:  # Show first 3 rows
            print(row)
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error connecting to PostgreSQL: {e}")
