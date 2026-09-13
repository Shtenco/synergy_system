#!/usr/bin/env bash
set -euo pipefail

SHTTPS_COMMIT="${SHTTPS_COMMIT:-e8bb87fae6d98417782d51a583d4b9bee7896680}"
AI_COMPRESS_COMMIT="${AI_COMPRESS_COMMIT:-551fae36eacb5713aa503fc9da2fbc44fe8f2e84}"
SRC_ROOT="${SYNERGY_BUILD_ROOT:-/opt/synergy/src}"
VENV="${SYNERGY_PYTHON_VENV:-/opt/synergy/venv}"

if [[ "${EUID}" -ne 0 ]]; then
  echo "run as root" >&2
  exit 2
fi

install -d -m 0755 "$SRC_ROOT"

clone_pin() {
  local url="$1" path="$2" sha="$3"
  if [[ ! -d "$path/.git" ]]; then git clone "$url" "$path"; fi
  git -C "$path" fetch --prune origin "$sha"
  git -C "$path" checkout --detach "$sha"
  test "$(git -C "$path" rev-parse HEAD)" = "$sha"
}

clone_pin https://github.com/Shtenco/shttps.git "$SRC_ROOT/shttps" "$SHTTPS_COMMIT"
clone_pin https://github.com/Shtenco/ai_compress.git "$SRC_ROOT/ai_compress" "$AI_COMPRESS_COMMIT"

"$VENV/bin/python" -m pip install -e "$SRC_ROOT/shttps[pq]"

cat >/etc/synergy-federation-stack.env <<EOF
OQS_INSTALL_PATH=/opt/synergy/oqs/0.16.0
LD_LIBRARY_PATH=/opt/synergy/oqs/0.16.0/lib
PYOQS_VERSION=0.16.0
SYNERGY_PYTHON_VENV=$VENV
SHTTPS_CHECKOUT=$SRC_ROOT/shttps
SHTTPS_COMMIT=$SHTTPS_COMMIT
AI_COMPRESS_CHECKOUT=$SRC_ROOT/ai_compress
AI_COMPRESS_COMMIT=$AI_COMPRESS_COMMIT
SHTTPS_AI_COMPRESS_PATH=$SRC_ROOT/ai_compress
SHTTPS_REQUIRE_HYBRID=1
EOF
chmod 0644 /etc/synergy-federation-stack.env

echo "SYNERGY_FEDERATION_STACK_INSTALLED shttps=$SHTTPS_COMMIT ai_compress=$AI_COMPRESS_COMMIT"
