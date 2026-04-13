FROM python:3.11-slim

WORKDIR /app

# System deps for spaCy + building C extensions
RUN apt-get update && apt-get install -y \
    gcc g++ curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Download transformer models at build time (optional, skip with BUILD_DOWNLOAD_MODELS=false)
ARG BUILD_DOWNLOAD_MODELS=true
ARG MODEL_CACHE_DIR=/models
ENV MODEL_CACHE_DIR=${MODEL_CACHE_DIR}
COPY scripts/download_models.py .
RUN if [ "${BUILD_DOWNLOAD_MODELS}" = "true" ]; then \
        python download_models.py; \
    fi

# Copy application code
COPY app/ ./app/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
