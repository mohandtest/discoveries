# Analysis standards

- **Ground truth**: exact values on identical saved instances, same
  machine; instances committed to the repo.
- **Coverage**: fraction of genuinely independent runs whose intervals
  contain truth, at stated ε; nominal vs measured stated together.
- **Bias**: z = (estimate − truth)/SD, with conventions stated (which
  SD, population vs sample).
- **Tail bounds**: report 1/(draws+1)-style bounds for zero-hit
  events; say what normal extrapolations lean on.
- **Error understatement**: replica/dependent-run SEs understate true
  error (an 8-replica run once read 5σ low) — accuracy claims need
  many genuinely independent runs.
- **Measured vs extrapolated**: never let them blur — cap decisions
  and their evidence go in the report; rows measured at reduced
  thresholds/modes are labeled as such.
- **Conventions**: every reference mean, SD convention, and
  bias-vs-reference field must be self-consistent within one doc
  (an audit caught two conventions mixed in one paragraph).
- **Negative results are results.**
