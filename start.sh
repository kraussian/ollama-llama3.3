#!/bin/bash

# Kill any existing Ollama process
pgrep ollama | xargs kill -9 2>/dev/null || true

# Start the Ollama server
ollama serve >ollama.server.log 2>&1 &
OllamaPID=$!

# Check if the server is running
check_server_is_running() {
    tail -n 20 ollama.server.log | grep -q "Listening"
}

echo "Starting Ollama server..."
while ! check_server_is_running; do
    echo "Waiting for Ollama server to start..."
    sleep 2
done
echo "Ollama server is running."

# Pull the model (if not already pulled)
ollama pull $1 || exit 1

# Run the Python wrapper
python3 -u runpod_wrapper.py $1
