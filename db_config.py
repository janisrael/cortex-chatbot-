# db_config.py
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),        # Database host
    'user': os.getenv('DB_USER', 'root'),             # Database username
    'password': os.getenv('DB_PASSWORD', ''),         # Database password
    'database': os.getenv('DB_NAME', 'saturn')        # Database name
}