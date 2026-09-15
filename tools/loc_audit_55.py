#!/usr/bin/env python3
"""Exact physical source-line counter for the 55-repository Shtenco federation.

Requires GITHUB_TOKEN with read access to the private repositories.
Counts current default-branch source files from Git trees/blobs, not repository size.
Excludes common vendored/generated/build directories and binary blobs.
"""
from __future__ import annotations

import base64
import csv
import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter

OWNER = "Shtenco"
REPOS = [
"binary_quantum_theory","ai_language","synergy_pay_system","synergy_system","synergy_graph_print_money","midas_ai","agi_olga","synergy_financial_os","ai_financial_system","crypto_pump","ai_compress","synergy_meta_os","turbo_linux","midas_ai_trading_system","synergychain.github.io","synergychain","agi_nexus","qr_compress","synergynet","synergy_ai_blockchain","cold_nuclear","synergy_app","usds","cashero","shtencoauantai.github.io","blochain_budget","dlp_solver","synergy_eurasian","synergy_project","nexus_science_agent","ai_trade_terminal","3D_bars_market_structure","agi_autopilot","motherboard_xpu_xml","synergy_metachain","gguf_compress","ai_coder","print_money_synergychain","synergy_matrix_sota","sinergy-super-app","midas_lite","computer_vision_trading_metatrader_5","multi_threaded_trading_robot_with_machine_learning_python","synergy_ai_company","shttps","swap_arbitrage_metatrader_5","cross_forex_arbitrage_trading_metatrader_5","global_liquidity_dataminer","shtenco.github.io","shhts","synergy_chain_print_money","synergy_app_family","algotrading_graph_system","sinergy_app","quantum-trading_metatrader5",
]
CODE_EXT = {
'.py','.pyi','.sol','.js','.mjs','.cjs','.ts','.tsx','.jsx','.java','.kt','.kts','.go','.rs','.c','.h','.cc','.cpp','.cxx','.hpp','.hh','.cs','.fs','.fsx','.swift','.scala','.rb','.php','.lua','.r','.R','.m','.mm','.sh','.bash','.zsh','.fish','.ps1','.bat','.cmd','.sql','.html','.htm','.css','.scss','.sass','.less','.vue','.svelte','.dart','.ex','.exs','.erl','.hrl','.clj','.cljs','.groovy','.mq4','.mq5','.mqh'
}
EXCLUDE_PARTS = {'.git','node_modules','vendor','dist','build','target','.venv','venv','__pycache__','.next','.nuxt','coverage','.cache','artifacts','cache'}

TOKEN = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
if not TOKEN:
    sys.exit('Set GITHUB_TOKEN or GH_TOKEN with read access to all 55 repositories.')


def api(path: str):
    req = urllib.request.Request(
        'https://api.github.com' + path,
        headers={'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def count_repo(repo: str):
    meta = api(f'/repos/{OWNER}/{repo}')
    branch = meta['default_branch']
    tree = api(f'/repos/{OWNER}/{repo}/git/trees/{branch}?recursive=1')
    if tree.get('truncated'):
        raise RuntimeError(f'{repo}: recursive Git tree is truncated; split traversal required')
    loc = nonblank = files = 0
    by_ext = Counter()
    for item in tree.get('tree', []):
        if item.get('type') != 'blob':
            continue
        path = item['path']
        parts = path.split('/')
        if any(part in EXCLUDE_PARTS for part in parts):
            continue
        ext = os.path.splitext(path)[1]
        if ext not in CODE_EXT:
            continue
        blob = api(f"/repos/{OWNER}/{repo}/git/blobs/{item['sha']}")
        raw = base64.b64decode(blob['content']) if blob.get('encoding') == 'base64' else blob.get('content','').encode()
        if b'\x00' in raw[:4096]:
            continue
        text = raw.decode('utf-8', errors='replace')
        lines = text.splitlines()
        n = len(lines)
        nb = sum(1 for line in lines if line.strip())
        files += 1
        loc += n
        nonblank += nb
        by_ext[ext] += n
    return {'repository': repo, 'default_branch': branch, 'code_files': files, 'physical_lines': loc, 'nonblank_lines': nonblank, 'blank_lines': loc-nonblank, 'by_extension': dict(sorted(by_ext.items()))}


def main():
    rows = []
    for i, repo in enumerate(REPOS, 1):
        try:
            row = count_repo(repo)
        except urllib.error.HTTPError as e:
            row = {'repository': repo, 'error': f'HTTP {e.code}'}
        rows.append(row)
        print(f"[{i:02d}/55] {repo}: {row.get('physical_lines','ERROR')}")
    ok = [r for r in rows if 'physical_lines' in r]
    summary = {
        'schema': 'synergy.loc_audit/v1',
        'repositories_requested': len(REPOS),
        'repositories_counted': len(ok),
        'physical_lines_total': sum(r['physical_lines'] for r in ok),
        'nonblank_lines_total': sum(r['nonblank_lines'] for r in ok),
        'code_files_total': sum(r['code_files'] for r in ok),
        'repositories': rows,
    }
    with open('SYNERGY_55_LOC_REPORT.json','w',encoding='utf-8') as f:
        json.dump(summary,f,ensure_ascii=False,indent=2)
    with open('SYNERGY_55_LOC_REPORT.csv','w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f, fieldnames=['repository','default_branch','code_files','physical_lines','nonblank_lines','blank_lines','error'])
        w.writeheader()
        for r in rows:
            w.writerow({k:r.get(k,'') for k in w.fieldnames})
    print(json.dumps({k:v for k,v in summary.items() if k!='repositories'}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
