#!/usr/bin/env bash
set -euo pipefail

: "${SYNERGY_FEDERATION_SOURCE:=config/federation_trust_source_v1.json}"
: "${SYNERGY_FEDERATION_ROOT_PUBLIC:=/etc/synergy/federation-root.json}"
: "${SYNERGY_FEDERATION_ROOT_SECRET:=/run/secrets/federation-root.identity.json}"
: "${SYNERGY_FEDERATION_REGISTRY:=/etc/synergy/federation-registry.signed.json}"
: "${SYNERGY_FEDERATION_NODE_SECRETS:=/run/secrets/synergy-federation}"
: "${SYNERGY_FEDERATION_VERIFY_STATE:=/var/lib/synergy/federation-registry-state.json}"
: "${SYNERGY_FEDERATION_REGISTRY_VALID_DAYS:=30}"
: "${SYNERGY_FEDERATION_NODE_VALID_DAYS:=90}"
: "${SYNERGY_FEDERATION_ROTATE_BEFORE_SECONDS:=604800}"
: "${SYNERGY_FEDERATION_ROTATION_GRACE_SECONDS:=3600}"

cmd="${1:-}"
case "$cmd" in
  root-init)
    shttps-federation root-init --secret "$SYNERGY_FEDERATION_ROOT_SECRET" --public "$SYNERGY_FEDERATION_ROOT_PUBLIC"
    ;;
  provision-all)
    shttps-federation provision-all --source "$SYNERGY_FEDERATION_SOURCE" --root-secret "$SYNERGY_FEDERATION_ROOT_SECRET" --root-public "$SYNERGY_FEDERATION_ROOT_PUBLIC" --secrets-dir "$SYNERGY_FEDERATION_NODE_SECRETS" --registry-out "$SYNERGY_FEDERATION_REGISTRY" --valid-days "$SYNERGY_FEDERATION_REGISTRY_VALID_DAYS" --node-valid-days "$SYNERGY_FEDERATION_NODE_VALID_DAYS"
    ;;
  verify)
    shttps-federation verify --root-public "$SYNERGY_FEDERATION_ROOT_PUBLIC" --registry "$SYNERGY_FEDERATION_REGISTRY" --state "$SYNERGY_FEDERATION_VERIFY_STATE"
    ;;
  rotate-due)
    tmp="${SYNERGY_FEDERATION_REGISTRY}.next"
    shttps-federation-rotate-due --root-secret "$SYNERGY_FEDERATION_ROOT_SECRET" --root-public "$SYNERGY_FEDERATION_ROOT_PUBLIC" --registry "$SYNERGY_FEDERATION_REGISTRY" --secrets-dir "$SYNERGY_FEDERATION_NODE_SECRETS" --out "$tmp" --rotate-before-seconds "$SYNERGY_FEDERATION_ROTATE_BEFORE_SECONDS" --grace-seconds "$SYNERGY_FEDERATION_ROTATION_GRACE_SECONDS" --node-valid-days "$SYNERGY_FEDERATION_NODE_VALID_DAYS"
    mv "$tmp" "$SYNERGY_FEDERATION_REGISTRY"
    ;;
  revoke)
    node_id="${2:?usage: federation_operator.sh revoke NODE_ID}"
    tmp="${SYNERGY_FEDERATION_REGISTRY}.next"
    shttps-federation revoke --root-secret "$SYNERGY_FEDERATION_ROOT_SECRET" --root-public "$SYNERGY_FEDERATION_ROOT_PUBLIC" --registry "$SYNERGY_FEDERATION_REGISTRY" --node-id "$node_id" --out "$tmp"
    mv "$tmp" "$SYNERGY_FEDERATION_REGISTRY"
    ;;
  *)
    echo "usage: $0 {root-init|provision-all|verify|rotate-due|revoke NODE_ID}" >&2
    exit 2
    ;;
esac
