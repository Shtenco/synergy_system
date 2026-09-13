#!/usr/bin/env bash
set -euo pipefail

: "${OQS_INSTALL_PATH:=/opt/synergy/oqs/0.16.0}"
: "${SYNERGY_PYTHON_VENV:=/opt/synergy/venv}"
: "${SHTTPS_CHECKOUT:=/opt/synergy/src/shttps}"
: "${SHTTPS_COMMIT:=e8bb87fae6d98417782d51a583d4b9bee7896680}"
: "${AI_COMPRESS_CHECKOUT:=/opt/synergy/src/ai_compress}"
: "${AI_COMPRESS_COMMIT:=551fae36eacb5713aa503fc9da2fbc44fe8f2e84}"

export OQS_INSTALL_PATH
export LD_LIBRARY_PATH="$OQS_INSTALL_PATH/lib:${LD_LIBRARY_PATH:-}"
export PYOQS_VERSION=0.16.0
export SHTTPS_AI_COMPRESS_PATH="$AI_COMPRESS_CHECKOUT"
export SHTTPS_REQUIRE_HYBRID=1

[[ -x "$SYNERGY_PYTHON_VENV/bin/python" ]] || { echo "missing venv" >&2; exit 2; }
[[ -d "$SHTTPS_CHECKOUT/.git" ]] || { echo "missing SHTTPS checkout" >&2; exit 2; }
[[ -d "$AI_COMPRESS_CHECKOUT/.git" ]] || { echo "missing ai_compress checkout" >&2; exit 2; }

[[ "$(git -C "$SHTTPS_CHECKOUT" rev-parse HEAD)" == "$SHTTPS_COMMIT" ]] || { echo "SHTTPS commit mismatch" >&2; exit 3; }
[[ "$(git -C "$AI_COMPRESS_CHECKOUT" rev-parse HEAD)" == "$AI_COMPRESS_COMMIT" ]] || { echo "ai_compress commit mismatch" >&2; exit 3; }

"$SYNERGY_PYTHON_VENV/bin/python" - <<'PY'
import oqs
assert oqs.oqs_version() == "0.16.0", oqs.oqs_version()
assert oqs.oqs_python_version() == "0.16.0", oqs.oqs_python_version()
assert "ML-KEM-1024" in oqs.get_enabled_kem_mechanisms()
assert "ML-DSA-87" in oqs.get_enabled_sig_mechanisms()
assert "SLH-DSA-SHAKE-256s" in oqs.get_enabled_sig_mechanisms()
print("OQS_VERSION_AND_ALGORITHMS_OK")
PY

"$SYNERGY_PYTHON_VENV/bin/shttps-diagnose"
echo "SYNERGY_FEDERATION_PREFLIGHT_OK"
