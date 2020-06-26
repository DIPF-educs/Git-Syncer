FROM python:3.8-slim
RUN apt update && \
    apt install --no-install-recommends -y git openssl ssh && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app/sync
ADD sync.py /app/sync/sync.py

ENTRYPOINT ["python3", "sync.py"]
