from typing import List
from .utils import bin_fill
import pulp

def first_fit_decreasing(items: List[float]) -> List[List[float]]:
    """Simple FFD offline solver (fast, practical)."""
    items_sorted = sorted(items, reverse=True)
    bins = []
    for x in items_sorted:
        placed = False
        for b in bins:
            if bin_fill(b) + x <= 1.0 + 1e-12:
                b.append(x)
                placed = True
                break
        if not placed:
            bins.append([x])
    return bins

def exact_ilp(items: List[float]) -> List[List[float]]:
    """
    Exact packing via set-partition ILP (only for small n, e.g., n<=20).
    We construct all feasible subsets and solve a set-cover ILP.
    """
    n = len(items)
    if n > 22:
        # fallback to FFD for performance
        return first_fit_decreasing(items)

    # enumerate feasible subsets
    subsets = []
    for mask in range(1, 1<<n):
        subset = []
        s = 0.0
        for i in range(n):
            if (mask>>i)&1:
                s += items[i]
                if s > 1.0 + 1e-12:
                    break
                subset.append(i)
        else:
            subsets.append((mask, subset))

    prob = pulp.LpProblem('setcover', pulp.LpMinimize)
    y = {mask: pulp.LpVariable(f"y_{mask}", cat='Binary') for mask, _ in subsets}

    # objective: minimize sum y_mask
    prob += pulp.lpSum(y[mask] for mask,_ in subsets)

    # coverage constraints: each item must be in at least one chosen subset
    for i in range(n):
        prob += pulp.lpSum(y[mask] for mask, subset in subsets if i in subset) >= 1

    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    chosen_bins = []
    for mask, subset in subsets:
        if pulp.value(y[mask]) > 0.5:
            chosen_bins.append([items[i] for i in subset])
    return chosen_bins

# placeholder to plug in AFPTAS: in practice you'd implement the AFPTAS here
def offline_AU(items: List[float], mode='ffd') -> List[List[float]]:
    if mode == 'ffd':
        return first_fit_decreasing(items)
    elif mode == 'exact':
        return exact_ilp(items)
    else:
        raise ValueError("Unknown AU mode")
