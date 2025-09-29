FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Scapy
RUN apt-get update && apt-get install -y \
    tcpdump \
    iproute2 \
    iputils-ping \
    gcc \
    libpcap-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir scapy requests

# Copy script
COPY capture.py .

# Default command
CMD ["python", "capture.py", "-i", "eth0"]
