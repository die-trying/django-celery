import inspect


def find_ancestors(scope, base_class):
    """
    A shortcut to find all first level ancestors of Base class in scope
    I use it for testing abstract models
    """
    res = []
    for name, member in inspect.getmembers(scope):
        if not inspect.isclass(member):
            continue

        if base_class not in member.__bases__:
            continue

        res.append(member)

    return res
