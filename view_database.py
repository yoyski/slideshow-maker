#!/usr/bin/env python
"""
Simple script to view PostgreSQL database content
"""
import psycopg2
import os
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not set in .env file")
    exit(1)

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("\n" + "="*60)
    print("PostgreSQL Database Viewer")
    print("="*60 + "\n")
    
    # Get all tables
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()
    
    if not tables:
        print("✓ Database connected but no tables yet (empty)")
    else:
        print(f"✓ Found {len(tables)} table(s)\n")
        
        for (table_name,) in tables:
            print(f"\n{'='*60}")
            print(f"Table: {table_name}")
            print(f"{'='*60}")
            
            # Get column info
            cur.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
            """)
            columns = cur.fetchall()
            print("\nColumns:")
            for col_name, col_type in columns:
                print(f"  • {col_name}: {col_type}")
            
            # Get row count
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            print(f"\nRows: {count}")
            
            # Display data if exists
            if count > 0:
                cur.execute(f"SELECT * FROM {table_name}")
                rows = cur.fetchall()
                col_names = [desc[0] for desc in cur.description]
                print(f"\nData:")
                print(tabulate(rows, headers=col_names, tablefmt="grid"))
            else:
                print("(No data yet)")
    
    cur.close()
    conn.close()
    
    print("\n" + "="*60)
    print("✓ Connection successful!")
    print("="*60 + "\n")

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
