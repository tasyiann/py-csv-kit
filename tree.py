from collections import defaultdict, Mapping


def tree():
    return defaultdict(tree)


def dicts(t):
    return {k : dicts(t[k]) for k in t}


def exper(t):
    for k in t:
        print(k)
    a = {k: exper(t[k]) for k in t}

    return a

h = defaultdict(list)

def walk_dict(d, depth=0):
    for k,v in sorted(d.items(), key=lambda x: x[0]):
        h[depth].append(k)
        print("[depth:%d]" %depth+"  "*depth + ("%s" % k))
        walk_dict(v ,depth+1)



# def prettify(t, tiers_config, header):
#     tier_levels = defaultdict(list)
#     for tier_name, tier_attributes in tiers_config.items():
#         tier_attributes_dict = {}
#         tier_levels[tier_name].append(tier_attributes_dict)
#         for attribute in tier_attributes:
#             tier_attributes_dict[header[attribute]] = t.next()
#     return tier_levels


def group_attributes_in_tiers(t, tiers, ):
    pass

def dicts_x(t, new_t,  header, depth=0, tiers=None):
    return {k : dicts(t[k], header, depth+1) for k in t}


def normalize_dict(t, parent, depth=0):
    # if len(parent) <= 1 and depth != 0:
    #     # parent['h'] = t
    #     print(t)
    # else:
    #     print({k: normalize_dict(t[k], t, depth+1) for k in t})
    for k, v in t.items():
        if len(parent) == 1 and depth == 0:
            parent[k].append(normalize_dict(t[k], t, depth+1))
        return {k: normalize_dict(t[k], t, depth+1)}


def add_x(t, row, header, tiers):
    for tier_name, tier_attributes in tiers.items():
        x = {}
        for attribute_id in tier_attributes:
            attribute_name = header[attribute_id]
            x[attribute_name] = row[attribute_id]
        t[tier_name].append(x)


def add(t, row, header):
    for key, value in enumerate(row):
        config = "'%s': '%s'" % (header[key], value)
        # todo: analoga me to structure definition
        if key in range(0,17):
            t = t[config]
        else:
            t[config] = tree()

def add_flat(t, row, header):
    for key, value in enumerate(row):
        config = "%s: %s" % (header[key], value)
        t = t[config]


# def printdict(d, depth, header, flag=True):
#
#
#     for key, value in sorted(d.items()):
#         print("%s%s,"%('\t'*(depth+1), key))
#         printdict(value, depth+1, header, flag)
#
#     if depth == 2:
#         print("\n%s%s,"%('\t'*(depth), "Article:"))
#     if depth == 3:
#         print("\n%s%s," % ('\t' * (depth), "Variation:"))
#
