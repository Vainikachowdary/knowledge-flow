import os
import psycopg
from dotenv import load_dotenv

print("Starting database setup...")

load_dotenv("../.env")

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL not found in .env")

with psycopg.connect(database_url, connect_timeout=5) as connection:
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                filename TEXT NOT NULL,
                source TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_hash TEXT
            );
        """)

        cursor.execute("""
            ALTER TABLE documents
            ADD COLUMN IF NOT EXISTS file_hash TEXT;
        """)

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS documents_file_hash_unique
            ON documents(file_hash);
        """)

    connection.commit()

print("Documents table is ready!")
