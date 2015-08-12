__author__ = 'ewino'


def add(t1, t_or_n):
    if isinstance(t_or_n, (int, float)):
        return tuple(x + t_or_n for x in t1)
    elif isinstance(t_or_n, tuple):
        return tuple(x + t_or_n[i] for i, x in enumerate(t1))
    raise TypeError("Can't add a %s to a tuple" % type(t_or_n))


def multiply(t1, t_or_n):
    if isinstance(t_or_n, (int, float)):
        return tuple(x * t_or_n for x in t1)
    elif isinstance(t_or_n, tuple):
        return tuple(x * t_or_n[i] for i, x in enumerate(t1))
    raise TypeError("Can't multiply a tuple by a" % type(t_or_n))
