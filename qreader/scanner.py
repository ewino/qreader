from collections import Iterator
from io import StringIO
import six

from qreader import tuples
from qreader.spec import get_mask_func, FORMAT_INFO_MASK, get_dead_zones

__author__ = 'ewino'


class Scanner(object):
    def __init__(self, image):
        """
        :type image: PIL.Image.Image
        :return:
        """
        self.image = image.convert('L')
        self.info = self.read_info()
        self.mask = self.get_mask()
        self.data = self._read_all_data()
        self._data_len = len(self.data)
        self._current_index = -1
        self.reset()

    def reset(self):
        self._current_index = -1

    def _read_all_data(self):
        pos_iterator = QrZigZagIterator(self.info.size, get_dead_zones(self.info.version))
        data = StringIO()
        for pos in iter(pos_iterator):
            data.write(six.text_type(self._get_bit(pos) ^ self.mask[pos]))
        return data.getvalue()

    def read_bit(self):
        self._current_index += 1
        if self._current_index >= self._data_len:
            self._current_index = self._data_len
            raise StopIteration()
        return self.data[self._current_index]

    def read_int(self, amount_of_bits):
        val = 0
        bits = [self.read_bit() for _ in range(amount_of_bits)]
        for bit in bits:
            val = (val << 1) + int(bit)
        return val

    def get_mask(self):
        mask_func = get_mask_func(self.info.mask_id)
        return {(x, y): 1 if mask_func(y, x) else 0 for x in range(self.info.size) for y in range(self.info.size)}

    def __iter__(self):
        while True:
            yield self.read_bit()

    def read_info(self):
        info = QRCodeInfo()
        info.canvas = self.get_image_borders()
        info.block_size = self.get_block_size(info.canvas[:2])
        info.size = int((info.canvas[2] - (info.canvas[0]) + 1) / info.block_size[0])
        info.version = (info.size - 17) // 4
        self.info = info
        self._read_format_info()
        return info

    def get_image_borders(self):
        # TODO: use QR finder patterns
        min_x = min_y = max_x = max_y = None
        for x in range(self.image.width):
            for y in range(self.image.height):
                if self.image.getpixel((x, y)) < 128:
                    if min_x is None or min_x > x:
                        min_x = x
                    if max_x is None or max_x < x:
                        max_x = x
                    if min_y is None or min_y > y:
                        min_y = y
                    if max_y is None or max_y < y:
                        max_y = y
        return min_x, min_y, max_x, max_y

    def get_block_size(self, img_start):
        """
        Returns the size in pixels of a single block. Right now only supports square blocks
        :return: A tuple of width, height in pixels of a block
        :rtype: tuple[int]
        """
        for i in range(1, 20):
            if self.image.getpixel(tuples.add(img_start, i)) > 128:
                return i, i

    def _read_format_info(self):
        source_1 = (self._get_straight_bits((8, -7), 7, 'd') << 8) + self._get_straight_bits((-1, 8), 8, 'l')
        source_2 = (self._get_straight_bits((7, 8), 8, 'l', (1,)) << 8) + self._get_straight_bits((8, 0), 9, 'd', (6,))
        assert source_1 == source_2, 'discrepancy in format info'
        format_info = source_1 ^ FORMAT_INFO_MASK
        self.info.error_correction_level = (format_info >> 13) & 0b11
        self.info.mask_id = (format_info >> 10) & 0b111

    def _get_bit(self, coords):
        x, y = coords
        if x < 0:
            x += self.info.size
        if y < 0:
            y += self.info.size
        color = self.image.getpixel(tuples.add(self.info.canvas[:2], tuples.multiply((x, y), self.info.block_size)))
        return 1 if color < 128 else 0

    def _get_straight_bits(self, start, length, direction, skip=()):
        """
        Reads several bits from the specified coordinates
        :param tuple[int] start: The x, y of the start position
        :param int length: the amount of bits to read
        :param str direction: r(ight), d(own), l(eft), u(p)
        :param tuple skip: the indexes to skip. they will still be counted on for the length
        :return: The bits read as an integer
        :rtype: int
        """
        result = 0
        counted = 0
        step = (1, 0) if direction == 'r' else (0, 1) if direction == 'd' else (-1, 0) if direction == 'l' else (0, -1)
        for i in range(length):
            if i in skip:
                start = tuples.add(start, step)
                continue
            result += self._get_bit(start) << counted
            counted += 1
            start = tuples.add(start, step)
        return result


class QrZigZagIterator(Iterator):
    def __init__(self, size, dead_zones):
        self.size = size
        self.ignored_pos = {(x, y) for zone in dead_zones
                            for x in range(zone[0], zone[2] + 1)
                            for y in range(zone[1], zone[3] + 1)}
        self._current = ()
        self._scan_direction = 'u'
        self._odd_col_modifier = False
        self.reset()

    def reset(self):
        self._current = (self.size - 2, self.size)
        self._scan_direction = 'u'
        self._odd_col_modifier = False

    def _advance_pos(self):
        pos = self._current
        while pos[0] >= 0 and (pos == self._current or pos in self.ignored_pos):
            step = (-1, 0)
            # We advance a line if we're in an odd column, but if we have the col_modified flag on, we switch it around
            advance_line = ((self.size - pos[0]) % 2 == 0) ^ self._odd_col_modifier
            if advance_line:
                step = (1, -1 if self._scan_direction == 'u' else 1)
                # if we're trying to advance a line but we've reached the edge, we should change directions
                if (pos[1] == 0 and self._scan_direction == 'u') or (pos[1] == self.size - 1 and self._scan_direction == 'd'):
                    # swap scan direction
                    self._scan_direction = 'd' if self._scan_direction == 'u' else 'u'
                    # go one step left
                    step = (-1, 0)
                    # make sure we're not tripping over the timing array
                    if pos[0] > 0 and all((pos[0] - 1, y) in self.ignored_pos for y in range(self.size)):
                        step = (-2, 0)
                        self._odd_col_modifier = not self._odd_col_modifier
            pos = tuples.add(pos, step)
        self._current = pos

    def __next__(self):
        self._advance_pos()
        if self._current[0] < 0:
            raise StopIteration()
        return self._current

    next = __next__


class QRCodeInfo(object):
    # number between 1-40
    version = 0

    # the error correction level.
    error_correction_level = 0

    # the id of the mask (0-7)
    mask_id = 0

    # the part of the image that contains the QR code
    canvas = (0, 0)

    # the size of each block in pixels
    block_size = (0, 0)

    # the amount of blocks at each side of the image (it's always a square)
    size = 0

    def __str__(self):
        return '<version %s, size %s, ec %s, mask %s>' % (self.version, self.size, self.error_correction_level, self.mask_id)
