from collections import defaultdict
"""

This file is used ONLY in: 'utils.group_key_based' method!

Do not evaluate this approach.

It's just for fun & discussion.

"""


def tree():
    return defaultdict(tree)


def dicts(t):
    return {k: dicts(t[k]) for k in t}


def add(t, row, header):
    for key, value in enumerate(row):
        config = "'%s': '%s'" % (header[key], value)
        if key not in [0, 1, 2, 3, 4]:
            t = t[config]
        else:
            t[config] = tree()
