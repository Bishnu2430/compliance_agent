# deploy/Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y git build-essential && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PORT 8080
EXPOSE 8080

# default execution: run a sample audit with gunicorn + uvicorn worker (for production)
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8080"]
