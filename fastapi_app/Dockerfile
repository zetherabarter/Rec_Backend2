# FINAL FIX - Dockerfile with perfectly compatible MongoDB stack
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip==22.3.1 \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE $PORT

# Run with uvicorn using shell form for environment variable expansion
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
