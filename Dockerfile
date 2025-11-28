# Use official Python image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    unzip \
    build-essential

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# ------------------------------
# Install Whisper binary safely
# ------------------------------

WORKDIR /whisper

# Download ZIP instead of tar.gz (safe & works on Render)
RUN curl -L -o whisper.zip \
    https://huggingface.co/ggerganov/whisper.cpp/resolve/main/whisper-linux-x64.zip \
    && unzip whisper.zip -d whisper_bin \
    && chmod +x whisper_bin/*

# Return to app directory
WORKDIR /app

# Copy app files
COPY . /app

# Expose port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
