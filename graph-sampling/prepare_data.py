#!/usr/bin/env python3
"""Create fixtures, preserving labels as one-token integers with a label map.

Dolphins source zip is supplied explicitly, so reruns need no network.
"""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
import networkx as nx


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('dolphins_zip', type=Path)
    a = p.parse_args()
    graphs = {'florentine': nx.florentine_families_graph()}
    with zipfile.ZipFile(a.dolphins_zip) as z:
        graphs['dolphins'] = nx.parse_gml(z.read('dolphins.gml').decode().splitlines())
    manifest = {'networkx': nx.__version__, 'dolphins_archive_sha256': hashlib.sha256(a.dolphins_zip.read_bytes()).hexdigest(),
                'dolphins_url': 'https://websites.umich.edu/~mejn/netdata/dolphins.zip', 'retrieved_utc_date': '2026-11-10', 'datasets': {}}
    for name, g in graphs.items():
        assert not g.is_directed() and not g.is_multigraph() and not list(nx.selfloop_edges(g))
        labels = list(g)
        ids = {u:i for i,u in enumerate(labels)}
        edges = sorted(tuple(sorted((ids[u],ids[v]))) for u,v in g.edges())
        content = '# Undirected unweighted; see data/PROVENANCE.md and manifest.json\n'
        content += ''.join(f'{u} {v}\n' for u,v in edges)
        content += ''.join(f'{ids[u]}\n' for u in nx.isolates(g))
        path = Path('data') / f'{name}.edgelist'
        path.write_text(content)
        manifest['datasets'][name] = dict(nodes=len(g), edges=len(edges), labels=labels,
                                         sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    Path('data/manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    main()
