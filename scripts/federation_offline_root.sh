#!/usr/bin/env bash
set -euo pipefail

: "${SYNERGY_FEDERATION_SOURCE:?required}"
: "${SYNERGY_FEDERATION_ROOT_PUBLIC:?required}"
: "${SYNERGY_FEDERATION_ROOT_SECRET:?required}"

cmd="${1:-}"
case "$cmd" in
  root-init)
    test ! -e "$SYNERGY_FEDERATION_ROOT_SECRET" || { echo "root secret already exists" >&2; exit 3; }
    test ! -e "$SYNERGY_FEDERATION_ROOT_PUBLIC" || { echo "root public already exists" >&2; exit 3; }
    shttps-federation root-init --secret "$SYNERGY_FEDERATION_ROOT_SECRET" --public "$SYNERGY_FEDERATION_ROOT_PUBLIC"
    ;;
  issue-signer-cert)
    signer_public="${2:?usage: federation_offline_root.sh issue-signer-cert SIGNER_PUBLIC OUT [GENERATION]}"
    out="${3:?missing output certificate path}"
    generation="${4:-1}"
    shttps-federation-delegated issue-signer-cert \
      --root-secret "$SYNERGY_FEDERATION_ROOT_SECRET" --root-public "$SYNERGY_FEDERATION_ROOT_PUBLIC" \
      --signer-public "$signer_public" --source "$SYNERGY_FEDERATION_SOURCE" --out "$out" \
      --generation "$generation" --valid-days "${SYNERGY_FEDERATION_SIGNER_VALID_DAYS:-35}" \
      --max-registry-valid-days "${SYNERGY_FEDERATION_REGISTRY_VALID_DAYS:-7}"
    ;;
  revocations-init)
    out="${2:?usage: federation_offline_root.sh revocations-init OUT}"
    shttps-federation-delegated revocations-init \
      --root-secret "$SYNERGY_FEDERATION_ROOT_SECRET" --root-public "$SYNERGY_FEDERATION_ROOT_PUBLIC" \
      --out "$out" --valid-days "${SYNERGY_FEDERATION_REVOCATIONS_VALID_DAYS:-90}"
    ;;
  revoke-signer)
    current="${2:?usage: federation_offline_root.sh revoke-signer CURRENT_REVOCATIONS SIGNER_ID OUT}"
    signer_id="${3:?missing signer id}"
    out="${4:?missing output revocations path}"
    shttps-federation-delegated revoke-signer \
      --root-secret "$SYNERGY_FEDERATION_ROOT_SECRET" --root-public "$SYNERGY_FEDERATION_ROOT_PUBLIC" \
      --revocations "$current" --signer-id "$signer_id" --out "$out" \
      --valid-days "${SYNERGY_FEDERATION_REVOCATIONS_VALID_DAYS:-90}"
    ;;
  *)
    echo "usage: $0 {root-init|issue-signer-cert SIGNER_PUBLIC OUT [GENERATION]|revocations-init OUT|revoke-signer CURRENT_REVOCATIONS SIGNER_ID OUT}" >&2
    exit 2
    ;;
esac
