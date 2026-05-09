# --- Stage 1: Build & Dependencies ---
FROM python:3.11-slim as builder

WORKDIR /build

# Install system dependencies for common AI libraries (e.g., psycopg2, C extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies into a local folder
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# --- Stage 2: Final Runtime ---
FROM python:3.11-slim

WORKDIR /app

# Copy only the installed python packages from the builder stage
COPY --from=builder /root/.local /root/.local
COPY --from=builder /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu

# Ensure the local bin is in the PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Copy the application code
COPY app/ ./app/
COPY scripts/ ./scripts/
# Copy the .env only if you aren't using Docker Compose secrets/env_file
COPY .env . 

# Create a non-root user for security (Class of 2026 Production Standard)
RUN useradd -m mega_user && chown -R mega_user /app
USER mega_user

# Expose the FastAPI port
EXPOSE 8000

# Start the application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]