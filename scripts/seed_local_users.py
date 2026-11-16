#!/usr/bin/env python3
"""Create or reset local dev accounts (admin + normal user). Safe to run repeatedly."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from werkzeug.security import generate_password_hash

from models.user import User
from models.chatbot_appearance import ChatbotAppearance


LOCAL_ACCOUNTS = (
    {
        "email": "admin@example.com",
        "username": "admin",
        "password": "admin123",
        "role": "admin",
    },
    {
        "email": "user@example.com",
        "username": "UserNormal",
        "password": "user123",
        "role": "user",
    },
)


def _set_password(email: str, password: str) -> None:
    import sqlite3

    conn = User._get_db_connection()
    if not User._is_sqlite(conn):
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE email = %s",
            (generate_password_hash(password), email),
        )
        conn.commit()
        cursor.close()
    else:
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE email = ?",
            (generate_password_hash(password), email),
        )
        conn.commit()
    conn.close()


def ensure_account(email, username, password, role):
    existing = User.get_by_email(email)
    if existing:
        _set_password(email, password)
        if existing.role != role:
            import sqlite3

            conn = User._get_db_connection()
            if User._is_sqlite(conn):
                conn.execute("UPDATE users SET role = ? WHERE email = ?", (role, email))
                conn.commit()
            else:
                cur = conn.cursor()
                cur.execute("UPDATE users SET role = %s WHERE email = %s", (role, email))
                conn.commit()
                cur.close()
            conn.close()
        print(f"  updated: {email} / {password} (role={role})")
        return existing.id

    user_id, error = User.create_user(email, username, password, role=role)
    if user_id:
        print(f"  created: {email} / {password} (role={role})")
        return user_id
    print(f"  failed {email}: {error}", file=sys.stderr)
    return None


def main():
    User.init_db()
    ChatbotAppearance.init_db()
    ChatbotAppearance.ensure_schema()
    print("Local accounts:")
    for acc in LOCAL_ACCOUNTS:
        ensure_account(**acc)
    print("")
    print("Non-admin dashboard: http://127.0.0.1:6001/dashboard")
    print("  login → user@example.com / user123")
    print("Admin: admin@example.com / admin123")


if __name__ == "__main__":
    main()