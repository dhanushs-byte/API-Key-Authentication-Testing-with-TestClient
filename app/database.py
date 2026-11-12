
import os
import sqlite3
import hashlib
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DATABASE_PATH", "usage.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            key_hash TEXT UNIQUE NOT NULL,
            request_count INTEGER DEFAULT 0
        )
    """)

    keys = [
        ("user1", os.getenv("API_KEY_USER1")),
        ("user2", os.getenv("API_KEY_USER2"))
    ]

    for username, key in keys:
        if key:
            conn.execute("""
                INSERT OR IGNORE INTO api_users
                (username, key_hash)
                VALUES (?, ?)
            """, (username, hash_api_key(key)))

    conn.commit()
    conn.close()


def find_user(key_hash: str):
    conn = get_connection()

    user = conn.execute(
        "SELECT * FROM api_users WHERE key_hash = ?",
        (key_hash,)
    ).fetchone()

    conn.close()
    return dict(user) if user else None


def increment_request(user_id: int):
    conn = get_connection()

    conn.execute("""
        UPDATE api_users
        SET request_count = request_count + 1
        WHERE id = ?
    """, (user_id,))

    conn.commit()
    conn.close()
