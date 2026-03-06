"""Minimal vulnerable Flask app - intentional SQLi for benchmarking."""

import sqlite3
from pathlib import Path

from flask import Flask, request, jsonify

app = Flask(__name__)
DB_PATH = Path(__file__).resolve().parent / "data.db"


def init_db() -> None:
    """Create DB and seed with marker row for exploit detection."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)")
    cur.execute("DELETE FROM items")
    cur.execute("INSERT INTO items (id, name) VALUES (1, 'LEAK_MARKER')")
    cur.execute("INSERT INTO items (id, name) VALUES (2, 'apple'), (3, 'banana')")
    conn.commit()
    conn.close()


@app.route("/health")
def health() -> tuple:
    """Health check endpoint."""
    return ("OK", 200)


@app.route("/")
def index() -> tuple:
    """Root endpoint."""
    return ({"message": "Flask SQLi Demo"}, 200)


@app.route("/search")
def search() -> tuple:
    """Vulnerable search - intentional SQL injection (do not use in production)."""
    q = request.args.get("q", "")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Vulnerable: string concatenation into SQL
    cur.execute(f"SELECT id, name FROM items WHERE name LIKE '%{q}%'")
    rows = cur.fetchall()
    conn.close()
    return ({"results": [{"id": r[0], "name": r[1]} for r in rows]}, 200)


if __name__ == "__main__":
    init_db()
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=False)
