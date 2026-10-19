FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create models and data directories
RUN mkdir -p /app/models /app/data

# Copy backend application
COPY . .

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=5s --start-period=25s --retries=3 \
    CMD sh -c "curl -f http://localhost:\${PORT:-8000}/health || exit 1"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

