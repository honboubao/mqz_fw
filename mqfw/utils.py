def find(list, condition, default=None):
    try:
        return next(filter(condition, list))
    except StopIteration:
        return default