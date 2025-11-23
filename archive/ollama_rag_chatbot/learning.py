import os
from db_model import get_connection
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from datetime import datetime
import re

# Get the current working directory (the folder where the script is located)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
# GRANDPARENT_DIR = os.path.dirname(PARENT_DIR)
# Define the path for db/ollama_rag_chatbot directory
VECTORSTORE_DIR = os.path.join(PARENT_DIR, "db")
print(f"Directoryxxxx {VECTORSTORE_DIR} created.")
# Create the directory if it doesn't exist
if not os.path.exists(VECTORSTORE_DIR):
    os.makedirs(VECTORSTORE_DIR)
  

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def fetch_unsuccessful_sales():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM chat_logs
        WHERE sales_flag = 1 AND (success_flag = 0 OR success_flag IS NULL)
        ORDER BY timestamp ASC
    """)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def clean_text(text):
    text = re.sub(r"<.*?>", "", text)  # remove HTML tags
    return text.strip()

def build_qa_pairs(logs):
    qa_pairs = []
    grouped = {}

    for entry in logs:
        user_id = entry['user_id']
        grouped.setdefault(user_id, []).append(entry)

    for conv in grouped.values():
        for i in range(len(conv)-1):
            if conv[i]["sender"] == "user" and conv[i+1]["sender"] == "bot":
                question = clean_text(conv[i]["message"])
                answer = clean_text(conv[i+1]["message"])
                if question and answer:
                    qa_pairs.append((question, answer))
    return qa_pairs

def add_to_vectorstore(qa_pairs):
    # Use the dynamic path for the vector store
    db = Chroma(persist_directory=VECTORSTORE_DIR, embedding_function=embedding_model)
    for question, answer in qa_pairs:
        doc = f"Q: {question}\nA: {answer}"
        db.add_texts([doc])
    print(f"✅ Added {len(qa_pairs)} Q&A pairs to vector store.")

def main():
    logs = fetch_unsuccessful_sales()
    if not logs:
        print("No new logs to learn from.")
        return
    qa_pairs = build_qa_pairs(logs)
    add_to_vectorstore(qa_pairs)

if __name__ == "__main__":
    main()
