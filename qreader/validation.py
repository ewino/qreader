from queue import Full

import six

from qreader.exceptions import QrCorruptError, QrFormatError
from qreader.spec import FORMAT_INFO_BCH_GENERATOR, DATA_BLOCKS_INFO, PADDING_BY_VERSION
from reedsolo import RSCodec

from qreader.utils import ints_to_bytes, bits_to_ints, ints_to_bits, bytes_to_ints

__author__ = 'ewino'

# Much of the credit goes to the author of the article at
# https://en.wikiversity.org/wiki/Reed-Solomon_codes_for_coders


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
    """ Calculates the hamming weight of the difference between two number (number of different bits)
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
    :raise QrCorruptError: in case the format info is too corrupt to singularly verify
    :return: The 5-bit (0-31) format info number
    :rtype: int
    """
    if second_format_info_sample is None:
        second_format_info_sample = format_info
    if format_info_check(format_info) == format_info_check(second_format_info_sample) == 0:
        return format_info >> 10
    format_info = (format_info << 15) + second_format_info_sample

    best_format = None
    max_distance = 29
    for test_format in range(0, 32):
        test_code = (test_format << 10) ^ format_info_check(test_format << 10)
        test_dist = hamming_diff(format_info, test_code + (test_code << 15))

        if test_dist < max_distance:
            max_distance = test_dist
            best_format = test_format
        elif test_dist == max_distance:
            best_format = None
    if best_format is None:
        raise QrCorruptError('QR meta-info is too corrupt to read')
    return best_format


class InterleavedBlockWriter(object):
    def __init__(self, blocks_sizes):
        self.blocks_sizes = blocks_sizes[:]
        self.blocks = [[] for _ in self.blocks_sizes]
        """ :type: list[list[int]] """
        self._current_block_id = 0

    def write(self, value):
        counter = 0
        while len(self.blocks[self._current_block_id]) >= self.blocks_sizes[self._current_block_id]:
            self._advance()
            counter += 1
            if counter > len(self.blocks):
                raise Full('All blocks are full!')
        self.blocks[self._current_block_id].append(value)

    def fill(self, data):
        temp_block_sizes = []
        left = len(data)
        while left:
            if len(temp_block_sizes) >= len(self.blocks_sizes):
                raise Full('Not enough space in the blocks')
            temp_block_size = min(self.blocks_sizes[len(temp_block_sizes)], left)
            temp_block_sizes.append(temp_block_size)
            left -= temp_block_size

        full_block_sizes = self.blocks_sizes
        self.blocks_sizes = temp_block_sizes

        for val in data:
            self.write(val)

        self.blocks_sizes = full_block_sizes

    def get_blocks_needed(self, size):
        blocks_needed = 0
        while blocks_needed < len(self.blocks_sizes) and size:
            blocks_needed += 1
            size -= self.blocks_sizes[blocks_needed - 1]
        if size:
            raise Full('Not enough space in the blocks')
        return blocks_needed

    def _advance(self):
        self._current_block_id = (self._current_block_id + 1) % len(self.blocks_sizes)


def validate_data(data, version, ec_level):
    padding = PADDING_BY_VERSION[version - 1]
    if padding > 0 and data[-padding:] != [0] * padding:
        raise QrFormatError('Padding bits not found (found %r instead)' % (data[-padding:],))
    data = bits_to_ints(data[:-padding])

    blocks_info = DATA_BLOCKS_INFO[version][ec_level]
    block_sizes = [blocks_info[1]] * blocks_info[2] + [blocks_info[1] + 1] * (blocks_info[3] if len(blocks_info) > 3 else 0)
    ec_count = blocks_info[0]

    data_part = data[:-ec_count * len(block_sizes)]
    ec_part = data[-ec_count * len(block_sizes):]

    blocks_writer = InterleavedBlockWriter(block_sizes)
    blocks_writer.fill(data_part)

    ec_writer = InterleavedBlockWriter([ec_count] * len(block_sizes))
    ec_writer.fill(ec_part)

    output = six.BytesIO()
    codec = RSCodec(ec_count)
    for block_id, block_size in enumerate(block_sizes):
        data_block = blocks_writer.blocks[block_id]
        # data_block += [0] * (block_size - len(data_block))
        data_with_ec = ints_to_bytes(data_block + ec_writer.blocks[block_id])
        decoded = codec.decode(data_with_ec)
        output.write(decoded)
    output = ints_to_bits(bytes_to_ints(output.getvalue()))
    return data
