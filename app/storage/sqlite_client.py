import sqlite3
import json
import os

DB_PATH = "orderbook_snapshots.db"

def init_schema():
    """Initialize SQLite schema for storing order book snapshots."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orderbook_snapshots (
            ts REAL,
            instrument TEXT,
            bids TEXT,
            asks TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("SQLite table ready at", os.path.abspath(DB_PATH))


def persist_snapshot(snapshot: dict):
    """Insert a snapshot into SQLite DB."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO orderbook_snapshots (ts, instrument, bids, asks)
            VALUES (?, ?, ?, ?)
        """, (
            snapshot["ts"],
            snapshot["instrument"],
            json.dumps(snapshot["bids"]),
            json.dumps(snapshot["asks"])
        ))
        conn.commit()
        conn.close()
        print(f"Inserted snapshot at ts={snapshot['ts']}")
    except Exception as e:
        print(f"[Warning] Failed to persist snapshot: {e}")