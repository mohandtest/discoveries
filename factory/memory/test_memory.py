#!/usr/bin/env python3
"""Tests for factory memory (run: python3 factory/memory/test_memory.py).

Uses a throwaway DB via FACTORY_MEM_DB; covers the epistemic law:
sentinel-safe consolidation of kinds, evidence warnings, superseding,
failure-aware retrieval ordering, and negative terminal states.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEM = HERE / 'memory.py'


def run(*args, db):
    env = dict(os.environ, FACTORY_MEM_DB=str(db))
    r = subprocess.run([sys.executable, str(MEM), *args],
                       capture_output=True, text=True, env=env)
    return r


def main():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / 'test.db'
        assert run('init', db=db).returncode == 0
        assert db.exists()

        # add + id echo
        r = run('add', '--kind', 'observation', '--text',
                'hash clustering bug inflated exact timings above n=32',
                '--pass', '1', '--source', 'fpras.c', db=db)
        assert r.returncode == 0 and 'finding #1' in r.stdout, r.stdout

        # conclusion without evidence -> warning
        r = run('add', '--kind', 'conclusion', '--text',
                'exact DP is slow', '--pass', '1', db=db)
        assert 'WARNING' in r.stderr and '--evidence' in r.stderr, r.stderr

        # search finds by keyword
        r = run('search', 'hash clustering', db=db)
        assert 'finding' in r.stdout or '#1' in r.stdout, r.stdout
        assert '#1' in r.stdout, r.stdout

        # failure-aware ordering: lesson pinned before plain observation
        run('add', '--kind', 'lesson', '--text',
            'one hash function everywhere; hash clustering cost weeks',
            '--pass', '1', '--evidence', '1', db=db)
        run('add', '--kind', 'observation', '--text',
            'hash table load factor measured at 25 percent', '--pass', '2',
            db=db)
        r = run('similar', 'hash', db=db)
        lines = r.stdout.splitlines()
        ids = [ln.split('#')[1].split(' ')[0] for ln in lines if '#' in ln]
        assert ids[0] == '3', f'expected lesson #3 pinned first, got {ids}'

        # superseding chain + show
        r = run('add', '--kind', 'conclusion', '--text',
                'corrected: timings were inflated; exact DP is fast',
                '--pass', '1', '--status', 'supported', '--supersedes', '2',
                '--evidence', '1', db=db)
        assert 'finding #5' in r.stdout, r.stdout
        r = run('show', '2', db=db)
        assert 'superseded by: #5' in r.stdout, r.stdout
        r = run('show', '5', db=db)
        assert 'supersedes: #2' in r.stdout and 'evidence: #1' in r.stdout

        # negative terminal states are first-class
        r = run('experiment', '--name', 'head-to-head vs incumbent',
                '--pass', '3', '--status', 'NO_ADVANTAGE',
                '--provenance', 'seed=42', db=db)
        assert 'experiment #1' in r.stdout and 'NO_ADVANTAGE' in r.stdout
        r = run('experiment', '--name', 'bad', '--pass', '3',
                '--status', 'WAT', db=db)
        assert r.returncode != 0  # invalid status rejected

        # sources persisted
        r = run('show', '1', db=db)
        assert 'fpras.c' in r.stdout

    print('test_memory: all assertions passed')


if __name__ == '__main__':
    main()
