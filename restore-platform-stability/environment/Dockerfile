FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    git \
    build-essential \
    docker.io \
    docker-compose-v2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
