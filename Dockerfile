FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    traceroute \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt README.md ./
COPY netracoon/ netracoon/
COPY netracoon.py ./

RUN pip install --no-cache-dir .

ENTRYPOINT ["netracoon"]
CMD ["--help"]
