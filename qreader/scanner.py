from collections import Iterator

from qreader import tuples
from qreader.spec import get_mask_func, FORMAT_INFO_MASK, get_dead_zones
from qreader.validation import validate_format_info, validate_data

__author__ = 'ewino'

WHITE = 0
BLACK = 1


class Scanner(object):
    def __init__(self, image):
        """
        :type image: PIL.Image.Image
        :return:
        """
        self.image = image
        self.prepare_source()

        self.info = None
        self.read_info()

        self.mask = self.get_mask()
        self.data = validate_data(self._read_all_data())
        self._data_len = len(self.data)
        self._current_index = -1
        self.reset()

    def prepare_source(self):
        self.image = self.image.convert('L')

    def get_mask(self):
        mask_func = get_mask_func(self.info.mask_id)
        return {(x, y): 1 if mask_func(y, x) else 0 for x in range(self.info.size) for y in range(self.info.size)}

    def read_info(self):
        info = QRCodeInfo()
        info.canvas = self.get_image_borders()
        info.block_size = self.get_block_size(info.canvas[:2])
        info.size = int((info.canvas[2] - (info.canvas[0]) + 1) / info.block_size[0])
        info.version = (info.size - 17) // 4
        self.info = info
        self._read_format_info()
        return info

    def _get_pixel(self, coords):
        return 1 if self.image.getpixel(coords) < 128 else 0

    def get_image_borders(self):
        def get_corner_pixel(canvas_corner, vector, max_distance):
            for dist in range(max_distance):
                for x in range(dist + 1):
                    coords = (canvas_corner[0] + vector[0] * x, canvas_corner[1] + vector[1] * (dist - x))
                    if self._get_pixel(coords) == BLACK:
                        return coords
            raise ValueError("Couldn't find one of the edges (%s-%s)" % (('top', 'bottom')[vector[1] == -1],
                                                                          ('left', 'right')[vector[0] == -1]))

        max_dist = min(self.image.width, self.image.height)
        min_x, min_y = get_corner_pixel((0, 0), (1, 1), max_dist)
        max_x, max_x_y = get_corner_pixel((self.image.width - 1, 0), (-1, 1), max_dist)
        max_y_x, max_y = get_corner_pixel((0, self.image.height - 1), (1, -1), max_dist)
        if max_x_y != min_y:
            raise ValueError('Top-left position pattern not aligned with the top-right one')
        if max_y_x != min_x:
            raise ValueError('Top-left position pattern not aligned with the bottom-left one')
        return min_x, min_y, max_x, max_y

    def get_block_size(self, img_start):
        """
        Returns the size in pixels of a single block.
        :param tuple[int, int] img_start: The topmost left pixel in the QR (MUST be black or dark).
        :return: A tuple of width, height in pixels of a block
        :rtype: tuple[int, int]
        """
        PATTERN_SIZE = 7

        left, top = img_start
        block_height, block_width = 0, 0
        for i in range(1, self.image.width - left):
            if self._get_pixel((left + i * PATTERN_SIZE, top)) == WHITE:
                block_width = i
                break
        for i in range(1, self.image.height - top):
            if self._get_pixel((left, top + i * PATTERN_SIZE)) == WHITE:
                block_height = i
                break
        return block_width, block_height

    def _read_format_info(self):
        source_1 = (self._get_straight_bits((8, -7), 7, 'd') << 8) + self._get_straight_bits((-1, 8), 8, 'l')
        source_2 = (self._get_straight_bits((7, 8), 8, 'l', (1,)) << 8) + self._get_straight_bits((8, 0), 9, 'd', (6,))

        format_info = validate_format_info(source_1 ^ FORMAT_INFO_MASK, source_2 ^ FORMAT_INFO_MASK)
        self.info.error_correction_level = format_info >> 3
        self.info.mask_id = format_info & 0b111

    def _read_all_data(self):
        pos_iterator = QrZigZagIterator(self.info.size, get_dead_zones(self.info.version))
        return [self._get_bit(pos) ^ self.mask[pos] for pos in pos_iterator]

    def _get_bit(self, coords):
        x, y = coords
        if x < 0:
            x += self.info.size
        if y < 0:
            y += self.info.size
        return self._get_pixel(tuples.add(self.info.canvas[:2], tuples.multiply((x, y), self.info.block_size)))

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

    # Iteration methods #

    def reset(self):
        self._current_index = -1

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
            val = (val << 1) + bit
        return val

    def __iter__(self):
        while True:
            yield self.read_bit()


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
                if (pos[1] == 0 and self._scan_direction == 'u') or \
                        (pos[1] == self.size - 1 and self._scan_direction == 'd'):
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
        return '<version %s, size %s, ec %s, mask %s>' % \
               (self.version, self.size, self.error_correction_level, self.mask_id)
