__author__ = 'ewino'


def is_overlapping(rect1, rect2):
    hoverlaps = range_overlap(rect1[0], rect1[2], rect2[0], rect2[2])
    voverlaps = range_overlap(rect1[1], rect1[3], rect2[1], rect2[3])
    return hoverlaps and voverlaps


def range_overlap(a_min, a_max, b_min, b_max):
    """Neither range is completely greater than the other"""
    return (a_min <= b_max) and (b_min <= a_max)


# taken from qrcode package
def get_mask_func(mask_id):
    """
    Return the mask function for the given mask pattern.
    """
    if mask_id == 0:   # 000
        return lambda i, j: (i + j) % 2 == 0
    if mask_id == 1:   # 001
        return lambda i, j: i % 2 == 0
    if mask_id == 2:   # 010
        return lambda i, j: j % 3 == 0
    if mask_id == 3:   # 011
        return lambda i, j: (i + j) % 3 == 0
    if mask_id == 4:   # 100
        return lambda i, j: (i // 2 + j // 3) % 2 == 0
    if mask_id == 5:  # 101
        return lambda i, j: (i * j) % 2 + (i * j) % 3 == 0
    if mask_id == 6:  # 110
        return lambda i, j: ((i * j) % 2 + (i * j) % 3) % 2 == 0
    if mask_id == 7:  # 111
        return lambda i, j: ((i * j) % 3 + (i + j) % 2) % 2 == 0
    raise TypeError("Bad mask pattern: " + mask_id)