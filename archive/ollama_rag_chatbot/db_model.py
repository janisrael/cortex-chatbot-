import mysql.connector
from datetime import datetime
from sales_intent_classifier import classify_message  # Your classifier
from db_config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)

def log_chat(user_id, message, sender, intent=None, sales_flag=None, success_flag=None):
    try:
        # Convert values to native Python types
        user_id = user_id or None
        message = str(message)
        sender = str(sender)
        intent = str(intent)
        sales_flag = int(sales_flag) if sales_flag is not None else 0
        # Classify the message if intent not provided
        # if intent is None:
        #     label, sales = classify_message(message)
        #     intent = str(label)
        #     sales_flag = int(sales)
        # else:
        #     intent = str(intent)
        #     sales_flag = int(sales_flag) if sales_flag is not None else 0

        logger.info(f"this is the succes flag after {success_flag}")
        if success_flag == None:
            success_flag = 'No'
        else:
            if int(success_flag):
                if success_flag == 1:
                    success_flag = 'Yes'
                else:
                    success_flag = 'No'
            else:
                if success_flag == 'Yes':
                    success_flag = 'Yes'
                else:
                    success_flag = 'No'
            # success_flag = int(success_flag) if success_flag is not None else (1 if sales_flag else 0)

        # Establish connection
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Parameterized insert
        query = """
            INSERT INTO chat_logs (timestamp, user_id, message, sender, intent, sales_flag, success_flag)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (timestamp, user_id, message, sender, intent, sales_flag, success_flag))
        connection.commit()

        print("✅ Chat logged successfully!")

    except mysql.connector.Error as e:
        print(f"❌ Error logging chat: {e}")

    except Exception as e:
        print(f"⚠️ General error: {e}")

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()


def get_or_create_user(name, email, phone):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user:
        cursor.close()
        conn.close()
        return user["id"]

    cursor.execute(
        "INSERT INTO users (name, email, phone) VALUES (%s, %s, %s)",
        (str(name), str(email), str(phone))
    )
    conn.commit()
    user_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return user_id

def log_conversation_node(convo_id, node_id, parent_id, user_id, message, sender,
                          topic=None, intent=None, sales_flag=False, success_flag=False):
    conn = get_connection()
    cursor = conn.cursor()

    # Cast all string fields to native Python str
    convo_id = str(convo_id)
    user_id = str(user_id)
    message = str(message)
    sender = str(sender)
    topic = str(topic) if topic is not None else None
    intent = str(intent) if intent is not None else None

    # Ensure booleans are native Python bool
    sales_flag = bool(sales_flag)
    success_flag = bool(success_flag)

    sql = """
    INSERT INTO conversation_nodes (
        convo_id, node_id, parent_id, user_id, message, sender,
        topic, intent, sales_flag, success_flag
    ) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        convo_id,
        node_id,
        parent_id if parent_id != 0 else None,
        user_id,
        message,
        sender,
        topic,
        intent,
        sales_flag,
        success_flag
    )

    try:
        print(values)  # Debug log
        cursor.execute(sql, values)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        cursor.close()
        conn.close()


    
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
