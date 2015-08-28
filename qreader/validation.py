from qreader.spec import FORMAT_INFO_BCH_GENERATOR

__author__ = 'ewino'


def format_info_check(fmt):
    g = FORMAT_INFO_BCH_GENERATOR
    for i in range(4, -1, -1):
        if fmt & (1 << (i+10)):
            fmt ^= g << i
    return fmt


def hamming_diff(a, b):
    """ Calculates the hamming weight of the difference between two number (summing the different bits)
    :param int a: A number to calculate the diff from
    :param int b: A number to calculate the diff from
    :return: The amount of different bits
    """
    weight = 0
    diff = a ^ b
    while diff > 0:
        weight += diff & 1
        diff >>= 1
    return weight


def validate_format_info(format_info, second_format_info_sample=None):
    best_format = None
    max_distance = 30
    if second_format_info_sample is None:
        second_format_info_sample = format_info
    format_info = (format_info << 15) + second_format_info_sample
    for test_format in range(0, 32):
        test_code = (test_format << 10) ^ format_info_check(test_format << 10)
        test_dist = hamming_diff(format_info, test_code + (test_code << 15))
        if test_dist == 0:
            return test_format

        if test_dist < max_distance:
            max_distance = test_dist
            best_format = test_format
        elif test_dist == max_distance:
            best_format = None
    return best_format
