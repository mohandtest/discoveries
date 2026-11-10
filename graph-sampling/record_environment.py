#!/usr/bin/env python3
"""Record source/input/result hashes without importing any optional sampler."""
import hashlib
import importlib.metadata
import json
import platform
import subprocess
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    paths = sorted(list(Path('.').glob('*.py')) + [Path('requirements-research.txt')])
    data = sorted(p for p in Path('data').iterdir() if p.is_file())
    artifacts = sorted(p for p in Path('results').rglob('*') if p.is_file() and p.name!='environment.json')
    try:
        nx_version = importlib.metadata.version('networkx')
    except importlib.metadata.PackageNotFoundError:
        nx_version = None
    report = dict(python=platform.python_version(),implementation=platform.python_implementation(),
                  platform=platform.platform(),machine=platform.machine(),networkx=nx_version,
                  base_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  source_sha256={str(p):digest(p) for p in paths},
                  input_sha256={str(p):digest(p) for p in data},
                  artifact_sha256={str(p):digest(p) for p in artifacts},
                  note='Source hashes identify working-tree code, not just the base commit. Runtime fields vary. No server was used.')
    Path('results/environment.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    main()
