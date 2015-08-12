from itertools import permutations
from qreader import tuples
from qreader.utils import is_overlapping, get_mask_func

__author__ = 'ewino'


FORMAT_MASK = 0b101010000010010


ALIGNMENT_POSITIONS = [
    [],
    [6, 18],
    [6, 22],
    [6, 26],
    [6, 30],
    [6, 34],
    [6, 22, 38],
    [6, 24, 42],
    [6, 26, 46],
    [6, 28, 50],
    [6, 30, 54],
    [6, 32, 58],
    [6, 34, 62],
    [6, 26, 46, 66],
    [6, 26, 48, 70],
    [6, 26, 50, 74],
    [6, 30, 54, 78],
    [6, 30, 56, 82],
    [6, 30, 58, 86],
    [6, 34, 62, 90],
    [6, 28, 50, 72, 94],
    [6, 26, 50, 74, 98],
    [6, 30, 54, 78, 102],
    [6, 28, 54, 80, 106],
    [6, 32, 58, 84, 110],
    [6, 30, 58, 86, 114],
    [6, 34, 62, 90, 118],
    [6, 26, 50, 74, 98, 122],
    [6, 30, 54, 78, 102, 126],
    [6, 26, 52, 78, 104, 130],
    [6, 30, 56, 82, 108, 134],
    [6, 34, 60, 86, 112, 138],
    [6, 30, 58, 86, 114, 142],
    [6, 34, 62, 90, 118, 146],
    [6, 30, 54, 78, 102, 126, 150],
    [6, 24, 50, 76, 102, 128, 154],
    [6, 28, 54, 80, 106, 132, 158],
    [6, 32, 58, 84, 110, 136, 162],
    [6, 26, 54, 82, 110, 138, 166],
    [6, 30, 58, 86, 114, 142, 170]
]


class Scanner(object):
    def __init__(self, image):
        """
        :type image: PIL.Image.Image
        :return:
        """
        self.image = image.convert('L')
        self.info = self.read_info()
        dead_zones = self.get_dead_zones()
        self.mask = self.apply_mask(dead_zones)
        self._next_pos = ()
        self._odd_col_modifier = False
        self._scan_direction = 'u'
        self.reset()

    def reset(self):
        self._next_pos = (self.info.size - 1, self.info.size - 1)
        self._scan_direction = 'u'
        self._odd_col_modifier = False

    def apply_mask(self, dead_zones):
        mask = {}
        mask_func = get_mask_func(self.info.mask_id)
        for x in range(self.info.size):
            for y in range(self.info.size):
                mask[x, y] = 1 if mask_func(y, x) else 0
        for zone in dead_zones:
            for x in range(zone[0], zone[2] + 1):
                for y in range(zone[1], zone[3] + 1):
                    mask[x, y] = None
        return mask

    def __iter__(self):
        self.reset()
        while self._next_pos[0] >= 0 and self._next_pos[1] >= 0:
            yield self._get_bit(self._next_pos) * self.mask[self._next_pos]
            self._next_pos = self._get_next_pos(self._next_pos)

    def _get_next_pos(self, current):
        pos = current
        while pos[0] >= 0 and (pos == current or self.mask[pos] is None):
            step = (-1, 0)
            # We advance a line if we're in an odd column, but if we have the col_modified flag on, we switch it around
            advance_line = ((self.info.size - pos[0]) % 2 == 0) ^ self._odd_col_modifier
            if advance_line:
                step = (1, -1 if self._scan_direction == 'u' else 1)
                # if we're trying to advance a line but we've reached the edge, we probably shouldn't do that
                if (pos[1] == 0 and self._scan_direction == 'u') or (pos[1] == self.info.size - 1 and self._scan_direction == 'd'):
                    # swap scan direction
                    self._scan_direction = 'd' if self._scan_direction == 'u' else 'u'
                    # go one step left
                    step = (-1, 0)
                    # make sure we're not tripping over the timing array
                    if pos[0] > 0 and all(self.mask[pos[0] - 1, y] is None for y in range(self.info.size)):
                        step = (-2, 0)
                        self._odd_col_modifier = not self._odd_col_modifier
            pos = tuples.add(pos, step)
        return pos

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

    def get_dead_zones(self):
        size = self.info.size
        zones = [
            (0, 0, 8, 8),  # top left position
            (size - 8, 0, size - 1, 8),  # top right position
            (0, size - 8, 7, size - 1),  # bottom left position
            (8, size - 7, 8, size - 1),  # bottom left format info
            (8, 6, size - 9, 6),  # top timing array
            (6, 8, 6, size - 9)  # left timing array
        ]
        alignments_zones = []
        alignment_positions = list([(x, x) for x in ALIGNMENT_POSITIONS[self.info.version - 1]]) + list(permutations(ALIGNMENT_POSITIONS[self.info.version - 1], 2))
        for pos_x, pos_y in alignment_positions:
            alignment_zone = (pos_x - 2, pos_y - 2, pos_x + 2, pos_y + 2)
            if all(not is_overlapping(alignment_zone, dead_zone) for dead_zone in zones):
                alignments_zones.append(alignment_zone)
        return zones + alignments_zones

    def _read_format_info(self):
        source_1 = (self._get_straight_bits((8, -7), 7, 'd') << 7) + self._get_straight_bits((-1, 8), 8, 'l')
        source_2 = (self._get_straight_bits((7, 8), 8, 'l', (1,)) << 7) + self._get_straight_bits((8, 0), 9, 'd', (6,))
        assert source_1 == source_2, 'discrepancy in format info'
        format_info = source_1 ^ FORMAT_MASK
        self.info.error_correction_level = (format_info >> 11) & 0b11
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
