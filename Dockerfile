# Use the official lightweight Python image.
FROM python:3.9-slim

# Set environment variables for Python.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies.
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user.
RUN useradd --create-home appuser

# Set the working directory.
WORKDIR /app

# Copy only the requirements file to leverage Docker cache.
COPY requirements.txt .

# Install Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY . .

# Change ownership of the application directory.
RUN chown -R appuser /app

# Switch to the non-root user.
USER appuser

# Expose the port (Cloud Run uses the PORT environment variable, default is 8080).
ENV PORT=8080
EXPOSE 8080

# Start the application using Gunicorn, binding to all network interfaces.
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 3 --threads 2 --timeout 120 index:app
