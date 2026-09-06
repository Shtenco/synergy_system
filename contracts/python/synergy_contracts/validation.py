from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker, RefResolver


class ContractValidationError(ValueError):
    pass


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class ContractValidator:
    def __init__(self, schema_dir: str | Path, registry_path: str | Path | None = None):
        self.schema_dir = Path(schema_dir)
        self._schemas: dict[str, dict[str, Any]] = {}
        self._schema_store: dict[str, dict[str, Any]] = {}
        for path in self.schema_dir.glob("*.json"):
            schema = json.loads(path.read_text(encoding="utf-8"))
            file_uri = path.resolve().as_uri()
            self._schemas[path.name] = schema
            self._schema_store[path.name] = schema
            self._schema_store[file_uri] = schema
            if "$id" in schema:
                self._schemas[schema["$id"]] = schema
                self._schema_store[schema["$id"]] = schema

        if registry_path is None:
            candidate = self.schema_dir.parent / "config" / "contract_registry_v1.json"
            registry_path = candidate if candidate.exists() else None
        self._registry: dict[str, dict[str, Any]] = {}
        if registry_path is not None:
            registry = json.loads(Path(registry_path).read_text(encoding="utf-8"))
            self._registry = {entry["type"]: entry for entry in registry["contracts"]}

    def validate(self, contract: dict[str, Any], schema_file: str) -> None:
        schema = self._schemas[schema_file]
        base_uri = self.schema_dir.resolve().as_uri() + "/"
        resolver = RefResolver(
            base_uri=base_uri,
            referrer=schema,
            store=self._schema_store,
        )
        validator = Draft202012Validator(schema, resolver=resolver, format_checker=FormatChecker())
        errors = sorted(validator.iter_errors(contract), key=lambda e: list(e.absolute_path))
        if errors:
            rendered = "; ".join(f"{list(e.absolute_path)}: {e.message}" for e in errors)
            raise ContractValidationError(rendered)
        self._validate_payload_hash(contract)
        self._validate_registry_binding(contract, schema_file)
        self._validate_authority_invariants(contract)

    @staticmethod
    def _validate_payload_hash(contract: dict[str, Any]) -> None:
        expected = canonical_payload_hash(contract["payload"])
        actual = contract["evidence"]["payload_hash"]
        if expected != actual:
            raise ContractValidationError("payload_hash does not match canonical payload SHA-256")

    def _validate_registry_binding(self, contract: dict[str, Any], schema_file: str) -> None:
        if not self._registry:
            return
        ctype = contract["contract_type"]
        entry = self._registry.get(ctype)
        if entry is None:
            raise ContractValidationError(f"unregistered contract_type: {ctype}")
        if entry["schema"] != schema_file:
            raise ContractValidationError(f"{ctype} must validate against {entry['schema']}")

        producer = contract["producer"]
        if producer["repo"] != entry["producer"]:
            raise ContractValidationError(f"{ctype} producer repo must be {entry['producer']}")
        if producer["authority"] != entry["producer_authority"]:
            raise ContractValidationError(f"{ctype} producer authority must be {entry['producer_authority']}")

        consumer = contract["consumer"]
        if entry["consumer"] != "DOMAIN_DEPENDENT" and consumer["repo"] != entry["consumer"]:
            raise ContractValidationError(f"{ctype} consumer repo must be {entry['consumer']}")
        if entry["consumer_authority"] != "DOMAIN_DEPENDENT" and consumer["authority"] != entry["consumer_authority"]:
            raise ContractValidationError(f"{ctype} consumer authority must be {entry['consumer_authority']}")

    @staticmethod
    def _validate_authority_invariants(contract: dict[str, Any]) -> None:
        ctype = contract["contract_type"]
        producer = contract["producer"]
        auth = contract["authorization"]

        if producer["repo"] == "Shtenco/agi_nexus" and auth["decision"] not in {"PROPOSAL_ONLY", "NOT_REQUIRED"}:
            raise ContractValidationError("NEXUS cannot grant execution authority")

        if ctype in {"FinancialCommitmentArtifact", "ReconciledTradingResult", "BudgetAccountingRecognition", "ProjectUnderwritingDecision"}:
            if producer["repo"] != "Shtenco/synergy_financial_os":
                raise ContractValidationError(f"{ctype} must be produced by Financial OS")

        if ctype in {"SettlementEvidence", "BudgetSettlementEvidence"}:
            if producer["repo"] != "Shtenco/synergy_pay_system":
                raise ContractValidationError(f"{ctype} must be produced by MetaPay")

        if ctype == "ChainCommitmentReceipt" and producer["repo"] != "Shtenco/synergy_ai_blockchain":
            raise ContractValidationError("ChainCommitmentReceipt must be produced by synergy_ai_blockchain")

        if ctype == "MetaChainCheckpointProof" and producer["repo"] != "Shtenco/synergy_metachain":
            raise ContractValidationError("MetaChainCheckpointProof must be produced by synergy_metachain")

    @staticmethod
    def validate_chain(contracts: list[dict[str, Any]]) -> None:
        if not contracts:
            raise ContractValidationError("chain is empty")
        correlation = contracts[0]["correlation_id"]
        previous_id = None
        for index, contract in enumerate(contracts):
            if contract["correlation_id"] != correlation:
                raise ContractValidationError("correlation_id changed inside chain")
            if index == 0:
                if contract.get("causation_id") is not None:
                    raise ContractValidationError("first contract in chain must have null causation_id")
            else:
                if contract.get("causation_id") != previous_id:
                    raise ContractValidationError("causation_id does not reference previous contract")
            previous_id = contract["contract_id"]
