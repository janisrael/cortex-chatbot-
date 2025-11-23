import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib
import os
import logging

logger = logging.getLogger(__name__)

MODEL_PATH = "sales_classifier.joblib"
CSV_PATH = '/home/jan-israel/dev/chatbot/ollama_rag_chatbot/data/convo_data.csv'

# ========== 1. Load CSV Training Data ==========
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"Training data not found at {CSV_PATH}")

df = pd.read_csv(CSV_PATH)

# Ensure the 'sales_flag' column exists
if 'sales_flag' not in df.columns:
    raise KeyError("The 'sales_flag' column is missing in the CSV file.")

# Extract texts and labels from the CSV
texts = df["message"].astype(str).tolist()
labels = df["sales_flag"].astype(str).tolist()

# ========== 2. Define Sales Keywords ==========
sales_keywords_interest = [
    "I'm interested", "Can I hire you?", "Let's collaborate", "I need your service", 
    "I'm ready to get started", "I'd love to discuss this", "We want to work with you", 
    "Can we start this week?", "Let’s set up a call", "Do you take new clients?", 
    "Looking for your help", "We need your expertise", "I want to move forward", 
    "Can we begin soon?", "I’m ready to commit", "We’re interested", "Can we partner up?", 
    "Looking forward to this", "We’d like to get started", "I’m excited to begin", 
    "I want to book your service", "I'm planning a project with you", "We’re ready to proceed", 
    "Please send a proposal", "Let’s sign a contract", "You’re the one I need", 
    "We chose you", "Can we work with your team?", "When can we begin?", 
    "Let’s talk about next steps", "I’ll go with your service", "Let’s lock this in", 
    "I want to reserve a spot", "How do we get started?", "I want to confirm this deal"
]

sales_keywords_inquiry = [
    "How much does it cost?", "What’s your rate?", "Do you offer payment plans?", 
    "How long does the project take?", "Can I get a quote?", "What’s included in your service?", 
    "How do you charge?", "Is there a discount for bulk?", "Can you break down the pricing?", 
    "Are there any hidden fees?", "Do you accept credit card?", "What’s your refund policy?", 
    "Do you have a service brochure?", "What’s your availability?", "Is there an hourly rate?", 
    "Do you charge per project?", "Can you send pricing details?", "Do you offer packages?", 
    "How do you invoice?", "Is the consultation free?", "What are the deliverables?", 
    "Do you offer maintenance?", "Can you do a demo?", "What’s your turnaround time?", 
    "Do you offer revisions?", "Are there extra charges?", "Do you work weekends?", 
    "Do you travel for work?", "Can I get a custom quote?", "What tools do you use?", 
    "Is support included?", "What’s the next step?", "Do you do contracts?", 
    "What payment methods are accepted?", "How soon can you start?"
]

sales_keywords_objection = [
    "That’s too expensive", "I’ll think about it", "Let me get back to you", 
    "It’s not in the budget", "I have to ask my partner", "We’re not ready yet", 
    "Maybe next time", "It’s a bit costly", "I need to consider other options", 
    "We already have a vendor", "We’re going in a different direction", "I’m not sure we need this", 
    "I’m not convinced", "This doesn’t fit our needs", "We’ll pass for now", 
    "I’m not the decision maker", "Can you lower the price?", "It’s more than we expected", 
    "We need more time", "That’s above our budget", "Can you match another quote?", 
    "We’re comparing offers", "Seems overpriced", "Is there a cheaper option?", 
    "I’ll have to delay", "Timing isn’t right", "It’s too soon", "We’re holding off for now", 
    "Do you offer a trial?", "What if we’re not happy?"
]

# ========== 3. Merge Sales Keywords into Training Data ==========
training_data = [
    # Interest Keywords
    *[(text, "interest") for text in sales_keywords_interest],
    
    # Inquiry Keywords
    *[(text, "inquiry") for text in sales_keywords_inquiry],
    
    # Objection Keywords
    *[(text, "objection") for text in sales_keywords_objection],
    
    # Original data from CSV
    *[(text, label) for text, label in zip(texts, labels)],
]

# Prepare and train the model
texts, labels = zip(*training_data)
model = make_pipeline(CountVectorizer(), MultinomialNB())
model.fit(texts, labels)

# Save the trained model
joblib.dump(model, MODEL_PATH)

# ========== 4. Classifier Function with Sales Intent ==========
def classify_message(message):
    """Classifies the message into one of the sales intents"""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Classifier model not found at {MODEL_PATH}")
    
    clf = joblib.load(MODEL_PATH)
    label = clf.predict([message])[0]

    # Sales flag indicates if the label is 'interest', 'inquiry', or 'objection'
    sales_flag = 1 if label in ["interest", "inquiry", "objection"] else 0

    logger.info(f"flag and label {label}")
    return label, sales_flag
