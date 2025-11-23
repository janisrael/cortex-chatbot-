from sales_intent_classifier import classify_message

print(classify_message("How much is your service?"))  # → inquiry
print(classify_message("Let's work together"))        # → interest
print(classify_message("That’s expensive"))           # → objection