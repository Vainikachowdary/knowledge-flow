import os
import psycopg
from dotenv import load_dotenv

print("1. Starting...")

load_dotenv("../.env")

database_url = os.getenv("DATABASE_URL")

print("2. Database URL loaded:", bool(database_url))

print("3. Connecting to PostgreSQL...")

with psycopg.connect(database_url, connect_timeout=5) as connection:
    print("4. Connected!")

    with connection.cursor() as cursor:
        print("5. Creating table...")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                filename TEXT NOT NULL,
                source TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

    connection.commit()

print("6. Documents table created!")