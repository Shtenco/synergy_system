#!/usr/bin/env bash
set -euo pipefail

: "${SYNERGY_FEDERATION_ROOT_PUBLIC:?required}"
: "${SYNERGY_FEDERATION_SIGNER_PUBLIC:?required}"
: "${SYNERGY_FEDERATION_SIGNER_CERT:?required}"
: "${SYNERGY_FEDERATION_SIGNER_REVOCATIONS:?required}"
: "${SYNERGY_FEDERATION_REGISTRY:?required}"
: "${SYNERGY_FEDERATION_NODE_SECRETS:?required}"
: "${SYNERGY_FEDERATION_VERIFY_STATE:?required}"
: "${SHTTPS_PKCS11_MODULE:?required}"
: "${SHTTPS_PKCS11_TOKEN_LABEL:?required}"
: "${SHTTPS_PKCS11_KEY_LABEL:?required}"
: "${SHTTPS_PKCS11_PIN_FILE:?required}"

# Fail closed if an operator accidentally exposes the cold root secret here.
if [[ -n "${SYNERGY_FEDERATION_ROOT_SECRET:-}" ]]; then
  echo "REFUSING_TO_RUN: Federation Root secret must not exist on the online HSM node" >&2
  exit 42
fi

: "${SYNERGY_FEDERATION_REGISTRY_VALID_DAYS:=7}"
: "${SYNERGY_FEDERATION_NODE_VALID_DAYS:=90}"
: "${SYNERGY_FEDERATION_ROTATE_BEFORE_SECONDS:=604800}"
: "${SYNERGY_FEDERATION_REGISTRY_RENEW_BEFORE_SECONDS:=172800}"
: "${SYNERGY_FEDERATION_ROTATION_GRACE_SECONDS:=3600}"

cmd="${1:-}"
case "$cmd" in
  hsm-init)
    test ! -e "$SYNERGY_FEDERATION_SIGNER_PUBLIC" || { echo "signer public descriptor already exists" >&2; exit 3; }
    shttps-hsm-signer init \
      --module "$SHTTPS_PKCS11_MODULE" --token-label "$SHTTPS_PKCS11_TOKEN_LABEL" \
      --key-label "$SHTTPS_PKCS11_KEY_LABEL" --pin-file "$SHTTPS_PKCS11_PIN_FILE" \
      --public-out "$SYNERGY_FEDERATION_SIGNER_PUBLIC"
    ;;
  hsm-check)
    shttps-hsm-signer check \
      --module "$SHTTPS_PKCS11_MODULE" --token-label "$SHTTPS_PKCS11_TOKEN_LABEL" \
      --key-label "$SHTTPS_PKCS11_KEY_LABEL" --pin-file "$SHTTPS_PKCS11_PIN_FILE"
    ;;
  provision-initial)
    : "${SYNERGY_FEDERATION_SOURCE:?required for initial provisioning}"
    test ! -e "$SYNERGY_FEDERATION_REGISTRY" || { echo "registry already exists" >&2; exit 4; }
    shttps-federation-delegated provision-initial \
      --root-public "$SYNERGY_FEDERATION_ROOT_PUBLIC" \
      --signer-cert "$SYNERGY_FEDERATION_SIGNER_CERT" \
      --signer-revocations "$SYNERGY_FEDERATION_SIGNER_REVOCATIONS" \
      --source "$SYNERGY_FEDERATION_SOURCE" --secrets-dir "$SYNERGY_FEDERATION_NODE_SECRETS" \
      --registry-out "$SYNERGY_FEDERATION_REGISTRY" \
      --registry-valid-days "$SYNERGY_FEDERATION_REGISTRY_VALID_DAYS" \
      --node-valid-days "$SYNERGY_FEDERATION_NODE_VALID_DAYS"
    ;;
  verify)
    shttps-federation-delegated verify \
      --root-public "$SYNERGY_FEDERATION_ROOT_PUBLIC" \
      --signer-revocations "$SYNERGY_FEDERATION_SIGNER_REVOCATIONS" \
      --registry "$SYNERGY_FEDERATION_REGISTRY" --state "$SYNERGY_FEDERATION_VERIFY_STATE"
    ;;
  maintain)
    shttps-federation-delegated maintain \
      --root-public "$SYNERGY_FEDERATION_ROOT_PUBLIC" \
      --signer-cert "$SYNERGY_FEDERATION_SIGNER_CERT" \
      --signer-revocations "$SYNERGY_FEDERATION_SIGNER_REVOCATIONS" \
      --registry "$SYNERGY_FEDERATION_REGISTRY" --secrets-dir "$SYNERGY_FEDERATION_NODE_SECRETS" \
      --state "$SYNERGY_FEDERATION_VERIFY_STATE" \
      --rotate-before-seconds "$SYNERGY_FEDERATION_ROTATE_BEFORE_SECONDS" \
      --renew-before-seconds "$SYNERGY_FEDERATION_REGISTRY_RENEW_BEFORE_SECONDS" \
      --registry-valid-days "$SYNERGY_FEDERATION_REGISTRY_VALID_DAYS" \
      --node-valid-days "$SYNERGY_FEDERATION_NODE_VALID_DAYS" \
      --grace-seconds "$SYNERGY_FEDERATION_ROTATION_GRACE_SECONDS"
    ;;
  revoke-node)
    node_id="${2:?usage: federation_hsm_operator.sh revoke-node NODE_ID}"
    shttps-federation-delegated revoke-node \
      --root-public "$SYNERGY_FEDERATION_ROOT_PUBLIC" \
      --signer-cert "$SYNERGY_FEDERATION_SIGNER_CERT" \
      --signer-revocations "$SYNERGY_FEDERATION_SIGNER_REVOCATIONS" \
      --registry "$SYNERGY_FEDERATION_REGISTRY" --node-id "$node_id" \
      --registry-valid-days "$SYNERGY_FEDERATION_REGISTRY_VALID_DAYS"
    ;;
  *)
    echo "usage: $0 {hsm-init|hsm-check|provision-initial|verify|maintain|revoke-node NODE_ID}" >&2
    exit 2
    ;;
esac
