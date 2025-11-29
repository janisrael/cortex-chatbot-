#!/usr/bin/env python3
"""
Script to create an admin account
Usage: python3 create_admin.py <email> <username> <password>
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user import User

if len(sys.argv) != 4:
    print("Usage: python3 create_admin.py <email> <username> <password>")
    sys.exit(1)

email = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]

# Check if user already exists
if User.email_exists(email):
    print(f"❌ User with email {email} already exists")
    sys.exit(1)

if User.username_exists(username):
    print(f"❌ Username {username} already taken")
    sys.exit(1)

# Create admin user
user_id = User.create_user(email, username, password, role='admin')

if user_id:
    print(f"✅ Admin account created successfully!")
    print(f"   Email: {email}")
    print(f"   Username: {username}")
    print(f"   Role: admin")
else:
    print("❌ Failed to create admin account")
    sys.exit(1)
