#!/usr/bin/env bash
set -euo pipefail

# Run from the synergy_system repository root after install_oqs_ubuntu.sh and
# install_synergy_federation_stack.sh. This creates REAL PQ identities only on
# the protected signing node. It intentionally refuses to overwrite an existing
# root or registry.

STACK_ENV="${SYNERGY_STACK_ENV:-/etc/synergy-federation-stack.env}"
OPERATOR_ENV="${SYNERGY_OPERATOR_ENV:-/etc/synergy-federation-operator.env}"

[[ "${EUID}" -eq 0 ]] || { echo "run as root" >&2; exit 2; }
[[ -f "$STACK_ENV" ]] || { echo "missing $STACK_ENV" >&2; exit 2; }
[[ -f "$OPERATOR_ENV" ]] || { echo "missing $OPERATOR_ENV" >&2; exit 2; }

set -a
source "$STACK_ENV"
source "$OPERATOR_ENV"
set +a

export PATH="$SYNERGY_PYTHON_VENV/bin:$PATH"
export LD_LIBRARY_PATH="$OQS_INSTALL_PATH/lib:${LD_LIBRARY_PATH:-}"

bash scripts/federation_preflight.sh

install -d -m 0755 "$(dirname "$SYNERGY_FEDERATION_ROOT_PUBLIC")"
install -d -m 0755 "$(dirname "$SYNERGY_FEDERATION_REGISTRY")"
install -d -m 0700 "$(dirname "$SYNERGY_FEDERATION_ROOT_SECRET")"
install -d -m 0700 "$SYNERGY_FEDERATION_NODE_SECRETS"
install -d -m 0700 "$(dirname "$SYNERGY_FEDERATION_VERIFY_STATE")"

for p in "$SYNERGY_FEDERATION_ROOT_PUBLIC" "$SYNERGY_FEDERATION_ROOT_SECRET" "$SYNERGY_FEDERATION_REGISTRY"; do
  if [[ -e "$p" ]]; then
    echo "refusing to overwrite existing federation artifact: $p" >&2
    exit 3
  fi
done

bash scripts/federation_operator.sh root-init
bash scripts/federation_operator.sh provision-all
bash scripts/federation_operator.sh verify

chmod 0600 "$SYNERGY_FEDERATION_ROOT_SECRET"
find "$SYNERGY_FEDERATION_NODE_SECRETS" -type f -name '*.json' -exec chmod 0600 {} +
chmod 0644 "$SYNERGY_FEDERATION_ROOT_PUBLIC" "$SYNERGY_FEDERATION_REGISTRY"
chmod 0600 "$SYNERGY_FEDERATION_VERIFY_STATE"

"$SYNERGY_PYTHON_VENV/bin/python" - "$SYNERGY_FEDERATION_REGISTRY" <<'PY'
import json,sys
p=sys.argv[1]
d=json.load(open(p,encoding='utf-8'))
b=d['registry']
repos=b['repositories']; controls=b.get('control_principals',[])
assert len(repos)==51
assert any(x['name']=='synergy_ai_company' for x in controls)
assert all(len(x.get('nodes',[]))==1 for x in [*repos,*controls])
print(json.dumps({
  'ceremony':'OK',
  'sequence':b['sequence'],
  'registry_hash':d['registry_hash'],
  'repositories':len(repos),
  'control_principals':len(controls),
  'node_identities':sum(len(x.get('nodes',[])) for x in [*repos,*controls]),
},sort_keys=True))
PY

echo "FIRST_BOOT_CEREMONY_COMPLETE"
echo "Back up the public root and registry separately. Protect the private directory with encrypted storage and offline backup before enabling maintenance."
