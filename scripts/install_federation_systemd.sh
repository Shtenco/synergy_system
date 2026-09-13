#!/usr/bin/env bash
set -euo pipefail

[[ "${EUID}" -eq 0 ]] || { echo "run as root" >&2; exit 2; }

install -d -m 0755 /usr/local/libexec /etc/systemd/system
install -m 0755 scripts/federation_operator.sh /usr/local/libexec/synergy-federation-operator
install -m 0755 scripts/federation_preflight.sh /usr/local/libexec/synergy-federation-preflight
install -m 0644 deploy/systemd/synergy-federation-maintenance.service /etc/systemd/system/synergy-federation-maintenance.service
install -m 0644 deploy/systemd/synergy-federation-maintenance.timer /etc/systemd/system/synergy-federation-maintenance.timer

systemctl daemon-reload
systemctl enable synergy-federation-maintenance.timer

echo "SYSTEMD_INSTALLED_NOT_STARTED"
echo "Run first-boot ceremony and an explicit maintenance service test before starting the timer."
