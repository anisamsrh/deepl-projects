FROM python:3.12-slim

WORKDIR /app

# Install sistem dependensi jika ada
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["sh", "-c", "uvicorn backend.backend:app --host 0.0.0.0 --port 8000 & streamlit run frontend/frontend.py --server.address=0.0.0.0 --server.port=8501"]