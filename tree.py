from collections import defaultdict


def tree():
    return defaultdict(tree)


def dicts(t):
    return {k: dicts(t[k]) for k in t}


def add(t, path):
    for node in path:
        t = t[node]
