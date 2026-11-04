import os
import psycopg
from dotenv import load_dotenv

load_dotenv("../.env")

database_url = os.getenv("DATABASE_URL")


#to save documents
def save_document(filename, source, file_hash):
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents (filename, source, file_hash)
                VALUES (%s, %s, %s);
                """,
                (filename, source, file_hash)
            )

        connection.commit()

# to check whether a document already exists
def document_exists(file_hash):
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1 FROM documents
                WHERE file_hash = %s

                LIMIT 1;
                """,
                (file_hash,)
            )

            return cursor.fetchone() is not None

#to get all documents at once
def get_documents():
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM documents;")
            rows = cursor.fetchall()

            return rows


#to delete particular documents

def delete_document(document_id):
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "Delete FROM documents WHERE id = %s;",
                (document_id,)
        
            )

        connection.commit()



#to get a particular document
def get_document(document_id):
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM documents WHERE ID =%s;",
                (document_id,)
            )
            row = cursor.fetchone()

            return row