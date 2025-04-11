import psycopg2
from psycopg2.extras import RealDictCursor
from prog.utils.db import get_db_connection

def authenticate_user(login, password):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM Employee WHERE login = %s AND password_hash = crypt(%s, password_hash);",
            (login, password)
        )
        user = cur.fetchone()
    conn.close()
    return user
