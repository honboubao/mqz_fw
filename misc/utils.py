import gc

def find(list, condition, default=None):
    try:
        return next(filter(condition, list))
    except StopIteration:
        return default

def print_mem():
    gc.collect()
    used = gc.mem_alloc()
    free = gc.mem_free()
    print("Memory used: " + str(used) + " (" + str(round(100 * used / (used + free))) + "%) free: " + str(free))
