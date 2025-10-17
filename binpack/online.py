from .blueprint import blueprint_pack
from typing import List
import math

def run_full_algorithm(stream: List[float], AU_mode='ffd', X=0.2, stage_k=None):
    """
    stream: items arriving sequentially.
    If stage_k is None, use doubling trick: guess n0=100, then if items exceed guess, rebuild.
    Simpler: partition into chunks of size k (sample stage + repeated blueprint usage).
    """
    n = len(stream)
    if stage_k is None:
        # pick k = max(100, sqrt(n)) heuristic
        stage_k = max(100, int(math.sqrt(max(1,n))))
    # Stage 0 sample
    if n < 2*stage_k:
        # fallback: simple online FFD
        from .au import first_fit_decreasing
        return [stream]  # placeholder

    S1 = stream[:stage_k]
    rest = stream[stage_k:]
    bins, stats = blueprint_pack(S1, rest[:stage_k], AU_mode=AU_mode, X=X)
    # For simplicity only handle one blueprint use; production code iterates per stage
    return bins, stats
