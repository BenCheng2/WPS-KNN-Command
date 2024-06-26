def singleton(cls):
    # Decorator to enable singleton pattern

    _instance = {}

    def inner(*args, **kwargs):
        if cls in _instance:
            return _instance[cls]
        obj = cls(*args, **kwargs)
        _instance[cls] = obj

        return obj

    return inner
