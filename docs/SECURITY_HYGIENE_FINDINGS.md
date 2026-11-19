# 🔐 SYNERGY — Documentation Security Hygiene Findings

> Срез: 20 ноября 2026; исходные findings сохранены как исторический baseline.
> Цель: зафиксировать наличие потенциально чувствительных credential artifacts в Git, не публикуя содержимое секретов.

## Правило

Любой private key, deployer key, wallet `.env`, SSH private key или иной credential, однажды попавший в Git history, должен рассматриваться как потенциально скомпрометированный.

```text
secret committed to Git
        ↓
assume compromised
        ↓
revoke / rotate
        ↓
remove from current tree
        ↓
optional history rewrite
        ↓
secret scanner + CI guard
```

## Findings текущего deep pass

### `Shtenco/synergy_usds`

В дереве `main` обнаружен файл с именем `base-mainnet-deployer.key`.

Рекомендация: не использовать соответствующий credential для production; rotate/revoke и удалить секретный материал из repository tree.

### `Shtenco/synergy_cashero`

В дереве `main` присутствуют `.env`, `owner.env`, `bot1.env`, `bot2.env`.

Факт наличия файла не доказывает, что внутри действующий секрет, но такие paths должны пройти secret scan. Любые реальные private keys необходимо rotate.

### `Shtenco/synergy_turbo_linux`

В дереве виден `Linux Ubuntu.ppk`.

`.ppk` обычно является PuTTY private-key container. Если это реальный SSH credential, его следует считать скомпрометированным и заменить.

## Что НЕ сделано

- содержимое ключей не копировалось;
- fingerprints/private material не публиковались;
- соответствующие аккаунты не проверялись;
- credential не использовались.

## Mandatory repository policy

1. `.env*`, `*.key`, `*.pem`, `*.p12`, `*.ppk`, wallet seed/private-key files — deny by default;
2. разрешённые example-файлы должны содержать только placeholders;
3. добавить secret scanning в CI;
4. production secrets — только secret manager / protected CI variables / HSM/MPC where appropriate;
5. incident response должен включать rotation, а не только удаление файла.

## Следующий gate

Добавить в `synergy_system` federation CI отдельную проверку repository manifests на запрещённые credential filename patterns и централизованный security checklist.


## Реализованный security gate

Добавлены:

```text
registry/SECURITY_BLOCKERS.json
integration/security_gate.py
.github/workflows/federation-security-gate.yml
```

Gate fail-closed проверяет, что:

- repository с `federation_promotion_blocked=true` не повышен выше `ARCHITECTURAL_ONLY`;
- repository с `deployment_blocked=true` не имеет edge со статусом `DEPLOYED`.

Для `Shtenco/synergy_usds` дополнительно добавлены `.gitignore` patterns для credential-файлов и локальный `SECURITY_FEDERATION_BLOCKER.md`. Это предотвращает новые случайные коммиты такого типа, но **не считается rotation или history cleanup**.


## Re-audit — 20 November 2026

The current main trees were rechecked by path only; no secret values or private-key bytes were read or reproduced.

- **Cashero:** .env, bot1.env, bot2.env and owner.env remain in main. No dedicated security-remediation PR is open. Existing PR #8 is provenance-only and PR #6 is trading/simulation work. Status remains UNRESOLVED / P0.
- **USDS:** base-mainnet-deployer.key remains in main and also remains in the security PR #6 branch. PR #6 changes only .gitignore and SECURITY_KEY_ROTATION.md; it does not remove the tracked key. Status remains UNRESOLVED / P0.
- **TURBO Linux:** Linux Ubuntu.ppk remains in main. Draft PR #13 removes it from the PR branch and adds an incident report, but is unmerged. The incident report does not prove external rotation, host revocation or history sanitization. Status remains UNRESOLVED / P0.

TURBO's federation-promotion flag is now fail-closed and its interface status is SECURITY_BLOCKED. This aligns the registry with the documented unencrypted SSH-key incident. No deployment or key rotation was performed by this audit.

See [SECURITY_REAUDIT_2026-11-20.md](SECURITY_REAUDIT_2026-11-20.md) and [SECURITY_BLOCKERS.json](../registry/SECURITY_BLOCKERS.json).
