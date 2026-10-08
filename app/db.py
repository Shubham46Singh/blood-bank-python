import os

import psycopg
from psycopg.rows import dict_row


def url():
    return os.environ.get("DATABASE_URL", "")


def connect():
    return psycopg.connect(url(), row_factory=dict_row)


def query(sql, params=None):
    with connect() as conn, conn.cursor() as cur:
        cur.execute(sql, params or ())
        if cur.description is None:
            return []
        return cur.fetchall()
