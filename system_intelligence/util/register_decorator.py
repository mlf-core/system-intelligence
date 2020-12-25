QUERIER = dict()


def register(cls):
    """
    Register an info querier as a querier class
    """
    QUERIER[cls.__name__] = cls
    return cls
