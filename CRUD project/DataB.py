import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = "database.db"


def get_db_conn():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            salary REAL NOT NULL
        )
    """)

    admin = cursor.execute(
        "SELECT * FROM admins WHERE email = ?",
        ("admin@staffsync.com",)
    ).fetchone()

    if not admin:
        cursor.execute(
            """
            INSERT INTO admins
            (first_name, email, password)
            VALUES (?, ?, ?)
            """,
            (
                "Admin",
                "admin@staffsync.com",
                generate_password_hash("admin123")
            )
        )

    conn.commit()
    conn.close()


init_db()