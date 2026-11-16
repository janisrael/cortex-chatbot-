#!/usr/bin/env python3
"""
Recover Cortex users (and map knowledge paths) from legacy SQLite users.db into MySQL.

Use on the Hetzner server when accounts disappeared after switching systemd to MySQL:
  cd /opt/cortex && venv-prod/bin/python scripts/recover_user_from_sqlite.py --dry-run
  cd /opt/cortex && venv-prod/bin/python scripts/recover_user_from_sqlite.py --import-missing

Knowledge (Chroma, uploads, config) is keyed by numeric user id under:
  /opt/cortex/chroma_db/user_<id>/
  /opt/cortex/uploads/user_<id>/
  /opt/cortex/config/user_<id>/
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_config import DB_CONFIG


def sqlite_users(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, email, username, password_hash, role, created_at, last_login FROM users ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mysql_users():
    import mysql.connector

    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, email, username, role FROM users ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def import_user(row, dry_run: bool) -> str:
    import mysql.connector

    email = row["email"]
    if dry_run:
        return f"would import id={row['id']} {email} ({row['username']})"

    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO users (email, username, password_hash, role, created_at, last_login)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                row["email"],
                row["username"],
                row["password_hash"],
                row.get("role") or "user",
                row.get("created_at"),
                row.get("last_login"),
            ),
        )
        conn.commit()
        new_id = cur.lastrowid
        return f"imported {email} sqlite_id={row['id']} -> mysql_id={new_id} (may need to rename chroma_db/user_{row['id']} if ids differ)"
    except mysql.connector.Error as e:
        conn.rollback()
        return f"skip {email}: {e}"
    finally:
        cur.close()
        conn.close()


def asset_hint(sqlite_id: int, base: str) -> str:
    path = os.path.join(base, f"user_{sqlite_id}")
    if os.path.isdir(path):
        try:
            count = sum(len(files) for _, _, files in os.walk(path))
        except OSError:
            count = "?"
        return f"  assets: {path} (files~{count})"
    return f"  assets: {path} (missing)"


def main():
    parser = argparse.ArgumentParser(description="Recover users from SQLite into MySQL")
    parser.add_argument("--sqlite", default="/opt/cortex/users.db", help="Path to legacy users.db")
    parser.add_argument("--dry-run", action="store_true", help="List actions only")
    parser.add_argument(
        "--import-missing",
        action="store_true",
        help="Insert SQLite users whose email is not already in MySQL",
    )
    parser.add_argument("--search", default="", help="Filter by substring in email/username")
    args = parser.parse_args()

    if not os.path.isfile(args.sqlite):
        print(f"No SQLite database at {args.sqlite}")
        sys.exit(1)

    sq = sqlite_users(args.sqlite)
    try:
        my = mysql_users()
    except Exception as e:
        print(f"MySQL connect failed ({DB_CONFIG.get('host')}/{DB_CONFIG.get('database')}): {e}")
        sys.exit(1)

    my_emails = {u["email"].lower() for u in my}
    filt = (args.search or "").lower()

    print("=== SQLite users ===")
    for u in sq:
        if filt and filt not in (u["email"] or "").lower() and filt not in (u["username"] or "").lower():
            continue
        print(f"  [{u['id']}] {u['email']} | {u['username']} | {u['role']}")
        print(asset_hint(u["id"], "/opt/cortex/chroma_db"))
        print(asset_hint(u["id"], "/opt/cortex/uploads"))
        print(asset_hint(u["id"], "/opt/cortex/config"))

    print("\n=== MySQL users ===")
    for u in my:
        if filt and filt not in (u["email"] or "").lower() and filt not in (u["username"] or "").lower():
            continue
        print(f"  [{u['id']}] {u['email']} | {u['username']} | {u['role']}")

    if args.import_missing:
        print("\n=== Import missing into MySQL ===")
        for u in sq:
            if u["email"].lower() in my_emails:
                continue
            if filt and filt not in (u["email"] or "").lower() and filt not in (u["username"] or "").lower():
                continue
            print(import_user(u, args.dry_run))
    elif not args.dry_run:
        print("\nUse --import-missing to copy SQLite-only accounts into MySQL.")
        print("If MySQL assigns a new id, rename user_* folders to match or re-ingest.")


if __name__ == "__main__":
    main()