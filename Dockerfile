FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY pyproject.toml .
RUN pip install --no-cache-dir ".[server]"

# Copy source
COPY autoreadme/ autoreadme/

EXPOSE 8080

CMD ["uvicorn", "autoreadme.github_app.webhook_server:app", "--host", "0.0.0.0", "--port", "8080"]
