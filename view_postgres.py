PS C:\Users\THINKPAD\Documents\slideshow-maker> git push -u origin main
To https://github.com/yoyski/slideshow-maker.git
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'https://github.com/yoyski/slideshow-maker.git'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. This is usually caused by another repository pushing to
hint: the same ref. If you want to integrate the remote changes, use
hint: 'git pull' before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
PS C:\Users\THINKPAD\Documents\slideshow-maker> #!/usr/bin/env python3
"""View PostgreSQL database contents"""
import psycopg2
import psycopg2.extras
from tabulate import tabulate

# Connection details
conn_string = "postgresql://postgres:password123@localhost:5432/slideshow_maker"

try:
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    print("\n" + "="*60)
    print("POSTGRESQL DATABASE VIEWER")
    print("="*60)
    
    # Get tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()
    
    print(f"\n📊 Tables in database: slideshow_maker")
    print("-" * 60)
    
    for table in tables:
        table_name = table['table_name']
        
        # Get row count
        cur.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        count = cur.fetchone()['count']
        
        print(f"\n📋 Table: {table_name.upper()} ({count} rows)")
        print("-" * 60)
        
        if count > 0:
            # Get all data
            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            
            # Convert to list of dicts for tabulate
            data = [dict(row) for row in rows]
            
            # Print as table
            print(tabulate(data, headers="keys", tablefmt="grid"))
        else:
            print("   (no data)")
    
    conn.close()
    print("\n" + "="*60)
    print("✓ Connection successful!")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n❌ Error connecting to database:")
    print(f"   {e}\n")
