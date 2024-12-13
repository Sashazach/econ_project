# Use the official lightweight Python image
FROM python:3.9-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system and gevent dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev libssl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home appuser

# Set the working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Change ownership of the application directory
RUN chown -R appuser /app

# Switch to the non-root user
USER appuser

# Start the application using Gunicorn, binding to the PORT environment variable
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 3 --threads 2 --timeout 200 index:app"]
