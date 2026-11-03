"""Lab 8 image v2: database-backed GET /get_users on port 3000."""
import os
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_PATH = Path(os.getenv("DB_PATH", "/app/data/users.db"))


def connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
        # Only seed an empty database, preserving any records already present.
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            conn.executemany("INSERT INTO users(name) VALUES (?)", [
                ("Alice",), ("Bob",), ("Charlie",)
            ])


@app.get("/health")
def health():
    return jsonify(status="ok", port=3000)


@app.get("/get_users")
def get_users():
    """Read names from the SQLite users table on every request."""
    with connection() as conn:
        rows = conn.execute("SELECT name FROM users ORDER BY id").fetchall()
    return jsonify(users=[row["name"] for row in rows])


@app.post("/users")
def add_user():
    """Optional helper to add names for demonstrating database queries."""
    body = request.get_json(silent=True) or {}
    name = body.get("name")
    if not isinstance(name, str) or not name.strip():
        return jsonify(error="Provide a non-empty string in the name field"), 400
    with connection() as conn:
        cur = conn.execute("INSERT INTO users(name) VALUES (?)", (name.strip(),))
    return jsonify(id=cur.lastrowid, name=name.strip()), 201


initialize_database()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)
