#!/usr/bin/env python3
"""Cross-repository SYNERGY trading truth path verifier.

Expected layout under SYNERGY_REPOS_ROOT:
  synergy_midas_ai/
  synergy_quantlab/
  synergy_riskguard/
  synergy_trademux/
  synergy_pay_system/
  synergy_financial_os/
  synergy_ai_blockchain/

The harness does not execute live trades. It verifies the adapter chain and
fail-closed invariants across independently owned repositories.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(os.environ.get("SYNERGY_REPOS_ROOT", ".")).resolve()
HERE = Path(__file__).resolve().parent
LOCK = json.loads((HERE / "integration_lock_v1.json").read_text(encoding="utf-8"))

PY_TESTS = {
    "synergy_midas_ai": ["tests/test_portfolio_decision_contract.py"],
    "synergy_quantlab": ["tests/test_synergy_contracts.py"],
    "synergy_riskguard": ["tests/test_synergy_contracts.py"],
    "synergy_trademux": ["tests/test_synergy_contracts.py"],
    "synergy_pay_system": ["tests/test_synergy_contracts.py"],
    "synergy_financial_os": ["tests/test_accounting_recognition_contract.py"],
}

def run(cmd: list[str], cwd: Path) -> None:
    print("+", " ".join(cmd), f"(cwd={cwd})")
    subprocess.run(cmd, cwd=cwd, check=True)

def verify_git_commit(repo: Path, expected: str) -> None:
    actual=subprocess.check_output(["git","rev-parse","HEAD"],cwd=repo,text=True).strip()
    if actual != expected:
        raise RuntimeError(f"{repo.name}: lock mismatch {actual} != {expected}")

def main() -> int:
    missing=[]
    by_name={}
    for item in LOCK["repositories"]:
        name=item["repo"].split("/",1)[1]
        path=ROOT/name
        by_name[name]=(path,item)
        if not path.is_dir():
            missing.append(str(path))
    if missing:
        raise SystemExit("missing checked-out repositories:\n" + "\n".join(missing))

    strict=os.environ.get("SYNERGY_VERIFY_LOCK","0")=="1"
    if strict:
        for path,item in by_name.values():
            verify_git_commit(path,item["commit"])

    for name, tests in PY_TESTS.items():
        path,_=by_name[name]
        run([sys.executable,"-m","pytest","-q",*tests],path)

    blockchain,_=by_name["synergy_ai_blockchain"]
    run(["cargo","test","domain_commitment","--lib"],blockchain)

    print("SYNERGY TRADING TRUTH PATH: ADAPTER E2E PASS")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
