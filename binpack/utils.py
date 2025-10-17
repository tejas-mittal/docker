import random
import numpy as np
from typing import List

def gen_iid_items(n:int, dist='uniform', **kwargs) -> List[float]:
    if dist == 'uniform':
        a = kwargs.get('a', 0.0)
        b = kwargs.get('b', 1.0)
        return list(np.random.uniform(a,b,n))
    elif dist == 'two_point':
        # simple mixture: small p of large values
        p = kwargs.get('p', 0.2)
        return [kwargs.get('v1',0.25) if random.random() > p else kwargs.get('v2',0.75) for _ in range(n)]
    else:
        raise ValueError("unknown dist")

def bin_fill(bin_items: List[float]) -> float:
    return sum(bin_items)
