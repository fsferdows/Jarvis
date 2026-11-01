#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONUNBUFFERED=1
export OMNIVOICE_PORT=8008
echo "[omnivoice] Starting OmniVoice TTS service on port 8008..."
exec "$DIR/omnivoice_env/bin/python" "$DIR/omnivoice_service.py"

