import requests
import os
from   dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
ENDPOINT_ID    = os.getenv("ENDPOINT_ID")
if not RUNPOD_API_KEY:
    raise ValueError("API key not found! Ensure RUNPOD_API_KEY is set in the .env file.")
if not ENDPOINT_ID:
    raise ValueError("Endpoint ID not found! Ensure ENDPOINT_ID is set in the .env file.")

# Set application options
DEBUG = False
N_CTX = 8192
MAX_CONTEXT_SIZE = 8192 * 4  # Assuming ~4 characters per token on average
SUMMARY_TRIGGER_SIZE = MAX_CONTEXT_SIZE // 2  # Trigger summarization when history exceeds half the limit

# System message to define the chatbot's persona
SYSTEM_MESSAGE = "You are a helpful, polite, and knowledgeable assistant. Always respond with clarity and detail. Honestly say you don't know if you are unsure of the answer, do not make things up."

# Define Runpod API Endpoint
url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync"

# Define Runpod API Key
api_key = RUNPOD_API_KEY

# Headers for the request
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Function to summarize old messages
def summarize_history(history, summarization_prompt="Summarize the following conversation:"):
    # Prepare the payload for summarizing old messages
    payload = {
        "input": {
            "method_name": "generate",
            "input": {
                "prompt": f"{summarization_prompt}\n\n" + "\n".join(history),
                "num_ctx": N_CTX,
            }
        }
    }

    # Send the request to summarize
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("output", {}).get("response", "Failed to summarize history.")
    except requests.exceptions.RequestException as e:
        return f"Error summarizing history: {e}"

# Function to manage hierarchical memory
def manage_memory(conversation_history, long_term_memory):
    total_size = sum(len(msg) + 1 for msg in conversation_history)  # +1 for newlines

    # If the total size exceeds the summarization trigger, summarize older messages
    if total_size > SUMMARY_TRIGGER_SIZE:
        old_history = conversation_history[:-10]  # All except the last 10 messages
        recent_history = conversation_history[-10:]  # Last 10 messages to keep detail
        summary = summarize_history(old_history)
        long_term_memory.append(f"Summary of earlier conversation: {summary}")
        conversation_history = recent_history

    # Combine long-term memory and short-term memory (recent messages)
    combined_history = [SYSTEM_MESSAGE] + long_term_memory + conversation_history

    # Truncate to fit within the maximum context size
    truncated_history = []
    current_size = 0
    for message in reversed(combined_history):
        message_size = len(message)
        if current_size + message_size + 1 > MAX_CONTEXT_SIZE:
            break
        truncated_history.insert(0, message)  # Prepend to maintain order
        current_size += message_size + 1

    return truncated_history, long_term_memory

# Function to send the conversation history and get a response
def send_message_to_model(conversation_history, long_term_memory):
    # Manage hierarchical memory
    truncated_history, long_term_memory = manage_memory(conversation_history, long_term_memory)

    # Define the payload for the request
    payload = {
        "input": {
            "method_name": "generate",
            "input": {
                "prompt": "\n".join(truncated_history),
                "num_ctx": N_CTX,
            }
        }
    }

    # Send the POST request
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("output", {}).get("response", "No response found."), long_term_memory
    except requests.exceptions.RequestException as e:
        return f"Error communicating with the model: {e}", long_term_memory

# Main chatbot function
def chat():
    print("Chatbot: Hello! I am your AI assistant. How may I help you today?\nType 'exit' or 'bye' to quit.\n")

    # Conversation history (short-term memory) and long-term memory
    conversation_history = ["Chatbot: Hello! I am your AI assistant. How may I help you today?"]
    long_term_memory = []

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Chatbot: Goodbye!")
            break

        # Add the user's input to the conversation history
        conversation_history.append(f"You: {user_input}")

        # Send the managed conversation history and long-term memory to the model
        response, long_term_memory = send_message_to_model(conversation_history, long_term_memory)
        print(f"\nChatbot: {response}\n")

        # Add the chatbot's response to the conversation history
        conversation_history.append(f"Chatbot: {response}")

if __name__ == "__main__":
    chat()