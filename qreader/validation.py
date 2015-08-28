from qreader.spec import FORMAT_INFO_BCH_GENERATOR

__author__ = 'ewino'


def format_info_check(format_info):
    """ Returns 0 if given a complete format info code and it is valid.
    Otherwise, returns a positive number.
    If given a format info marker padded with 10 bits (e.g. 101010000000000) returns
    the corresponding 10-bit error correction code to append to it
    :param int format_info: The format info with error correction (15 bits) or without it (5 bits)
    :rtype: int
    """
    g = FORMAT_INFO_BCH_GENERATOR
    for i in range(4, -1, -1):
        if format_info & (1 << (i+10)):
            format_info ^= g << i
    return format_info


def hamming_diff(a, b):
    """ Calculates the hamming weight of the difference between two number (summing the different bits)
    :param int a: A number to calculate the diff from
    :param int b: A number to calculate the diff from
    :return: The amount of different bits
    :rtype: int
    """
    weight = 0
    diff = a ^ b
    while diff > 0:
        weight += diff & 1
        diff >>= 1
    return weight


def validate_format_info(format_info, second_format_info_sample=None):
    """
    Receives one or two copies of a QR format info containing error correction bits, and returns just the format
    info bits, after error checking and correction
    :param int format_info: The 15-bit format info bits with the error correction info
    :param int second_format_info_sample: The secondary 15-bit format info bits with the error correction info
    :return: The 5-bit format info number, or None if one could not be determined
    :rtype: int|None
    """
    if second_format_info_sample is None:
        second_format_info_sample = format_info
    if format_info_check(format_info) == format_info_check(second_format_info_sample) == 0:
        return format_info >> 10

    best_format = None
    max_distance = 30
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
