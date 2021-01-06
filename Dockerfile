FROM python:3.8-slim

RUN apt update && \
    apt install --no-install-recommends -y git openssl ssh && \
    rm -rf /var/lib/apt/lists/*

ADD sync.py /bin/sync
RUN chmod +x /bin/sync

