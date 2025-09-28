FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn requests
COPY parser.py .
CMD ["uvicorn", "parser:app", "--host", "0.0.0.0", "--port", "8001"]
