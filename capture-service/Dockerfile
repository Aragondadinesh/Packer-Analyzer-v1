FROM python:3.11-slim
WORKDIR /app
COPY capture.py .
RUN apt-get update && apt-get install -y tcpdump && \
    pip install scapy requests
CMD ["python", "capture.py"]
