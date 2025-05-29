# import psycopg2

# try:
#     # Try Docker connection
#     print("Connecting to Docker PostgreSQL...")
#     conn = psycopg2.connect(
#         host="localhost",
#         port="5433",
#         database="postgres", 
#         user="postgres",
#         password="nhancho1707"
#     )
    
#     # Test query
#     cursor = conn.cursor()
#     cursor.execute("SELECT version();")
#     version = cursor.fetchone()
#     print(f"Connected to: {version[0]}")
    
#     # Test pgvector
#     cursor.execute("SELECT 'vector'::regtype;")
#     print("pgvector is installed!")
    
#     conn.close()
#     print("Connection test successful")
    
# except Exception as e:
#     print(f"Connection error: {e}")

import psycopg2
conn = psycopg2.connect(host="localhost", port="5433", dbname="postgres", user="postgres", password="nhancho1707")
cur = conn.cursor()
cur.execute("SELECT 'vector'::regtype;")
print(cur.fetchone())