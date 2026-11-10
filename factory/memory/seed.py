#!/usr/bin/env python3
"""Seed the factory memory with the founding rows (passes #1–2).

Idempotent: skips if findings already exist. Run after `memory.py init`
on a fresh clone so failure-aware retrieval works from day one.

Epistemic discipline here is the point: observations carry provenance;
the superseded early-crossover claim stays in the DB (superseded, not
deleted); the sweep law is stored as an open hypothesis with its
evidence linked; kills are decisions with their arithmetic in the text.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memory  # noqa: E402

db = memory.connect()
if db.execute('SELECT COUNT(*) FROM findings').fetchone()[0]:
    n = db.execute('SELECT COUNT(*) FROM findings').fetchone()[0]
    print(f'memory already seeded ({n} findings) -- skipping')
    sys.exit(0)

S = 'graph-sampling/results/MIXING_RESULTS.md'
F = 'fpras-benchmark/README.md'


def add(kind, text, pass_=None, status='open', evidence=None,
        supersedes=None, sources=()):
    fid, warns = memory.add_finding(db, kind, text, pass_=pass_,
                                    status=status, evidence=evidence,
                                    supersedes=supersedes, sources=sources)
    for w in warns:
        print(f'WARNING (#{fid}): {w}', file=sys.stderr)
    return fid


# --- Pass #1: FPRAS for counting perfect matchings -------------------
p1_obs_truth = add(
    'observation',
    'Algorithm #1 exact ground truth: G(44,0.5) s42 has '
    '38,960,201,918,564,595,040 perfect matchings; exact reachable-state '
    'DP: 1217.5 s, 1,129,482,570 reachable states; reproduced '
    'bit-identically in an independent rerun.', pass_='1',
    sources=[F, 'benchmarks/overnight/campaign1/',
             'env: 24-core server, 128-bit counts'])
p1_obs_cov = add(
    'observation',
    '600-run FPRAS validation at eps=0.25: coverage 84-93.5% vs nominal '
    '95% (z=+0.48 at n=44); sparse ladders 16-25% -- the guarantee shape '
    'fails on sparse instances (negative result).', pass_='1',
    sources=[F, 'benchmarks/overnight/campaign2/'])
p1_obs_hash = add(
    'observation',
    'FAILURE: fpras.c hash-clustering bug -- a hash function that '
    'respected structured keys silently clustered; inflated every exact '
    'timing above n~32 and masqueraded as an algorithmic slowdown for '
    'weeks.', pass_='1', status='abandoned',
    sources=[F + ' (correction section)', 'commit history: root-cause '
             'needed profiles + git archaeology + a control experiment'])
p1_concl_old = add(
    'conclusion',
    'EARLY CLAIM: exact DP impractical above n~32; FPRAS ~1,100x faster '
    'at n=40.', pass_='1', status='superseded',
    evidence=p1_obs_hash)
p1_concl_fix = add(
    'conclusion',
    'CORRECTED: exact DP practical through n=44 (0.2 s at n=24, 123 s at '
    'n=40, 1217.5 s at n=44); FPRAS ~1,270x faster at n=44 and necessary '
    'beyond (n=48 exact needs >400 GiB, RAM-infeasible).',
    pass_='1', status='supported', evidence=p1_obs_truth,
    supersedes=p1_concl_old,
    sources=[F + ' (correction section)'])
add('decision',
    'Pre-launch subagent audit caught a uint64 count overflow at n>=44 '
    '(would have corrupted the headline result) -> 128-bit counts + '
    '24-byte slots; 128-bit pipe protocol verified above 2^64.',
    pass_='1', sources=['commit 470f1ab context', 'AGENTS.md protocol'])
add('lesson',
    'One hash function everywhere; identical probe paths in put/get; '
    'treat silent performance failure from data-structure assumptions '
    'as a real failure class; cross-verify with an independent '
    'implementation.', pass_='1', evidence=p1_obs_hash)
add('lesson',
    'Replica/dependent-run standard errors understate true error (an '
    '8-replica run once read 5 sigma low) -- accuracy claims need many '
    'genuinely independent runs.', pass_='1', evidence=p1_obs_cov)
add('lesson',
    'Exact ground truth must precede approximation claims; report '
    'measured coverage against nominal honestly, including misses.',
    pass_='1', evidence=p1_obs_cov)

# --- Pass #2: degree-preserving graph sampling (#131) ----------------
p2_obs_sweeps = add(
    'observation',
    'Switch chain (#131) exact mixing, completed rows: t(1/4) = '
    '50/250/250/500/1000 at n=6/8/9/10/11 (d=2..4, checkpoint units); '
    'sweep ratios t(1/4)/C(n,4) = 3.33/3.57/1.98/2.38/3.03.',
    pass_='2', sources=[S, 'graph-sampling/results/mixing/'])
p2_hyp = add(
    'hypothesis',
    'SWEEP LAW: t_mix(1/4) ~= 1.5-4 passes over the proposal space '
    'C(n,4) (checkpoint-grid upper bounds), across densities and '
    'heterogeneous sequences. Pre-registered bands for n=10 d=3/d=4 '
    '(420-840), n=11 (660-1320), n=12 (990-1980), het cases -- stated '
    'before outcomes (commit 1d32259).', pass_='2',
    evidence=p2_obs_sweeps, sources=[S, 'commit 1d32259'])
add('observation',
    'n=11 d=2 first frontier outcome: t(1/4)=1000 vs predicted 660-1320 '
    '-- IN BAND (3.03 sweeps). t(0.05)=1000 fell below its secondary '
    'band (1300-2600): faster tail than predicted; a prediction miss in '
    'the favorable direction, reported as such.', pass_='2',
    evidence=p2_hyp, sources=['graph-sampling/results/mixing/n11d2.txt'])
add('observation',
    'R-hat convergence gate is miscalibrated on the switch chain: '
    'passes 10-12% of the time when TV is genuinely bad; fails on '
    'near-stationary heterogeneous cases; nominal 95% t-intervals cover '
    'truth only 82-99/100 (1,800-trial calibration).', pass_='2',
    sources=['graph-sampling/STUDY_REPORT.md'])
add('observation',
    'Real networks: dolphins 95 triangles vs null 34.28 +/- 4.94, '
    '0/800,000 upper-tail draws (z=12.3) -- degrees do NOT explain '
    'dolphin clustering. Karate: tail 12.6% (z=1.2) -- degrees DO '
    'explain karate clustering.', pass_='2',
    sources=['graph-sampling/results/dolphins_tail.json', S])
add('observation',
    'Burn-in 0->125k attempts moves null means <=0.5 triangles; '
    'thin=1 biases karate by -1.39 (~5x MCSE): budget goes to thinning '
    'and chains, not burn-in.', pass_='2',
    sources=['graph-sampling/results/burn_spacing.json', S])
add('observation',
    'switch_exact.c verified against independent Python '
    '(exact_mixing.py) to six digits at n=6 d=2 and n=8 d=2; state '
    'counts match enumeration at n=6-10; complement symmetry '
    'd<->n-1-d exact (n8d3 == n8d4: 19,355 states, identical times).',
    pass_='2', sources=[S, 'graph-sampling/switch_exact.c'])
add('decision',
    'Kills decided on measured arithmetic before outcomes: n10d3 killed '
    '29 min before its 90-min cap (7.6 s/step x fitted t(0.05)~780 '
    'steps); n10d4 killed after enumeration (66,462,606 states, ~44 '
    's/step at 22 workers); n=12 t(0.05) capped by cost model (10-30 '
    'h/start) -> --t25only rows. ~2.5 h zero-yield grinding avoided.',
    pass_='2',
    sources=['graph-sampling/results/mixing/n10d4.err',
             'graph-sampling/results/mixing/n10d3.err', 'commit 51f4034'])
p2_obs_audit = add(
    'observation',
    'Pre-close adversarial audit of the frozen campaign: 13 findings, '
    'verdict FIX-FIRST -- zero correctness findings in '
    'enumeration/kernel/hash/propagation/parallelism; every blocker '
    'was in the reporting/orchestration layer (consolidation crash on '
    'sentinel t05=-1, wrong n^4/3 constant, checkpoint-vs-hitting-time '
    'definition, uncommitted cap evidence). All fixed pre-close '
    '(commit 313c622).', pass_='2',
    sources=['commit 313c622'])
add('lesson',
    'Audits bite in the reporting and orchestration layer, exactly '
    'where the implementer\'s own tests pass: test consolidation '
    'against sentinel/partial rows BEFORE the rows exist; state '
    'definitions and constants precisely in headline claims.',
    pass_='2', evidence=p2_obs_audit)
add('lesson',
    'Server-side state (nohup supervisors, DONE.flags, logs) survives '
    'harness restarts; local sleep-watchers are conveniences, never '
    'the record.', pass_='2')
add('decision',
    'STANDING USER DIRECTIVE: novelty is the primary criterion for '
    'what this project takes on; market x implementability are gates.',
    pass_='2', sources=['factory/STATE.md Directives, 2026-11-10'])

# --- Experiments (linking hypotheses to runs) ------------------------
memory.add_experiment(
    db, 'FPRAS exact-vs-approx crossover + coverage campaign', '1',
    hypothesis=None, status='SUPPORTED',
    provenance='24-core server; saved graphs g24..g64; 920+200 trials; '
               'benchmarks/overnight/campaign{1,2}')
memory.add_experiment(
    db, 'Exact TV mixing ladder n=6..12 (switch chain #131)', '2',
    hypothesis=p2_hyp, status='RUNNING',
    provenance='22 cores; instances are degree sequences; '
               'results/mixing/*.txt; pre-registration commit 1d32259')

n = db.execute('SELECT COUNT(*) FROM findings').fetchone()[0]
e = db.execute('SELECT COUNT(*) FROM experiments').fetchone()[0]
print(f'seeded: {n} findings, {e} experiments -> {memory.DB}')
