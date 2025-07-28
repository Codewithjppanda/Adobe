# Use official Python runtime with AMD64 architecture
FROM --platform=linux/amd64 python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for pdfminer
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY process_pdfs.py .

# Create input and output directories (optional but good practice)
RUN mkdir -p /app/input /app/output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Run the main script
CMD ["python", "process_pdfs.py"]
