FROM python:3.11-slim
WORKDIR /app
RUN pip install requests
COPY capture.py .
CMD ["python", "capture.py"]
