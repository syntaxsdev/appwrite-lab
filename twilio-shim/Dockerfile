FROM python:3.12-slim

WORKDIR /app

# deps
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

# mkcert (static binary)
RUN curl -L -o /usr/local/bin/mkcert \
  https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-amd64 \
 && chmod +x /usr/local/bin/mkcert

# app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py ./main.py

# entrypoint that generates certs then runs HTTPS
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 443
ENTRYPOINT ["/entrypoint.sh"]
