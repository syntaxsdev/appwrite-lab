#!/usr/bin/env bash
set -euo pipefail

CERT_DIR=${CERT_DIR:-/certs}
CAROOT="${CERT_DIR}/ca"
mkdir -p "${CAROOT}"

# Generate CA + leaf if missing
if [ ! -f "${CERT_DIR}/api.twilio.com.crt" ] || [ ! -f "${CERT_DIR}/api.twilio.com.key" ]; then
  echo ">> Generating dev CA and leaf cert..."
  export CAROOT
  mkcert -install >/dev/null 2>&1 || true
  mkcert -key-file "${CERT_DIR}/api.twilio.com.key" \
         -cert-file "${CERT_DIR}/api.twilio.com.crt" \
         "api.twilio.com"
  cp "${CAROOT}/rootCA.pem" "${CERT_DIR}/dev-rootCA.pem"
fi

echo ">> Starting Twilio shim (HTTPS)…"
exec uvicorn main:app \
  --host 0.0.0.0 --port 443 \
  --ssl-keyfile "${CERT_DIR}/api.twilio.com.key" \
  --ssl-certfile "${CERT_DIR}/api.twilio.com.crt"
