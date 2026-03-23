import sqlite3
from contextlib import contextmanager
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "finance.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT DEFAULT 'Uncategorized',
                predicted_category TEXT,
                confidence REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                budget REAL DEFAULT 0.0,
                color TEXT DEFAULT '#6366f1'
            );

            CREATE TABLE IF NOT EXISTS monthly_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                category TEXT NOT NULL,
                total REAL NOT NULL,
                UNIQUE(year, month, category)
            );

            INSERT OR IGNORE INTO categories (name, color) VALUES
                ('Food', '#f59e0b'),
                ('Travel', '#3b82f6'),
                ('Bills', '#ef4444'),
                ('Shopping', '#8b5cf6'),
                ('Entertainment', '#ec4899'),
                ('Healthcare', '#10b981'),
                ('Education', '#f97316'),
                ('Subscriptions', '#06b6d4'),
                ('Other', '#6b7280');
        """)

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
