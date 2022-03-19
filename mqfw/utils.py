def find(list, condition, default=None):
    try:
        return next(i for i in list if condition(i))
    except StopIteration:
        return default