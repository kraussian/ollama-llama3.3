# Build with: docker build -t ollama-llama3.3 .
# Tag with: docker tag ollama-llama3.3 kraussian/ollama-llama3.3:latest
# Run with: docker run -d --gpus=all -p 15251:15251 --name ollama-llama kraussian/ollama-llama3.3
# Push with: docker push kraussian/ollama-llama3.3:latest
# Test on localhost with:
#curl -X POST http://localhost:15251/api/chat -H "Content-Type: application/json" -d '{
#    "model": "llama3.3",
#    "messages": [{"role": "user", "content": "Why is the sky blue?"}],
#    "stream": false
#}'

# Download latest Ollama image
FROM ollama/ollama:latest

# Set environment variables
ENV PYTHONUNBUFFERED=1 
ENV DEBIAN_FRONTEND=noninteractive

# Change Ollama's default host and port
ENV OLLAMA_HOST=0.0.0.0:15251

# Set up the working directory
WORKDIR /

# Install necessary dependencies for building Python from source
RUN apt update && apt install -y --no-install-recommends \
    build-essential wget git curl unzip cmake software-properties-common \
    zlib1g-dev libffi-dev libssl-dev libbz2-dev libreadline-dev libsqlite3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Download and build Python 3.12 from source
RUN wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz \
    && tar -xzf Python-3.12.0.tgz \
    && cd Python-3.12.0 \
    && ./configure --enable-optimizations \
    && make -j$(nproc) \
    && make altinstall \
    && cd .. \
    && rm -rf Python-3.12.0 Python-3.12.0.tgz

# Update alternatives to use Python 3.12 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.12 1 \
    && update-alternatives --set python3 /usr/local/bin/python3.12 \
    && ln -sf /usr/local/bin/python3.12 /usr/bin/python

# Update pip and setuptools
RUN python3 -m ensurepip && python3 -m pip install --upgrade pip setuptools wheel

# Install Runpod Python module
RUN pip install runpod

# Copy starting script
COPY start.sh .

# Copy Runpod wrapper script
COPY runpod_wrapper.py .

# Override Ollama's entrypoint
ENTRYPOINT ["bash", "start.sh"]

# Pull Llama 3.3 model
CMD ["llama3.3"]
