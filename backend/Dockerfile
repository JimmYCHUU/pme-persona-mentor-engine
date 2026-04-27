FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg curl build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
COPY constraints.txt .
ENV PIP_CONSTRAINT=/app/constraints.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
COPY . .
RUN mkdir -p data/{chroma,sessions,uploads,personas,mastery_certs}
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
