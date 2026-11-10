#!/usr/bin/env python3
"""Structured operational memory for the algorithm factory.

SQLite + FTS5: observations, hypotheses, conclusions, decisions,
lessons, experiments, provenance. Git + Markdown stay canonical for
research artifacts; this is the retrieval layer that survives agent
sessions and feeds briefs (architecture: factory/README.md).

Usage:
  memory.py init
  memory.py add --kind observation --text "..." [--pass 2]
         [--status open] [--evidence ID] [--supersedes ID]
         [--source "path or commit"] [--source ...]
  memory.py search QUERY        # keyword search (FTS5, prefix terms)
  memory.py similar QUERY       # failure-aware: failures/lessons pinned first
  memory.py show ID
  memory.py experiment --name ... --pass ... [--hypothesis ID]
         [--status RUNNING|SUPPORTED|REFUTED|INCONCLUSIVE|NO_ADVANTAGE|INCORRECT]
         [--provenance "..."]

DB: factory/memory/factory.db (override with FACTORY_MEM_DB).
Founding rows: python3 seed.py (idempotent; skips if findings exist).
"""
import argparse
import os
import re
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = Path(os.environ.get('FACTORY_MEM_DB') or HERE / 'factory.db')
SCHEMA = HERE / 'schema.sql'
KINDS = ('observation', 'hypothesis', 'conclusion', 'decision', 'lesson')
EXP_STATUS = ('RUNNING', 'SUPPORTED', 'REFUTED', 'INCONCLUSIVE',
              'NO_ADVANTAGE', 'INCORRECT')
PIN_SQL = ('CASE WHEN f.kind IN (\'lesson\',\'decision\') '
           'OR f.status IN (\'refuted\',\'superseded\',\'abandoned\') '
           'THEN 0 ELSE 1 END')


def connect():
    if not DB.exists():
        sys.exit(f'no memory DB at {DB} -- run: memory.py init')
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    db = sqlite3.connect(DB)
    db.executescript(SCHEMA.read_text())
    try:
        db.execute('CREATE VIRTUAL TABLE IF NOT EXISTS findings_fts '
                   'USING fts5(text, findings_id UNINDEXED)')
        has_fts = True
    except sqlite3.Error:
        has_fts = False
    db.commit()
    print(f'initialized {DB} (fts5={"yes" if has_fts else "NO -- LIKE fallback"})')
    return db


def add_finding(db, kind, text, pass_=None, status='open', evidence=None,
                supersedes=None, sources=()):
    warnings = []
    if kind == 'conclusion' and evidence is None:
        warnings.append('conclusion without --evidence: conclusions must '
                        'cite the observations they rest on')
    cur = db.execute(
        'INSERT INTO findings (kind, status, pass, text, evidence, '
        'supersedes) VALUES (?,?,?,?,?,?)',
        (kind, status, pass_, text, evidence, supersedes))
    fid = cur.lastrowid
    for ref in sources:
        db.execute('INSERT OR IGNORE INTO sources (ref) VALUES (?)', (ref,))
        sid = db.execute('SELECT id FROM sources WHERE ref=?',
                         (ref,)).fetchone()[0]
        db.execute('INSERT OR IGNORE INTO links VALUES (?,?)', (fid, sid))
    try:
        db.execute('INSERT INTO findings_fts (text, findings_id) '
                   'VALUES (?,?)', (text, fid))
    except sqlite3.Error:
        pass
    db.commit()
    return fid, warnings


def add_experiment(db, name, pass_, hypothesis=None, status='RUNNING',
                   provenance=None):
    cur = db.execute(
        'INSERT INTO experiments (pass, name, hypothesis, status, '
        'provenance) VALUES (?,?,?,?,?)',
        (pass_, name, hypothesis, status, provenance))
    db.commit()
    return cur.lastrowid


def _terms(query):
    return [t for t in re.split(r'\W+', query) if t]


def match_rows(db, query, failure_first=False):
    terms = _terms(query)
    if not terms:
        return []
    order = f'{PIN_SQL}, t.rank' if failure_first else 't.rank'
    try:
        q = ' OR '.join(f'{t}*' for t in terms)
        return db.execute(
            'SELECT f.* FROM findings f JOIN findings_fts t '
            'ON t.findings_id = f.id WHERE t.text MATCH ? '
            f'ORDER BY {order} LIMIT 25', (q,)).fetchall()
    except sqlite3.Error:
        like = ' OR '.join('f.text LIKE ?' for _ in terms)
        order = PIN_SQL if failure_first else 'f.id'
        return db.execute(
            f'SELECT f.* FROM findings f WHERE {like} '
            f'ORDER BY {order} LIMIT 25',
            [f'%{t}%' for t in terms]).fetchall()


def sources_of(db, fid):
    return [r['ref'] for r in db.execute(
        'SELECT s.ref FROM sources s JOIN links l ON l.source_id = s.id '
        'WHERE l.finding_id = ?', (fid,))]


def print_rows(db, rows, failure_first=False):
    if not rows:
        print('(no matches)')
        return
    if failure_first:
        print('--- failures/lessons first: what went wrong, on what '
              'evidence ---')
    for r in rows:
        pin = (r['kind'] in ('lesson', 'decision')
               or r['status'] in ('refuted', 'superseded', 'abandoned'))
        mark = '! ' if pin else '  '
        print(f"{mark}#{r['id']} [{r['kind']}/{r['status']}] pass={r['pass']}")
        print(f"     {r['text']}")
        srcs = sources_of(db, r['id'])
        if srcs:
            print(f"     sources: {'; '.join(srcs)}")


def show(db, fid):
    r = db.execute('SELECT * FROM findings WHERE id=?', (fid,)).fetchone()
    if not r:
        sys.exit(f'no finding #{fid}')
    print(f"#{r['id']} kind={r['kind']} status={r['status']} "
          f"pass={r['pass']} created={r['created']}")
    print(r['text'])
    if r['evidence']:
        e = db.execute('SELECT kind, text FROM findings WHERE id=?',
                       (r['evidence'],)).fetchone()
        print(f"  evidence: #{r['evidence']} [{e['kind']}] {e['text']}")
    if r['supersedes']:
        s = db.execute('SELECT kind, status, text FROM findings WHERE id=?',
                       (r['supersedes'],)).fetchone()
        print(f"  supersedes: #{r['supersedes']} [{s['kind']}/{s['status']}] "
              f"{s['text']}")
    for s in db.execute('SELECT id, kind, status, text FROM findings '
                        'WHERE supersedes=?', (fid,)):
        print(f"  superseded by: #{s['id']} [{s['kind']}/{s['status']}] "
              f"{s['text']}")
    srcs = sources_of(db, fid)
    if srcs:
        print(f"  sources: {'; '.join(srcs)}")
    for e in db.execute('SELECT id, name, status FROM experiments '
                        'WHERE hypothesis=?', (fid,)):
        print(f"  experiment #{e['id']}: {e['name']} [{e['status']}]")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest='cmd', required=True)

    sub.add_parser('init')

    a = sub.add_parser('add')
    a.add_argument('--kind', required=True, choices=KINDS)
    a.add_argument('--text', required=True)
    a.add_argument('--pass', dest='pass_')
    a.add_argument('--status', default='open')
    a.add_argument('--evidence', type=int)
    a.add_argument('--supersedes', type=int)
    a.add_argument('--source', action='append')

    s = sub.add_parser('search')
    s.add_argument('query', nargs='+')

    s = sub.add_parser('similar')
    s.add_argument('query', nargs='+')

    s = sub.add_parser('show')
    s.add_argument('id', type=int)

    e = sub.add_parser('experiment')
    e.add_argument('--name', required=True)
    e.add_argument('--pass', dest='pass_', required=True)
    e.add_argument('--hypothesis', type=int)
    e.add_argument('--status', default='RUNNING', choices=EXP_STATUS)
    e.add_argument('--provenance')

    args = ap.parse_args()
    if args.cmd == 'init':
        init_db()
        return
    db = connect()
    if args.cmd == 'add':
        fid, warnings = add_finding(
            db, args.kind, args.text, pass_=args.pass_, status=args.status,
            evidence=args.evidence, supersedes=args.supersedes,
            sources=args.source or ())
        print(f'finding #{fid} ({args.kind}, status={args.status})')
        for w in warnings:
            print(f'WARNING: {w}', file=sys.stderr)
    elif args.cmd in ('search', 'similar'):
        print_rows(db, match_rows(db, ' '.join(args.query),
                                  failure_first=(args.cmd == 'similar')),
                   failure_first=(args.cmd == 'similar'))
    elif args.cmd == 'show':
        show(db, args.id)
    elif args.cmd == 'experiment':
        eid = add_experiment(db, args.name, args.pass_, args.hypothesis,
                             args.status, args.provenance)
        print(f'experiment #{eid} ({args.name}, status={args.status})')


if __name__ == '__main__':
    main()
