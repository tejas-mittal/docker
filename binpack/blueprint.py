from typing import List, Tuple
from .au import offline_AU
from .upright import max_upright_matching
from .utils import bin_fill
import bisect

def split_large_small(items: List[float], X: float) -> Tuple[List[float], List[float]]:
    small = [x for x in items if x < X]
    large = [x for x in items if x >= X]
    return large, small

def blueprint_pack(S1: List[float], S2: List[float], AU_mode='ffd', X=0.2):
    """
    Implements BlueP(S2, AU, S1) per paper, simplified and practical.
    Returns final_bins list and statistics.
    """
    # 1. compute blueprint packing AU(S1)
    blueprint_bins = offline_AU(S1, mode=AU_mode)
    # Remove small items from blueprint to create proxy bins and S-slots
    # We'll identify proxy items = large items in blueprint bins
    proxy_bins = []
    S_slots = []  # list of available slot sizes (floats)
    for b in blueprint_bins:
        large_items = [x for x in b if x >= X]
        small_items = [x for x in b if x < X]
        proxy_bins.append(list(large_items))
        # slot size available in bin after removing small items = 1 - sum(large_items)
        slot = 1.0 - sum(large_items)
        if slot > 1e-12:
            S_slots.append(slot)

    # normalize S_slots as list (we will pack small items using NF into S_slots)
    # Represent S_slots as bins with remaining capacity to pack small items
    S_bins = S_slots[:]  # remaining capacities
    # We'll also keep a list of closed-large bins representing where we placed proxy large items
    # Now pack S2:
    large_S2, small_S2 = split_large_small(S2, X)

    # Process large items: for each large item, try to find a proxy in proxy_bins
    # Represent proxies as list of proxies sizes (their original size) along with bin index.
    proxies = []
    for i, pb in enumerate(proxy_bins):
        for p in pb:
            # coordinate: (x=index or order, y=size). For upright matching we need order coordinate.
            proxies.append((i, p))  # x = i, y = p
    # For S2 large items, create plus points with their own order coordinates (we can use their order in S2)
    plus = [(i, v) for i, v in enumerate(large_S2)]
    minus = [(i, v) for i, v in enumerate([p for _, p in proxies])]

    # Upright matching: produce unmatched count and which matched — simplified version: do greedy matching by sorting proxies and larges by size
    # Simpler practical approach: sort proxies ascending, for each large in ascending try to replace smallest proxy > large
    proxies_sizes = sorted([p for _,p in proxies])
    used_bins = [list(b) for b in proxy_bins]  # copy
    unmatched_large_bins = []
    import bisect
    for v in sorted(large_S2):
        # find smallest proxy strictly > v
        idx = bisect.bisect_right(proxies_sizes, v)
        if idx < len(proxies_sizes):
            # replace that proxy (we take it out)
            proxies_sizes.pop(idx)
            # Use that bin (we don't open new bin)
        else:
            # open a new bin for this large item (closed)
            unmatched_large_bins.append([v])

    # Now pack small items into existing S_bins (Next-Fit on available S_bins)
    # S_bins currently have capacities; pack small_S2 sequentially into these slots, filling them greedily.
    small_bins = []  # new S-bins opened
    # Use existing S_bins as active bins
    active = S_bins[:]
    for s in small_S2:
        placed = False
        # try to fit into any active S_slot (best-fit is fine)
        # try to place into the slot with smallest leftover >= s (best-fit)
        best_idx = None
        best_rem = None
        for j, rem in enumerate(active):
            if rem + 1e-12 >= s:
                rem_after = rem - s
                if best_rem is None or rem_after < best_rem:
                    best_rem = rem_after
                    best_idx = j
        if best_idx is not None:
            active[best_idx] -= s
            placed = True
        else:
            # open a new small bin (capacity 1), pack s, then it's an S_bin with remaining 1-s
            small_bins.append([s])
            active.append(1.0 - s)

    # Combine everything: used bins = blueprint bins (proxy bins count) + unmatched_large_bins + small_bins (new ones)
    # For simplicity we return counts and a combined list
    combined_bins = []
    # reconstruct blueprint bins: proxy_bins plus their small items from S1 were removed; for accounting we count original AU(S1)
    combined_bins.extend(blueprint_bins)  # count blueprint cost
    combined_bins.extend(unmatched_large_bins)
    combined_bins.extend(small_bins)
    stats = {
        'blueprint_bins': len(blueprint_bins),
        'unmatched_large_bins': len(unmatched_large_bins),
        'new_small_bins': len(small_bins),
        'total_bins': len(combined_bins)
    }
    return combined_bins, stats
