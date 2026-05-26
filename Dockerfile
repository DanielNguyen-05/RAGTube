FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install dependencies first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8501

# Launch the Streamlit web interface
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
