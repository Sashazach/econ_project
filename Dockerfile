FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV PORT=8080

# Expose the Cloud Run port
EXPOSE 8080

# Run the Flask app with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "index:app"]
