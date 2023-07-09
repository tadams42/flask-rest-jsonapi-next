def dummy_decorator():
    def deco(f):
        def wrapper_f(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper_f

    return deco
