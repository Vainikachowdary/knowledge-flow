import os
import psycopg
from dotenv import load_dotenv

load_dotenv("../.env")

database_url = os.getenv("DATABASE_URL")


def save_document(filename, source):
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents (filename, source)
                VALUES (%s, %s);
                """,
                (filename, source)
            )

        connection.commit()