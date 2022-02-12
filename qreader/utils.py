from itertools import chain

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


def bit_list_to_bytes(all_data_bits, bits_in_a_byte=8):
    bits_accumulated = 0
    current_byte = 0
    byte_list = []
    for i, b in enumerate(all_data_bits):
        current_byte = (current_byte << 1) + b
        bits_accumulated += 1
        if bits_accumulated % bits_in_a_byte == 0:
            byte_list.append(current_byte)
            current_byte = 0

    all_data_bytes = ints_to_bytes(byte_list)

    return all_data_bytes


def bytes_to_bit_list(byte_data, bits_in_a_byte=8):
    bit_data = []
    for b in byte_data:
        for i in range(bits_in_a_byte - 1, -1, -1):
            bit = (b >> i) & 1
            bit_data.append(bit)
    return bit_data


def interleave_blocks(blocks, n):
    """
    Useful for encoding.
    For n=2, given data like this - [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    returns data like this [1, 6, 2, 7, 3, 8, 4, 9, 5, 10]

    :param bytes blocks: The data blocks
    :param int n: Block count as per the QR spec
    """
    chunks = []
    chunk_size = int(len(blocks)/n)

    for i in range(n):
        chunks.append(blocks[i*chunk_size:(i+1)*chunk_size])

    interleaved_blocks = []
    for i in range(chunk_size):
        for chunk in chunks:
            interleaved_blocks.append(chunk[i])

    if len(interleaved_blocks) != len(blocks):
        raise NotImplementedError('Unequal blocks or chunks not supported')

    return interleaved_blocks


def de_interleave_blocks(blocks, n):
    """
    For n=2, given data like this - [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    return data like this - [1, 3, 5, 7, 9, 2, 4, 6, 8, 10]
    """
    blocks_copy = blocks[:]
    chunks = []
    while blocks_copy:
        chunks.append(blocks_copy[:n])
        blocks_copy = blocks_copy[n:]

    d_chunks = list(zip(*chunks))
    de_interleaved_blocks = list(chain(*d_chunks))

    return de_interleaved_blocks

