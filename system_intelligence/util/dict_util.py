def flatten(d: dict):
    """
    https://stackoverflow.com/questions/52081545/python-3-flattening-nested-dictionaries-and-lists-within-dictionaries
    """
    out = {}
    for key, val in d.items():
        if isinstance(val, dict):
            val = [val]
        if isinstance(val, list):
            for subdict in val:
                deeper = flatten(subdict).items()
                out.update({key + '_' + key2: val2 for key2, val2 in deeper})
        else:
            out[key] = val
    return out
