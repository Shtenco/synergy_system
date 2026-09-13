#!/usr/bin/env bash
set -euo pipefail

[[ "${EUID}" -eq 0 ]] || { echo "run as root" >&2; exit 2; }

install -d -m 0755 /usr/local/libexec /etc/systemd/system /etc/synergy/federation /var/lib/synergy/federation/private/nodes /var/lib/synergy/federation/state
install -m 0755 scripts/federation_hsm_operator.sh /usr/local/libexec/synergy-federation-hsm-operator
install -m 0755 scripts/federation_offline_root.sh /usr/local/libexec/synergy-federation-offline-root
install -m 0755 scripts/federation_preflight.sh /usr/local/libexec/synergy-federation-preflight
install -m 0644 deploy/systemd/synergy-federation-maintenance.service /etc/systemd/system/synergy-federation-maintenance.service
install -m 0644 deploy/systemd/synergy-federation-maintenance.timer /etc/systemd/system/synergy-federation-maintenance.timer

if [[ ! -e /etc/synergy-federation-hsm.env ]]; then
  install -m 0600 config/federation_hsm_operator.env.example /etc/synergy-federation-hsm.env
else
  echo "preserving existing /etc/synergy-federation-hsm.env"
fi

# Root private material is deliberately not installed or copied to this node.
if grep -q '^SYNERGY_FEDERATION_ROOT_SECRET=' /etc/synergy-federation-hsm.env; then
  echo "REFUSING_TO_INSTALL: online HSM env must not reference Federation Root secret" >&2
  exit 42
fi

systemctl daemon-reload
systemctl enable synergy-federation-maintenance.timer

echo "SYSTEMD_HSM_PROFILE_INSTALLED_NOT_STARTED"
echo "Complete offline root certification, HSM key initialization, initial registry provisioning and an explicit one-shot maintenance test before starting the timer."
