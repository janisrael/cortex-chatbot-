from db_model import get_connection

def setup():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SET FOREIGN_KEY_CHECKS=0")

    # Create chat_logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_logs (
        id INT PRIMARY KEY AUTO_INCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        user_id VARCHAR(100),
        message TEXT NOT NULL,
        sender ENUM('user', 'bot') NOT NULL,
        sales_flag VARCHAR(50),
        success_flag ENUM('Yes', 'No') DEFAULT 'No',
        intent VARCHAR(50), 
        context_snapshot TEXT
    )
                   
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_nodes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            convo_id VARCHAR(64),
            node_id INT,
            parent_id INT,
            user_id VARCHAR(255),
            message TEXT,
            sender VARCHAR(10),
            topic VARCHAR(100),
            intent VARCHAR(100),
            sales_flag BOOLEAN,
            success_flag BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            phone VARCHAR(20),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Ensure the success_flag column exists in case of schema changes
    cursor.execute("""
    ALTER TABLE chat_logs
    ADD COLUMN IF NOT EXISTS success_flag ENUM('Yes', 'No') DEFAULT 'No';
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Migration complete, Database Created!")

if __name__ == "__main__":
    setup()
