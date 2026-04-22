FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y unzip curl wget && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create data directory (will be mounted as volume on Railway)
RUN mkdir -p /data

# Set environment
ENV PYTHONUNBUFFERED=1
ENV DB_PATH=/data/aiktivist.db

EXPOSE 3000

CMD ["sh", "-c", "reflex init && reflex run --env prod"]
