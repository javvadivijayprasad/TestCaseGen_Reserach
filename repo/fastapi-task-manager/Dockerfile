# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

# Expose port 8000
EXPOSE 8000

# Command to run the application in production mode
CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]