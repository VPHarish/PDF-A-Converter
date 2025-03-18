FROM ubuntu:latest

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    ghostscript \
    libleptonica-dev \
    icc-profiles-free \
    qpdf \
    unpaper \
    pngquant \
    zlib1g-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload and output directories
RUN mkdir -p uploads outputs && \
    chmod -R 777 uploads outputs

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]