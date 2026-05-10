# ----------------------------- 
# PyTorch 2.5.1 + CUDA 12.1 (runtime) 
# ----------------------------- 
FROM pytorch/pytorch:2.5.1-cuda12.1-cudnn9-runtime 
 
# Environment variables 
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1 
 
# Set working directory 
WORKDIR /app 
 
# Install system tools 
RUN apt-get update && apt-get install -y \ 
    git \ 
    build-essential \ 
    && rm -rf /var/lib/apt/lists/* 
 
# Copy requirements first (for Docker cache) 
COPY requirements.txt . 
 
# Upgrade pip + install with wheels 
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt \
    --index-url https://pypi.org/simple 
 
# Copy project files 
COPY . . 
 
# Expose Flask port 
EXPOSE 5000 
 
# Run Flask app 
CMD ["python", "app.py"]