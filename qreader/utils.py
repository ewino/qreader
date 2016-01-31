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
    """Wraps the list of ints in a bytes or bytestring wrapper
    :param list[int] ints: the bytes to wrap
    """
    if six.PY3:
        return bytes(ints)
    else:
        return ''.join(chr(x) for x in ints)


def bytes_to_ints(bs):
    if six.PY3:
        return list(bs)
    else:
        return [ord(c) for c in bs]


def bits_to_ints(bits, bits_in_byte=8, offset=0):
    output = []
    for start_bit_id in range(offset, int(len(bits) / bits_in_byte) * bits_in_byte, bits_in_byte):
        val = 0
        for bit_id in range(bits_in_byte):
            val = (val << 1) + bits[start_bit_id + bit_id]
        output.append(val)
    return output


def ints_to_bits(nums, bits_in_byte=8):
    output = []
    for num in nums:
        num_bits = []
        while num:
            num_bits.append(num % 2)
            num >>= 1
        num_bits = num_bits[:bits_in_byte]
        num_bits.reverse()
        num_bits = [0] * (bits_in_byte - len(num_bits)) + num_bits
        output.extend(num_bits)
    return output
