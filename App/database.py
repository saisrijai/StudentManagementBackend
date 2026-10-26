```python
import sqlite3

DATABASE_NAME = "students.db"


def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    """Create the students table if it does not exist."""
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            course TEXT,
            address TEXT,
            enrollment_date TEXT
        )
    """)

    conn.commit()
    conn.close()
