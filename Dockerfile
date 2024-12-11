# Use the official Python image.
FROM python:3.9-slim

# Set the working directory.
WORKDIR /app

# Copy project files into the container.
COPY . /app

# Install dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask runs on.
EXPOSE 8080

# Set environment variables for Flask.
ENV FLASK_APP=index.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Run Flask.
CMD ["flask", "run", "--port=8080"]
