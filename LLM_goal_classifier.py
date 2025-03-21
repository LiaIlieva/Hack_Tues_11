

# Sample input texts to test the model
# sample_texts = [
#     "I want to lose weight and burn fat quickly.",
#     "I need to build muscle and increase my strength.",
#     "I want to maintain my current weight and stay healthy.",
#     "What should I do to gain more muscle mass?",
#     "How can I reduce my body fat percentage?",
#     "I wanna drive a car.",  # Unrelated input
#     "What's the weather like today?",  # Unrelated input
#     "I love playing video games."  # Unrelated input
# ]

# Test the model on the sample texts
# for text in sample_texts:
#     result = classifier(text, candidate_labels=labels)
#     predicted_label = result['labels'][0]
#     confidence = result['scores'][0]

#     # Check if the confidence is below the threshold
#     if confidence < confidence_threshold:
#         predicted_label = "unrelated"

#     print(f"Text: {text}")
#     print(f"Predicted Label: {predicted_label} (Confidence: {confidence:.4f})\n")

def get_goal(text):
    from transformers import pipeline

    # Load a zero-shot classification model
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    # Define your custom labels
    labels = ["fat loss", "muscle gain", "maintain weight"]

    # Define a confidence threshold for unrelated inputs
    confidence_threshold = 0.5  # Adjust this value as needed
    result = classifier(text, candidate_labels=labels)
    predicted_label = result['labels'][0]
    confidence = result['scores'][0]

    # Check if the confidence is below the threshold
    if confidence < confidence_threshold:
        return None  # Return None if the input is unrelated

    # Replace spaces with underscores to match the database schema
    predicted_label = predicted_label.replace(" ", "_")

    print(f"Text: {text}")
    print(f"Predicted Label: {predicted_label} (Confidence: {confidence:.4f})\n")

    return predicted_label