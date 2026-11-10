"""Conservative descriptive diagnostics; none can certify stationarity."""
import math
import statistics as st


def split_rhat(chains):
    half = len(chains[0]) // 2
    if half < 2:
        return None
    splits = [part for c in chains for part in (c[:half], c[-half:])]
    within = st.mean(st.variance(c) for c in splits)
    if within == 0:
        return None  # constant trajectories cannot establish convergence
    between = half * st.variance([st.mean(c) for c in splits])
    return math.sqrt((half - 1) / half + between / (half * within))


def batch_ess(values):
    """Nonoverlapping sqrt(n) batch-means ESS, descriptive and capped at n.

    Returns None for constant data or too few batches; not an independence test.
    """
    size = math.isqrt(len(values))
    count = len(values) // max(size, 1)
    if size < 2 or count < 4 or st.variance(values) == 0:
        return None
    means = [st.mean(values[i*size:(i+1)*size]) for i in range(count)]
    asymptotic_variance = size * st.variance(means)
    if asymptotic_variance == 0:
        return None
    return min(len(values), len(values) * st.variance(values) / asymptotic_variance)


def summarize(chains, observed):
    means = [st.mean(c) for c in chains]
    tails = [st.mean(x >= observed for x in c) for c in chains]
    hits = sum(x >= observed for c in chains for x in c)
    total = sum(map(len, chains))
    return dict(mean=st.mean(means), mcse_mean=st.stdev(means)/math.sqrt(len(means)),
                upper_tail=st.mean(tails),
                mcse_tail=None if hits in (0, total) else st.stdev(tails)/math.sqrt(len(tails)),
                tail_hits=hits, draws=total, split_rhat=split_rhat(chains),
                batch_ess_per_chain=[batch_ess(c) for c in chains],
                zero_tail_variation=hits in (0, total))
