FROM python:3.12-slim

WORKDIR /app

# System deps kept minimal; sentence-transformers pulls torch as a wheel.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the local embedding model so the image is self-contained and the
# first request doesn't pay a download (also lets it run offline).
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
