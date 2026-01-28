# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (for some Python packages and Playwright)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies (PIP_ROOT_USER_ACTION=ignore silences "Running pip as root" warning)
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium && \
    playwright install-deps chromium

# Copy application code
COPY . .

# Expose port (Cloud Run sets PORT env var automatically)
EXPOSE 8080

# Set environment variable for production
ENV PYTHONUNBUFFERED=1

# Run the application
# Cloud Run sets PORT environment variable automatically
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1
