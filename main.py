from binpack.utils import gen_iid_items
from binpack.online import run_full_algorithm
import numpy as np

def evaluate_distribution(n=2000):
    items = gen_iid_items(n, dist='two_point', p=0.3, v1=0.25, v2=0.75)
    bins, stats = run_full_algorithm(items, AU_mode='ffd', X=0.25, stage_k=200)
    print("stats:", stats)
    print("approx bins used:", stats['total_bins'])
    print("n items:", n)

if __name__ == "__main__":
    evaluate_distribution(2000)
