from bisect import bisect_right, insort
from typing import List, Tuple

def max_upright_matching(minus: List[Tuple[float,float]], plus: List[Tuple[float,float]]) -> int:
    """
    minus: list of tuples (x_coord, y_coord)  (these are '-' points)
    plus: list of tuples (x_coord, y_coord)   (these are '+' points)
    Returns number of unmatched total points (or unmatched plus if context)
    Implementation: process by increasing x; when minus arrives, add its y to multiset;
    when plus arrives, match to largest y <= plus.y if exists.
    """
    # Create combined events: (x, type, y). type: -1 for minus (arrived earlier), +1 for plus
    events = []
    for x,y in minus:
        events.append((x, 0, y))  # 0 for minus
    for x,y in plus:
        events.append((x, 1, y))   # 1 for plus, ensure same-x ordering: minus before plus?
    events.sort(key=lambda t: (t[0], t[1]))  # process minus before plus at same x

    multiset = []  # sorted list of minus y's currently unmatched
    matches = 0
    for x, typ, y in events:
        if typ == 0:
            # minus arrives: add y
            insort(multiset, y)
        else:
            # plus arrives: find largest y <= plus.y
            idx = bisect_right(multiset, y) - 1
            if idx >= 0:
                # match
                multiset.pop(idx)
                matches += 1
            else:
                # unmatched plus
                pass
    # unmatched points can be computed if needed:
    unmatched_plus = len(plus) - matches
    unmatched_minus = len(minus) - matches
    return unmatched_plus, unmatched_minus
