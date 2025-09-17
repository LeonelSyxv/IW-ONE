# Official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-tk \
    python3-dev \
    gcc \
    make \
    libx11-6 \
    libx11-dev \
    libxtst6 \
    libxtst-dev \
    libpng-dev \
    libjpeg-dev \
    libtiff5-dev \
    libxext6 \
    libsm6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Run the main script when the container starts
CMD ["python", "main.py"]
