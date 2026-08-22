from __future__ import annotations
import argparse, hashlib, json, os, pathlib, stat, zipfile
from typing import Iterable

FIXED_TIME=(1980,1,1,0,0,0)
MODE_FILE=0o100644
SCHEMA='synergy.deterministic-python-zipapp/v1'

def canonical_json(v):
    return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')

def sha256(b): return hashlib.sha256(b).hexdigest()

def zip_info(name):
    zi=zipfile.ZipInfo(name,FIXED_TIME)
    zi.create_system=3
    zi.compress_type=zipfile.ZIP_STORED
    zi.external_attr=MODE_FILE << 16
    zi.internal_attr=0
    zi.extra=b''
    zi.comment=b''
    return zi

def build(output: pathlib.Path, root: pathlib.Path, mappings: list[tuple[str,str]], launcher: bytes, metadata: dict):
    entries=[]
    files=[]
    for src_rel, arc in mappings:
        p=root/src_rel
        data=p.read_bytes()
        entries.append((arc,data))
        files.append({'path':arc,'sha256':sha256(data),'size':len(data)})
    entries.append(('__main__.py',launcher))
    files.append({'path':'__main__.py','sha256':sha256(launcher),'size':len(launcher)})
    manifest={'schema':SCHEMA,'metadata':metadata,'files':sorted(files,key=lambda x:x['path'])}
    manifest_bytes=canonical_json(manifest)+b'\n'
    entries.append(('SYNERGY_ARTIFACT_MANIFEST.json',manifest_bytes))
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_STORED,allowZip64=False,strict_timestamps=True) as zf:
        zf.comment=b''
        for name,data in sorted(entries,key=lambda x:x[0]):
            zf.writestr(zip_info(name),data)
    out=output.read_bytes()
    return {'artifact_sha256':sha256(out),'artifact_size':len(out),'manifest_sha256':sha256(manifest_bytes),'file_count':len(entries)}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('output')
    args=ap.parse_args(); spec=json.loads(pathlib.Path(args.spec).read_text())
    r=build(pathlib.Path(args.output),pathlib.Path(spec['root']),[(x['source'],x['archive']) for x in spec['files']],spec['launcher'].encode('utf-8'),spec['metadata'])
    print(json.dumps(r,sort_keys=True))
