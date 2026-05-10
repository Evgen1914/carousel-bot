#!/usr/bin/env bash
set -euo pipefail

if [[ "${USE_TOR_FOR_TELEGRAM:-false}" == "true" && -z "${TELEGRAM_PROXY:-}" ]]; then
  tor --SocksPort 127.0.0.1:9050 --Log "notice stdout" &
  export TELEGRAM_PROXY="socks5://127.0.0.1:9050"

  python - <<'PY'
import socket
import time

deadline = time.time() + 45
while time.time() < deadline:
    try:
        with socket.create_connection(("127.0.0.1", 9050), timeout=1):
            break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit("Tor SOCKS proxy did not start in time")
PY
fi

exec carousel-bot

