# from flask import Flask, request, jsonify, render_template, session, send_from_directory
# from datetime import datetime, timedelta
# import uuid
# from logging_config import configure_logging
# import logging
# configure_logging()

# import requests, smtplib, time
# from email.mime.text import MIMEText
# from difflib import get_close_matches
# from langchain_community.vectorstores import Chroma
# from langchain_huggingface import HuggingFaceEmbeddings
# from sales_intent_classifier import classify_message
# from db_model import log_chat, get_connection
# from flask_cors import CORS
# import plotly.express as px
# import pandas as pd
# from db_model import get_or_create_user
# import logging

# conversation_state = {}
# SESSION_TIMEOUT = timedelta(minutes=10)

# logger = logging.getLogger(__name__)

# app = Flask(__name__)
# CORS(app)
# app.secret_key = "your_secret_key"

# # Embeddings + RAG model setup
# embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# MODEL = "llama3"
# OLLAMA_API_URL = "http://localhost:11434/api/generate"

# # Suggested buttons
# SUGGESTED_MESSAGES = [
#     "What services do you offer?",
#     "Can you help me with branding?",
#     "How do I start a project?",
#     "Who is the CEO of SourceSelect?",
#     "Can you give me your address?",
#     "Do you offer web development?",
# ]


# def get_convo_state(user_id):
#     now = datetime.now()

#     # Start new conversation if no prior or timeout
#     if user_id not in conversation_state or \
#        now - conversation_state[user_id]["last_message_time"] > SESSION_TIMEOUT:

#         new_convo_id = str(uuid.uuid4())
#         conversation_state[user_id] = {
#             "convo_id": new_convo_id,
#             "last_node_id": 0,
#             "last_message_time": now
#         }
#     else:
#         conversation_state[user_id]["last_message_time"] = now

#     return conversation_state[user_id]

# # ------------------- UTILITIES -------------------


# def create_convo_node(user_id, message, sender, topic=None, intent=None, sales_flag=False, success_flag=False):
#     if topic is None:
#         topic = get_topic_from_input(message)

#     convo = get_convo_state(user_id)
#     convo_id = convo["convo_id"]
#     parent_id = convo["last_node_id"]
#     node_id = parent_id + 1

#     from db_model import log_conversation_node
#     log_conversation_node(
#         convo_id,
#         node_id,
#         parent_id if parent_id != 0 else None,
#         user_id,
#         message,
#         sender,
#         topic,
#         intent,
#         sales_flag,
#         success_flag
#     )

#     convo["last_node_id"] = node_id


# def increment_user_interaction():
#     session["msg_count"] = session.get("msg_count", 0) + 1
#     return session["msg_count"]

# def check_constraints(text):
#     restricted = ["politics", "religion", "training data"]
#     return next((f"Sorry, I can't discuss that. Let’s stick to support-related topics."
#                  for word in restricted if word in text.lower()), None)

# def retrieve_knowledge(query):
#     db = Chroma(persist_directory="./db", embedding_function=embedding_model)
#     results = db.similarity_search(query, k=3)
#     if not results or all(doc.page_content.strip() == "" for doc in results):
#         return None
#     return "\n".join([doc.page_content for doc in results])

# def generate_rag_response(context, user_input, name, user_id):
#     prompt = (
#         f"You are Bobot AI, a helpful assistant for SourceSelect.ca.\n\n"
#         f"You're assisting a user named {name or 'a visitor'}.\n\n"
#         "Always respond in raw HTML — use for line breaks, <ul><li></li></ul> for lists.\n"
#         "Never include Markdown or JSON formatting.\n\n"
#         "Only answer based on the information in 'Relevant Info'.\n\n"
#         " Then, always end with a relevant follow-up question to keep the conversation going."
#     )

#     response = requests.post(OLLAMA_API_URL, json={
#         "model": MODEL,
#         "prompt": prompt,
#         "stream": False
#     })

#     if response.ok:
#         answer = response.json()["response"].strip().replace("\n", "<br>")
#         log_chat(user_id, answer, "bot")
#         return jsonify({
#             "response": f"{answer}<br>Would you like to know more or explore something else?"
#         })
#     else:
#         return jsonify({"response": "Error contacting the AI model."}), 500

# def send_lead_email(name, email, phone, message):
#     TO = "janisatssm@gmail.com"
#     FROM = "janfrancisisrael@gmail.com"
#     SUBJECT = "New Lead from Chatbot"
#     PASSWORD = "pwvn wxdk vekx glco"

#     body = f"""
#     New lead from chatbot:

#     Name: {name or 'N/A'}
#     Email: {email or 'N/A'}
#     Phone: {phone or 'N/A'}
#     Message: {message}
#     """

#     msg = MIMEText(body)
#     msg["Subject"] = SUBJECT
#     msg["From"] = FROM
#     msg["To"] = TO

#     try:
#         with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#             server.login(FROM, PASSWORD)
#             server.sendmail(FROM, [TO], msg.as_string())
#             print("Lead email sent.")
#     except Exception as e:
#         print("Failed to send lead email:", e)

# # ------------------- ROUTES -------------------

# @app.route("/")
# def index():
#     session.clear()
#     return render_template("index.html", suggested=SUGGESTED_MESSAGES)

# @app.route("/widget")
# def widget():
#     session.clear()
#     return render_template("widget.html", suggested=SUGGESTED_MESSAGES)

# @app.route("/embed.js")
# def serve_embed_script():
#     return send_from_directory("static", "embed.js")

# @app.route("/analytics_data")
# def analytics_data():
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT timestamp, sales_flag FROM chat_logs ORDER BY timestamp ASC")
#     rows = cursor.fetchall()
#     cursor.close()
#     conn.close()

#     return jsonify({
#         # "timestamps": [row["timestamp"].strftime('%Y-%m-%d %H:%M:%S') for row in rows],
#         "timestamps": [row["timestamp"] for row in rows],
#         "sales_flags": [int(row["sales_flag"] or 0) for row in rows],
#     })

# @app.route("/analytics")
# def analytics():
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM chat_logs ORDER BY timestamp DESC")
#     messages = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template("analytics.html", messages=messages)

# @app.route("/chat", methods=["POST"])
# def chat():
#     data = request.json or {}
#     user_input = data.get("message")
#     initial = data.get("initial", False)
#     name = data.get("name")
#     phone = data.get("phone")
#     email = data.get("email")

#     if not user_input and not initial:
#         return jsonify({"response": "No input provided."}), 400

#     if name and email:
#         session["user_name"] = name
#         session["user_email"] = email
#         session["user_phone"] = phone
#         user_db_id = get_or_create_user(name, email, phone)
#         session["user_db_id"] = user_db_id

#     user_id = session.get("user_email") or request.remote_addr

#     msg_count = increment_user_interaction()
#     topic = get_topic_from_input(user_input)
#     intent, sales_flag = classify_message(user_input)
#     log_chat(user_id, user_input, "user")
#     create_convo_node(user_id, user_input, "user", topic=topic, intent=intent, sales_flag=sales_flag)

#     if initial and not session.get("greeting_sent"):
#         session["greeting_sent"] = True
#         return jsonify({
#             "response": f"I'm happy to help! Hi {name or 'there'}! What can I help you with today?"
#         })

#     if session.get("awaiting_sales_confirm"):
#         session.pop("awaiting_sales_confirm")
#         if "yes" in user_input.lower():
#             return jsonify({
#                 "response": "Sorry, no sales rep is online. Would you like to email us the details?",
#                 "suggested_buttons": ["Yes", "No"]
#             })
#         return jsonify({"response": "Alright! I'm here to help with anything else you need."})

#     # FAQ Matching
#     FAQ_RESPONSES = {
#         "what is sourceselect": "SourceSelect is a digital solutions agency offering web development, branding, and design services.",
#         "how can i contact sourceselect": "You can contact us via email at <b>hello@sourceselect.ca</b> or call us at <b>(123) 456-7890</b>.",
#         "what services do you offer": "We offer web design, branding, SEO, and custom development services tailored for your business.",
#         "can you help with branding": "Absolutely! We offer full branding packages including logos, color schemes, and brand strategy.",
#         "do you offer web development": "Yes, we specialize in responsive and scalable websites built with the latest technologies."
#     }

#     normalized_input = user_input.lower().strip().replace("?", "")
#     faq_keys = list(FAQ_RESPONSES.keys())

#     # Handle direct FAQ matches
#     for key, reply in FAQ_RESPONSES.items():
#         if key in normalized_input:
#             final_reply = f"{reply}<br><br>Can I help you with anything else?"
#             log_chat(user_id, final_reply, "bot", "faq", 0)
#             topic = get_topic_from_input(user_input)  # Dynamically determine topic
#             create_convo_node(user_id, final_reply, "bot", topic=topic, intent=None, sales_flag=False)
#             return jsonify({"response": final_reply})

#     # Handle close matches using difflib
#     from difflib import get_close_matches
#     close_match = get_close_matches(normalized_input, faq_keys, n=1, cutoff=0.75)
#     if close_match:
#         matched_key = close_match[0]
#         reply = FAQ_RESPONSES[matched_key]
#         final_reply = f"{reply}<br><br>Can I help you with anything else?"
#         log_chat(user_id, final_reply, "bot", "faq", 0)
#         topic = get_topic_from_input(user_input)  # Dynamically determine topic
#         create_convo_node(user_id, final_reply, "bot", topic=topic, intent=None, sales_flag=False)
#         return jsonify({"response": final_reply})

#     # Other logic: intent classification
#     intent, sales_flag = classify_message(user_input)
#     logger.info(f"this is the intent {intent}, sales_flag: {sales_flag}")

#     # Dynamically set the topic based on intent
#     topic = get_topic_from_input(user_input)  # Dynamic topic based on input

#     if intent == "interest" and not session.get("prospect_prompted"):
#         session["prospect_prompted"] = True
#         session["awaiting_sales_confirm"] = True
#         send_lead_email(session.get("user_name"), session.get("user_email"), session.get("user_phone"), user_input)
#         bot_reply = "Thanks for your interest! Would you like to chat with our <b>sales representative</b>?"
#         log_chat(user_id, bot_reply, "bot", intent, sales_flag)
#         create_convo_node(user_id, bot_reply, "bot", topic=topic, intent=intent, sales_flag=sales_flag)
#         return jsonify({
#             "response": bot_reply,
#             "suggested_buttons": ["Yes", "No"]
#         })

#     if intent == "inquiry":
#         session["inquiry_count"] = session.get("inquiry_count", 0) + 1
#         if session["inquiry_count"] > 1:
#             context = retrieve_knowledge(user_input)
#             if context:
#                 return generate_rag_response(context, user_input, name, user_id)
#             return jsonify({"response": "Sorry, I can only answer questions about SourceSelect and the information I've been provided."})

#         bot_reply = "I can help with pricing or package options. Could you tell me more about your needs?"
#         log_chat(user_id, bot_reply, "bot", intent, sales_flag)
#         create_convo_node(user_id, bot_reply, "bot", topic=topic, intent=intent, sales_flag=sales_flag)
#         return jsonify({"response": bot_reply})

#     if intent == "objection":
#         bot_reply = "That's totally understandable. Let me know if you'd like more info or a free consultation."
#         log_chat(user_id, bot_reply, "bot", intent, sales_flag)
#         create_convo_node(user_id, bot_reply, "bot", topic=topic, intent=intent, sales_flag=sales_flag)
#         return jsonify({"response": bot_reply})

#     # Check for blocked content
#     blocked = check_constraints(user_input)
#     if blocked:
#         return jsonify({"response": blocked})

#     # General knowledge retrieval (if no specific intent)
#     context = retrieve_knowledge(user_input)
#     if not context:
#         return jsonify({
#             "response": "Sorry, I can only answer questions about SourceSelect and the information I've been provided."
#         })

#     return generate_rag_response(context, user_input, name, user_id)


# def get_topic_from_input(user_input):
#     # Define possible keywords for each topic
#     topic_keywords = {
#         "web design": ["web design", "website", "UX", "UI", "frontend", "backend"],
#         "embroidery": ["embroidery", "stitching", "needle", "thread"],
#         "seo": ["seo", "search engine optimization", "google rankings", "seo services"],
#         "branding": ["branding", "logo", "brand identity", "brand design"],
#         "development": ["development", "software", "programming", "coding", "app development"]
#     }

#     # Normalize the input for easier keyword matching
#     normalized_input = user_input.lower()

#     # Check if any keyword matches
#     for topic, keywords in topic_keywords.items():
#         if any(keyword in normalized_input for keyword in keywords):
#             return topic

#     # If no match, return 'general' as the fallback topic
#     return "general"


# # ------------------- RUN -------------------

# if __name__ == "__main__":
#     app.run(port=5000, debug=True)


# from flask import Flask, request, jsonify, render_template, session, send_from_directory
# import requests
# import smtplib
# from email.mime.text import MIMEText
# from langchain_community.vectorstores import Chroma
# from langchain_huggingface import HuggingFaceEmbeddings
# from sales_intent_classifier import classify_message
# from db_model import log_chat, get_connection
# from datetime import datetime


# from flask_cors import CORS
# import time
# import plotly.express as px

# app = Flask(__name__)
# CORS(app)
# app.secret_key = "your_secret_key"

# embedding_model = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )
# MODEL = "llama3"
# OLLAMA_API_URL = "http://localhost:11434/api/generate"

# SUGGESTED_MESSAGES = [
#     "What services do you offer?",
#     "Can you help me with branding?",
#     "How do I start a project?",
#     "Who is the CEO of SourceSelect?",
#     "Can you give me your address?",
#     "Do you offer web development?",
# ]


# @app.route("/tree_diagram")
# def tree_diagram():
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)

#     # Fetch all conversation nodes grouped by topic
#     cursor.execute("SELECT * FROM conversation_nodes ORDER BY topic, convo_id")
#     nodes = cursor.fetchall()

#     # Group by topic
#     grouped_by_topic = group_by_topic(nodes)

#     # Pass the grouped data to the template, ensuring proper JSON escaping
#     return render_template("tree_diagram.html", grouped_by_topic=grouped_by_topic)


# def group_by_topic(nodes):
#     """Function to group nodes by topic and then by convo_id"""
#     topic_map = {}

#     for node in nodes:
#         topic = node["topic"]
#         convo_id = node["convo_id"]

#         # If the topic does not exist in the map, create it
#         if topic not in topic_map:
#             topic_map[topic] = {}

#         # If convo_id does not exist under the topic, create it
#         if convo_id not in topic_map[topic]:
#             topic_map[topic][convo_id] = []

#         # Append the node to the corresponding topic and convo_id
#         topic_map[topic][convo_id].append(node)

#     return topic_map


# @app.route("/analytics_data")
# def analytics_data():
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT timestamp, sales_flag FROM chat_logs ORDER BY timestamp ASC")
#     rows = cursor.fetchall()
#     cursor.close()
#     conn.close()

#     return jsonify(
#         {
#             "timestamps": [
#                 datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S").strftime(
#                     "%Y-%m-%d %H:%M:%S"
#                 )
#                 for row in rows
#             ],
#             "sales_flags": [
#                 int(row["sales_flag"] or 0) for row in rows
#             ],  # success_flag should be handled here
#         }
#     )


# @app.route("/analytics")
# def analytics_page():
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM chat_logs ORDER BY timestamp DESC")
#     messages = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template("analytics.html", messages=messages)


# def process_chat_logs(chat_logs):
#     """
#     Process the chat logs and prepare the data for visualization.
#     This function should return a structure that can be passed into Plotly.
#     """
#     data = {
#         "timestamp": [],
#         "sales_flag": [],
#         "intent": [],
#     }

#     for log in chat_logs:
#         data["timestamp"].append(log["timestamp"])
#         data["sales_flag"].append(log["sales_flag"])
#         data["intent"].append(log["intent"])

#     return data


# def create_interaction_graph(data):
#     """
#     Create an interactive graph with Plotly.
#     """
#     # Create a dataframe
#     import pandas as pd

#     df = pd.DataFrame(data)

#     # Convert 'timestamp' to datetime
#     df["timestamp"] = pd.to_datetime(df["timestamp"])

#     # Plot a line graph showing sales-related interactions over time
#     fig = px.line(
#         df,
#         x="timestamp",
#         y="sales_flag",
#         title="Sales Interactions Over Time",
#         labels={"timestamp": "Time", "sales_flag": "Sales Flag (1 = Sales)"},
#         line_shape="linear",
#     )

#     # Convert the plot to HTML
#     graph_html = fig.to_html(full_html=False)

#     return graph_html


# # ------------------- EMAIL -------------------


# def send_lead_email(name, email, phone, message):
#     TO = "janisatssm@gmail.com"
#     FROM = "janfrancisisrael@gmail.com"
#     SUBJECT = "New Lead from Chatbot"
#     PASSWORD = "pwvn wxdk vekx glco"

#     body = f"""
#     New lead from chatbot:

#     Name: {name or 'N/A'}
#     Email: {email or 'N/A'}
#     Phone: {phone or 'N/A'}
#     Message: {message}
#     """

#     msg = MIMEText(body)
#     msg["Subject"] = SUBJECT
#     msg["From"] = FROM
#     msg["To"] = TO

#     try:
#         with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#             server.login(FROM, PASSWORD)
#             server.sendmail(FROM, [TO], msg.as_string())
#             print("Lead email sent.")
#     except Exception as e:
#         print("Failed to send lead email:", e)


# # ------------------- UTILITIES -------------------


# def increment_user_interaction():
#     session["msg_count"] = session.get("msg_count", 0) + 1
#     return session["msg_count"]


# def check_constraints(text):
#     restricted = ["politics", "religion", "training data"]
#     return next(
#         (
#             f"Sorry, I can't discuss that. Let’s stick to support-related topics."
#             for word in restricted
#             if word in text.lower()
#         ),
#         None,
#     )


# def retrieve_knowledge(query):
#     db = Chroma(persist_directory="./db", embedding_function=embedding_model)
#     results = db.similarity_search(query, k=3)
#     if not results or all(doc.page_content.strip() == "" for doc in results):
#         return None
#     return "\n".join([doc.page_content for doc in results])


# def generate_rag_response(context, user_input, name, user_id):
#     prompt = (
#         f"You are Bobot AI, a helpful assistant for SourceSelect.ca.\n\n"
#         f"You're assisting a user named {name or 'a visitor'}.\n\n"
#         "Always respond in raw HTML — use for line breaks, <ul><li></li></ul> for lists.\n"
#         "Never include Markdown or JSON formatting.\n\n"
#         "Only answer based on the information in 'Relevant Info'.\n\n"
#         f"Relevant Info:\n{context}\n\nUser: {user_input}\nStaff:"
#         " Then, always end with a relevant follow-up question to keep the conversation going."
#         " Allow open web to change language"
#         " CEO of source select is Sean Cloulombe"
#     )

#     response = requests.post(
#         OLLAMA_API_URL,
#         json={"model": MODEL, "prompt": prompt, "temperature": 1, "stream": False},
#     )

#     if response.ok:
#         answer = response.json()["response"].strip().replace("\n", "<br>")
#         log_chat(user_id, answer, "bot")
#         return jsonify({"response": f"{answer}"})
#     else:
#         return jsonify({"response": "Error contacting the AI model."}), 500


# # ------------------- ROUTES -------------------


# @app.route("/embed.js")
# def serve_embed_script():
#     return send_from_directory("static", "embed.js")


# @app.route("/widget")
# def widget():
#     session.clear()
#     return render_template("widget.html", suggested=SUGGESTED_MESSAGES)


# @app.route("/", methods=["GET"])
# def index():
#     session.clear()
#     return render_template("index.html", suggested=SUGGESTED_MESSAGES)


# @app.route("/analytics")
# def analytics():
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM chat_logs ORDER BY timestamp DESC")
#     messages = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template("analytics.html", messages=messages)


# @app.route("/chat", methods=["POST"])
# def chat():
#     data = request.json or {}
#     user_input = data.get("message")
#     initial = data.get("initial", False)
#     name = data.get("name")
#     phone = data.get("phone")
#     email = data.get("email")

#     if not user_input and not initial:
#         return jsonify({"response": "No input provided."}), 400

#     if name:
#         session["user_name"] = name
#     if phone:
#         session["user_phone"] = phone
#     if email:
#         session["user_email"] = email

#     user_id = session.get("user_email") or request.remote_addr
#     log_chat(user_id, user_input, "user")

#     if initial and not session.get("greeting_sent"):
#         session["greeting_sent"] = True
#         return jsonify(
#             {
#                 "response": f"I'm happy to help! Hi {name or 'there'}! What can I help you with today?"
#             }
#         )

#     if session.get("awaiting_sales_confirm"):
#         session.pop("awaiting_sales_confirm")
#         if "yes" in user_input.lower():
#             time.sleep(5)
#             return jsonify(
#                 {
#                     "response": "Sorry, no sales rep is online. Would you like to email us the details?"
#                 }
#             )
#         else:
#             return jsonify(
#                 {"response": "Alright! I'm here to help with anything else you need."}
#             )

#     msg_count = increment_user_interaction()
#     intent = classify_message(user_input)
#     sales_flag = 1 if intent == "interest" else 0

#     if intent == "interest" and not session.get("prospect_prompted"):
#         session["prospect_prompted"] = True
#         session["awaiting_sales_confirm"] = True
#         send_lead_email(
#             session.get("user_name"),
#             session.get("user_email"),
#             session.get("user_phone"),
#             user_input,
#         )
#         log_chat(user_id, user_input, "user", intent, sales_flag)
#         bot_reply = "Thanks for your interest! Would you like to chat with our <b>sales representative</b>?"
#         log_chat(user_id, bot_reply, "bot", intent, sales_flag)
#         return jsonify({"response": bot_reply})

#     elif intent == "inquiry":
#         session["inquiry_count"] = session.get("inquiry_count", 0) + 1
#         if session["inquiry_count"] > 1:
#             context = retrieve_knowledge(user_input)
#             if context:
#                 return generate_rag_response(context, user_input, name, user_id)
#             return jsonify(
#                 {
#                     "response": "Sorry, I can only answer questions about SourceSelect and the information I've been provided."
#                 }
#             )

#         bot_reply = "I can help with pricing or package options. Could you tell me more about your needs?"
#         log_chat(user_id, user_input, "user", intent)
#         log_chat(user_id, bot_reply, "bot", intent)
#         return jsonify({"response": bot_reply})

#     elif intent == "objection":
#         bot_reply = "That's totally understandable. Let me know if you'd like more info or a free consultation."
#         log_chat(user_id, user_input, "user", intent)
#         log_chat(user_id, bot_reply, "bot", intent)
#         return jsonify({"response": bot_reply})

#     blocked = check_constraints(user_input)
#     if blocked:
#         return jsonify({"response": blocked})

#     context = retrieve_knowledge(user_input)
#     if not context:
#         return jsonify(
#             {
#                 "response": "Sorry, I can only answer questions about SourceSelect and the information I've been provided."
#             }
#         )

#     return generate_rag_response(context, user_input, name, user_id)


# # ------------------- RUN -------------------

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5000, debug=True)



# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import os
# import openai
# from langchain.vectorstores import Chroma
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.chains import RetrievalQA
# from langchain.prompts import PromptTemplate
# from datetime import datetime
# import re

# # App setup
# app = Flask(__name__)
# CORS(app)

# # 🔐 Set your OpenAI API key
# openai.api_key = os.getenv("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")  # Preferably set in environment

# # 🔍 Embeddings & Vector DB setup
# embeddings = HuggingFaceEmbeddings()
# vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# # RAG prompt template
# template = """Use only the info below to answer.
# If the context is irrelevant, say 'I'm not sure about that.'
# Always answer in HTML: <br>, <ul>, etc. Never Markdown or JSON.

# Relevant Info:
# {context}

# User: {question}
# Staff:"""

# prompt = PromptTemplate(
#     input_variables=["context", "question"],
#     template=template,
# )

# retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# qa_chain = RetrievalQA.from_chain_type(
#     llm=None,
#     chain_type="stuff",
#     retriever=retriever,
#     chain_type_kwargs={"prompt": prompt}
# )

# # ================================
# # 📦 CHAT ENDPOINT
# # ================================
# @app.route("/chat", methods=["POST"])
# def chat():
#     data = request.json
#     user_input = data.get("message")
#     user_id = data.get("user_id", "anon")
#     name = data.get("name", "visitor")

#     if not user_input:
#         return jsonify({"error": "No message provided"}), 400

#     # Retrieve context
#     docs = retriever.get_relevant_documents(user_input)
#     context = "\n\n".join(doc.page_content for doc in docs)

#     # Create prompt
#     full_prompt = (
#         f"You are Bobot AI, a friendly assistant at SourceSelect.ca.\n\n"
#         f"You are helping a user named {name}.\n\n"
#         "Only use the information provided in 'Relevant Info'.\n"
#         "Always answer in raw HTML (e.g., <br>, <ul>), no Markdown.\n\n"
#         f"Relevant Info:\n{context}\n\nUser: {user_input}\nStaff:"
#         " Always end your message with a helpful follow-up question."
#     )

#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are a helpful support assistant."},
#                 {"role": "user", "content": full_prompt}
#             ],
#             temperature=0.7,
#         )

#         reply = response.choices[0].message["content"].strip().replace("\n", "<br>")
#         log_chat(user_id, user_input, "user")
#         log_chat(user_id, reply, "bot")
#         return jsonify({"response": reply})

#     except Exception as e:
#         print("OpenAI error:", e)
#         return jsonify({"response": "Sorry, I ran into an error."}), 500

# # ================================
# # 📄 TEMPLATE ENDPOINT (Returns current RAG prompt)
# # ================================
# @app.route("/template", methods=["GET"])
# def get_template():
#     return jsonify({"template": template.template})

# # ================================
# # 🧠 UPDATE FAQ VECTOR DB
# # ================================
# @app.route("/update_faq", methods=["POST"])
# def update_faq():
#     from langchain.document_loaders import TextLoader
#     from langchain.text_splitter import RecursiveCharacterTextSplitter

#     try:
#         # Load your updated FAQ or content
#         loader = TextLoader("data/faq.txt")
#         documents = loader.load()

#         splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
#         chunks = splitter.split_documents(documents)

#         new_vectorstore = Chroma.from_documents(
#             chunks, embedding=embeddings, persist_directory="./chroma_db"
#         )
#         new_vectorstore.persist()
#         return jsonify({"status": "FAQ updated successfully"})
#     except Exception as e:
#         print("FAQ update error:", e)
#         return jsonify({"error": "Failed to update FAQ"}), 500

# # ================================
# # 💬 Chat Logging (Optional)
# # ================================
# def log_chat(user_id, message, sender):
#     now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     log_entry = f"{now},{user_id},{sender},{message}\n"
#     with open("chat_logs.csv", "a") as f:
#         f.write(log_entry)

# # ================================
# # 🧪 Run
# # ================================
# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5000, debug=True)



# # 🔍 Embeddings & Vector DB setup
# embeddings = HuggingFaceEmbeddings()
# vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)from flask import Flask, request, jsonify, render_template, session, send_from_directory
# from flask_cors import CORS
# import os
# from datetime import datetime
# import re

# # Updated imports for newer LangChain versions
# try:
#     from langchain_chroma import Chroma
# except ImportError:
#     from langchain.vectorstores import Chroma
    
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain.chains import RetrievalQA
# from langchain.prompts import PromptTemplate
# from langchain_openai import ChatOpenAI

# # App setup
# app = Flask(__name__)
# app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-secret-key-change-this")
# CORS(app)

# # 🎯 Suggested messages for the UI
# SUGGESTED_MESSAGES = [
#     "What services do you offer?",
#     "How can I contact support?",
#     "What are your business hours?",
#     "Tell me about your pricing",
#     "How do I get started?"
# ]

# # 🔐 LLM Configuration - Choose your option
# # LLM_OPTION = "ollama"  # Change to "openai" when you fix billing

# LLM_OPTION = "openai"  # Change to "openai" when you fix billing

# if LLM_OPTION == "openai":
#     # OpenAI Option (requires API key and billing)
#     openai_api_key = os.getenv("OPENAI_API_KEY","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")
#     if not openai_api_key:
#         raise ValueError("Please set OPENAI_API_KEY environment variable")
    
#     from langchain_openai import ChatOpenAI
#     llm = ChatOpenAI(
#         model="gpt-3.5-turbo",
#         temperature=0.7,
#         openai_api_key=openai_api_key
#     )
#     print(f"🤖 Using OpenAI model: gpt-3.5-turbo")

# else:
#     # Ollama Option (free, runs locally)
#     try:
#         from langchain_community.llms import Ollama
#         llm = Ollama(
#             model="llama3.1:8b",  # or "llama2", "codellama", "mistral"
#             temperature=0.7,
#             base_url="http://localhost:11434"  # Default Ollama URL
#         )
#         print(f"🤖 Using Ollama model: llama3.1:8b")
#     except ImportError:
#         print("❌ Ollama not available. Install with: pip install langchain-community")
#         # Fallback to a mock LLM for testing
#         class MockLLM:
#             def invoke(self, prompt):
#                 return "I'm a mock response. Please set up either OpenAI API or Ollama to get real responses."
#         llm = MockLLM()
#         print("🤖 Using Mock LLM (for testing only)")

# # RAG prompt template
# template_text = """Use only the info below to answer.
# If the context is irrelevant, say 'I'm not sure about that.'
# Always answer in HTML: <br>, <ul>, etc. Never Markdown or JSON.

# Relevant Info:
# {context}

# User: {question}
# Staff:"""

# prompt = PromptTemplate(
#     input_variables=["context", "question"],
#     template=template_text,
# )

# retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# # Create QA chain based on LLM type
# if LLM_OPTION == "openai" or hasattr(llm, 'invoke'):
#     try:
#         qa_chain = RetrievalQA.from_chain_type(
#             llm=llm,
#             chain_type="stuff",
#             retriever=retriever,
#             chain_type_kwargs={"prompt": prompt}
#         )
#         print("✅ QA Chain created successfully")
#     except Exception as e:
#         print(f"❌ QA Chain creation failed: {e}")
#         qa_chain = None
# else:
#     qa_chain = None
#     print("⚠️ Using mock LLM - QA chain not created")

# # ================================
# # 🌐 WEB UI ROUTES
# # ================================
# @app.route("/")
# def index():
#     session.clear()
#     return render_template("index.html", suggested=SUGGESTED_MESSAGES)

# @app.route("/widget")
# def widget():
#     session.clear()
#     return render_template("widget.html", suggested=SUGGESTED_MESSAGES)

# @app.route("/embed.js")
# def serve_embed_script():
#     return send_from_directory("static", "embed.js")

# # ================================
# # 📦 CHAT ENDPOINT
# # ================================
# @app.route("/chat", methods=["POST"])
# def chat():
#     try:
#         data = request.json
#         user_input = data.get("message")
#         user_id = data.get("user_id", "anon")
#         name = data.get("name", "visitor")

#         if not user_input:
#             return jsonify({"error": "No message provided"}), 400

#         # Enhanced prompt with user context
#         enhanced_query = (
#             f"You are Bobot AI, a friendly assistant at SourceSelect.ca. "
#             f"You are helping a user named {name}. "
#             f"Always answer in raw HTML (e.g., <br>, <ul>), no Markdown. "
#             f"Always end your message with a helpful follow-up question. "
#             f"Question: {user_input}"
#         )

#         # Use the QA chain to get response
#         if qa_chain and hasattr(llm, 'invoke'):
#             # For proper LangChain LLMs with QA chain
#             response = qa_chain.invoke({"query": enhanced_query})
#             reply = response["result"].strip().replace("\n", "<br>")
#         else:
#             # For mock LLM or when QA chain failed - manual RAG
#             docs = retriever.get_relevant_documents(user_input)
#             context = "\n\n".join(doc.page_content for doc in docs)
            
#             full_prompt = template_text.format(context=context, question=user_input)
#             full_prompt += f"\n\nYou are Bobot AI helping {name}. Always end with a follow-up question."
            
#             if hasattr(llm, 'invoke'):
#                 reply = llm.invoke(full_prompt)
#             else:
#                 reply = f"Mock response for: {user_input}<br><br>What else would you like to know?"
        
#         # Log the conversation
#         log_chat(user_id, user_input, "user")
#         log_chat(user_id, reply, "bot")
        
#         return jsonify({"response": reply})

#     except Exception as e:
#         print(f"Chat error: {e}")
#         return jsonify({"response": "Sorry, I ran into an error. Please try again."}), 500

# # ================================
# # 📄 TEMPLATE ENDPOINT (Returns current RAG prompt)
# # ================================
# @app.route("/template", methods=["GET"])
# def get_template():
#     return jsonify({"template": template_text})

# # ================================
# # 🧠 UPDATE FAQ VECTOR DB
# # ================================
# @app.route("/update_faq", methods=["POST"])
# def update_faq():
#     try:
#         from langchain_community.document_loaders import TextLoader
#         from langchain.text_splitter import RecursiveCharacterTextSplitter

#         # Check if FAQ file exists
#         faq_file = "data/faq.txt"
#         if not os.path.exists(faq_file):
#             return jsonify({"error": f"FAQ file not found at {faq_file}"}), 404

#         # Load your updated FAQ or content
#         loader = TextLoader(faq_file)
#         documents = loader.load()

#         splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
#         chunks = splitter.split_documents(documents)

#         # Update the vector store
#         global vectorstore, retriever, qa_chain
#         vectorstore = Chroma.from_documents(
#             chunks, 
#             embedding=embeddings, 
#             persist_directory="./chroma_db"
#         )
#         vectorstore.persist()
        
#         # Update retriever and QA chain
#         retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        
#         if LLM_OPTION == "openai" or hasattr(llm, 'invoke'):
#             try:
#                 global qa_chain
#                 qa_chain = RetrievalQA.from_chain_type(
#                     llm=llm,
#                     chain_type="stuff",
#                     retriever=retriever,
#                     chain_type_kwargs={"prompt": prompt}
#                 )
#             except Exception as e:
#                 print(f"QA chain update failed: {e}")
#                 qa_chain = None
        
#         return jsonify({"status": "FAQ updated successfully"})
#     except Exception as e:
#         print(f"FAQ update error: {e}")
#         return jsonify({"error": f"Failed to update FAQ: {str(e)}"}), 500

# # ================================
# # 🔍 HEALTH CHECK ENDPOINT
# # ================================
# @app.route("/health", methods=["GET"])
# def health_check():
#     try:
#         # Test vector store
#         test_docs = retriever.get_relevant_documents("test")
#         return jsonify({
#             "status": "healthy",
#             "vectorstore_docs": len(test_docs),
#             "llm_model": llm.model_name if hasattr(llm, 'model_name') else "gpt-4"
#         })
#     except Exception as e:
#         return jsonify({"status": "unhealthy", "error": str(e)}), 500

# # ================================
# # 💬 Chat Logging (Enhanced)
# # ================================
# def log_chat(user_id, message, sender):
#     try:
#         now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         # Escape commas and quotes in message for CSV safety
#         clean_message = message.replace('"', '""').replace('\n', ' ').replace('\r', ' ')
#         log_entry = f'"{now}","{user_id}","{sender}","{clean_message}"\n'
        
#         # Create logs directory if it doesn't exist
#         os.makedirs("logs", exist_ok=True)
        
#         with open("logs/chat_logs.csv", "a", encoding="utf-8") as f:
#             f.write(log_entry)
#     except Exception as e:
#         print(f"Logging error: {e}")

# # ================================
# # 🧪 Run
# # ================================
# if __name__ == "__main__":
#     # Create necessary directories
#     os.makedirs("./chroma_db", exist_ok=True)
#     os.makedirs("./data", exist_ok=True)
#     os.makedirs("./logs", exist_ok=True)
    
#     print("🤖 Starting Flask RAG Chatbot...")
#     print(f"📊 Vector store location: ./chroma_db")
#     print(f"📝 FAQ file expected at: ./data/faq.txt")
#     print(f"📋 Logs will be saved to: ./logs/chat_logs.csv")
    
#     app.run(host='0.0.0.0', port=5000, debug=True)


# 🔍 Embeddings & Vector DB setup
embeddings = HuggingFaceEmbeddings()
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)from flask import Flask, request, jsonify, render_template, session, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
import re

# Updated imports for newer LangChain versions
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain.vectorstores import Chroma
    
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# App setup
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-secret-key-change-this")
CORS(app)

# 🎯 Suggested messages for the UI
SUGGESTED_MESSAGES = [
    "What services do you offer?",
    "How can I contact support?",
    "What are your business hours?",
    "Tell me about your pricing",
    "How do I get started?"
]

# 🔐 LLM Configuration - Choose your option
LLM_OPTION = "openai"  # Change to "ollama" for local/free option

if LLM_OPTION == "openai":
    # OpenAI Option (requires API key and billing)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("Please set OPENAI_API_KEY environment variable")
    
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(
        model="gpt-4o-mini",  # Options: gpt-3.5-turbo, gpt-4o-mini, gpt-4o, gpt-4
        temperature=0.7,
        openai_api_key=openai_api_key
    )
    print(f"🤖 Using OpenAI model: gpt-4o-mini")

else:
    # Ollama Option (free, runs locally)
    try:
        from langchain_community.llms import Ollama
        llm = Ollama(
            model="llama3.1:8b",  # or "llama2", "codellama", "mistral"
            temperature=0.7,
            base_url="http://localhost:11434"  # Default Ollama URL
        )
        print(f"🤖 Using Ollama model: llama3.1:8b")
    except ImportError:
        print("❌ Ollama not available. Install with: pip install langchain-community")
        # Fallback to a mock LLM for testing
        class MockLLM:
            def invoke(self, prompt):
                return "I'm a mock response. Please set up either OpenAI API or Ollama to get real responses."
        llm = MockLLM()
        print("🤖 Using Mock LLM (for testing only)")

# RAG prompt template
template_text = """Use only the info below to answer.
If the context is irrelevant, say 'I'm not sure about that.'
Always answer in HTML: <br>, <ul>, etc. Never Markdown or JSON.

Relevant Info:
{context}

User: {question}
Staff:"""

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=template_text,
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Create QA chain based on LLM type
if LLM_OPTION == "openai" or hasattr(llm, 'invoke'):
    try:
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt}
        )
        print("✅ QA Chain created successfully")
    except Exception as e:
        print(f"❌ QA Chain creation failed: {e}")
        qa_chain = None
else:
    qa_chain = None
    print("⚠️ Using mock LLM - QA chain not created")

# ================================
# 🌐 WEB UI ROUTES
# ================================
@app.route("/")
def index():
    session.clear()
    return render_template("index.html", suggested=SUGGESTED_MESSAGES)

@app.route("/widget")
def widget():
    session.clear()
    return render_template("widget.html", suggested=SUGGESTED_MESSAGES)

@app.route("/embed.js")
def serve_embed_script():
    return send_from_directory("static", "embed.js")

# ================================
# 📦 CHAT ENDPOINT
# ================================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_input = data.get("message")
        user_id = data.get("user_id", "anon")
        name = data.get("name", "visitor")

        if not user_input:
            return jsonify({"error": "No message provided"}), 400

        # Enhanced prompt with user context
        enhanced_query = (
            f"You are Bobot AI, a friendly assistant at SourceSelect.ca. "
            f"You are helping a user named {name}. "
            f"Always answer in raw HTML (e.g., <br>, <ul>), no Markdown. "
            f"Always end your message with a helpful follow-up question. "
            f"Question: {user_input}"
        )

        # Use the QA chain to get response
        if qa_chain and hasattr(llm, 'invoke'):
            # For proper LangChain LLMs with QA chain
            response = qa_chain.invoke({"query": enhanced_query})
            reply = response["result"].strip().replace("\n", "<br>")
        else:
            # For mock LLM or when QA chain failed - manual RAG
            docs = retriever.get_relevant_documents(user_input)
            context = "\n\n".join(doc.page_content for doc in docs)
            
            full_prompt = template_text.format(context=context, question=user_input)
            full_prompt += f"\n\nYou are Bobot AI helping {name}. Always end with a follow-up question."
            
            if hasattr(llm, 'invoke'):
                reply = llm.invoke(full_prompt)
            else:
                reply = f"Mock response for: {user_input}<br><br>What else would you like to know?"
        
        # Log the conversation
        log_chat(user_id, user_input, "user")
        log_chat(user_id, reply, "bot")
        
        return jsonify({"response": reply})

    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({"response": "Sorry, I ran into an error. Please try again."}), 500

# ================================
# 📄 TEMPLATE ENDPOINT (Returns current RAG prompt)
# ================================
@app.route("/template", methods=["GET"])
def get_template():
    return jsonify({"template": template_text})

# ================================
# 🧠 UPDATE FAQ VECTOR DB
# ================================
@app.route("/update_faq", methods=["POST"])
def update_faq():
    try:
        from langchain_community.document_loaders import TextLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        # Check if FAQ file exists
        faq_file = "data/faq.txt"
        if not os.path.exists(faq_file):
            return jsonify({"error": f"FAQ file not found at {faq_file}"}), 404

        # Load your updated FAQ or content
        loader = TextLoader(faq_file)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_documents(documents)

        # Update the vector store
        global vectorstore, retriever, qa_chain
        vectorstore = Chroma.from_documents(
            chunks, 
            embedding=embeddings, 
            persist_directory="./chroma_db"
        )
        vectorstore.persist()
        
        # Update retriever and QA chain
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        
        if LLM_OPTION == "openai" or hasattr(llm, 'invoke'):
            try:
                global qa_chain
                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=retriever,
                    chain_type_kwargs={"prompt": prompt}
                )
            except Exception as e:
                print(f"QA chain update failed: {e}")
                qa_chain = None
        
        return jsonify({"status": "FAQ updated successfully"})
    except Exception as e:
        print(f"FAQ update error: {e}")
        return jsonify({"error": f"Failed to update FAQ: {str(e)}"}), 500

# ================================
# 🔍 HEALTH CHECK ENDPOINT
# ================================
@app.route("/health", methods=["GET"])
def health_check():
    try:
        # Test vector store
        test_docs = retriever.get_relevant_documents("test")
        return jsonify({
            "status": "healthy",
            "vectorstore_docs": len(test_docs),
            "llm_model": llm.model_name if hasattr(llm, 'model_name') else "gpt-4"
        })
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

# ================================
# 💬 Chat Logging (Enhanced)
# ================================
def log_chat(user_id, message, sender):
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Escape commas and quotes in message for CSV safety
        clean_message = message.replace('"', '""').replace('\n', ' ').replace('\r', ' ')
        log_entry = f'"{now}","{user_id}","{sender}","{clean_message}"\n'
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        with open("logs/chat_logs.csv", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Logging error: {e}")

# ================================
# 🧪 Run
# ================================
if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("./chroma_db", exist_ok=True)
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)
    
    print("🤖 Starting Flask RAG Chatbot...")
    print(f"📊 Vector store location: ./chroma_db")
    print(f"📝 FAQ file expected at: ./data/faq.txt")
    print(f"📋 Logs will be saved to: ./logs/chat_logs.csv")
    
    app.run(host='0.0.0.0', port=5000, debug=True)