FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn psycopg2-binary
COPY analyzer.py .
CMD ["uvicorn", "analyzer:app", "--host", "0.0.0.0", "--port", "8003"]
