# Use the official Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies required by moviepy, opencv, ffmpeg, and yt-dlp
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create necessary runtime directories
RUN mkdir -p uploads videos downloads output

# Expose the port Streamlit runs on (Render injects $PORT at runtime)
EXPOSE 8501

# Run Streamlit — honour $PORT if Render provides it, fall back to 8501
CMD streamlit run src/app.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
