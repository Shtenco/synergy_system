#!/usr/bin/env bash
set -euo pipefail

# Reproducible OQS installation for the SYNERGY federation signing/runtime nodes.
# Tested target: Ubuntu/Debian-family hosts with Python 3.11+.
# This script pins immutable upstream commits corresponding to release 0.16.0.

LIBOQS_COMMIT="5a1a854b0dc9f2141bdc771c555ee60c37950183"
LIBOQS_PY_COMMIT="c6378cd5c8db74c0adf34ddcfbb96ee9c99f8061"
PREFIX="${OQS_INSTALL_PATH:-/opt/synergy/oqs/0.16.0}"
SRC_ROOT="${SYNERGY_BUILD_ROOT:-/opt/synergy/src}"
VENV="${SYNERGY_PYTHON_VENV:-/opt/synergy/venv}"

if [[ "${EUID}" -ne 0 ]]; then
  echo "run as root" >&2
  exit 2
fi

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  ca-certificates git cmake ninja-build build-essential pkg-config \
  libssl-dev python3 python3-venv python3-pip

install -d -m 0755 "$SRC_ROOT" "$PREFIX"
rm -rf "$SRC_ROOT/liboqs" "$SRC_ROOT/liboqs-python"
git clone https://github.com/open-quantum-safe/liboqs.git "$SRC_ROOT/liboqs"
git -C "$SRC_ROOT/liboqs" checkout --detach "$LIBOQS_COMMIT"

cmake -S "$SRC_ROOT/liboqs" -B "$SRC_ROOT/liboqs/build" -GNinja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$PREFIX" \
  -DBUILD_SHARED_LIBS=ON \
  -DOQS_BUILD_ONLY_LIB=ON
cmake --build "$SRC_ROOT/liboqs/build" --parallel
cmake --install "$SRC_ROOT/liboqs/build"

python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip setuptools wheel

git clone https://github.com/open-quantum-safe/liboqs-python.git "$SRC_ROOT/liboqs-python"
git -C "$SRC_ROOT/liboqs-python" checkout --detach "$LIBOQS_PY_COMMIT"
OQS_INSTALL_PATH="$PREFIX" "$VENV/bin/python" -m pip install "$SRC_ROOT/liboqs-python"

cat >/etc/profile.d/synergy-oqs.sh <<EOF
export OQS_INSTALL_PATH=$PREFIX
export LD_LIBRARY_PATH=$PREFIX/lib:\${LD_LIBRARY_PATH:-}
export PYOQS_VERSION=0.16.0
EOF
chmod 0644 /etc/profile.d/synergy-oqs.sh

OQS_INSTALL_PATH="$PREFIX" LD_LIBRARY_PATH="$PREFIX/lib" "$VENV/bin/python" - <<'PY'
import oqs
assert oqs.oqs_version() == "0.16.0", oqs.oqs_version()
assert oqs.oqs_python_version() == "0.16.0", oqs.oqs_python_version()
k=set(oqs.get_enabled_kem_mechanisms())
s=set(oqs.get_enabled_sig_mechanisms())
for mech in ("ML-KEM-1024",):
    assert mech in k, (mech, sorted(k))
for mech in ("ML-DSA-87","SLH-DSA-SHAKE-256s"):
    assert mech in s, (mech, sorted(s))
print("OQS_ATTESTATION_OK", oqs.oqs_version(), oqs.oqs_python_version())
PY

echo "Installed pinned liboqs/liboqs-python 0.16.0 into $PREFIX / $VENV"
