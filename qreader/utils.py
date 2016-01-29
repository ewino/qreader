import six

__author__ = 'ewino'


def is_rect_overlapping(rect1, rect2):
    h_overlaps = is_range_overlapping((rect1[0], rect1[2]), (rect2[0], rect2[2]))
    v_overlaps = is_range_overlapping((rect1[1], rect1[3]), (rect2[1], rect2[3]))
    return h_overlaps and v_overlaps


def is_range_overlapping(a, b):
    """Neither range is completely greater than the other
    :param tuple a: first range
    :param tuple b: second range
    """
    return (a[0] <= b[1]) and (b[0] <= a[1])


def ints_to_bytes(ints):
    if six.PY3:
        return bytes(ints)
    else:
        return ''.join(chr(x) for x in ints)
