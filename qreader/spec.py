from itertools import permutations
from qreader.constants import MODE_SIZE_SMALL, MODE_SIZE_LARGE
from qreader.constants import MODE_SIZE_MEDIUM
from qreader.utils import is_overlapping

__author__ = 'ewino'


FORMAT_INFO_MASK = 0b101010000010010
FORMAT_INFO_BCH_GENERATOR = 0b10100110111

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


# taken from qrcode package
def get_mask_func(mask_id):
    """
    Return the mask function for the given mask pattern.
    """
    id_to_mask = {
        0: lambda i, j: (i + j) % 2 == 0,  # 000
        1: lambda i, j: i % 2 == 0,  # 001
        2: lambda i, j: j % 3 == 0,  # 010
        3: lambda i, j: (i + j) % 3 == 0,  # 011
        4: lambda i, j: (i // 2 + j // 3) % 2 == 0,  # 100
        5: lambda i, j: (i * j) % 2 + (i * j) % 3 == 0,  # 101
        6: lambda i, j: ((i * j) % 2 + (i * j) % 3) % 2 == 0,  # 110
        7: lambda i, j: ((i * j) % 3 + (i + j) % 2) % 2 == 0,  # 111
    }
    if mask_id in id_to_mask:
        return id_to_mask[mask_id]
    raise TypeError("Bad mask pattern: " + mask_id)


def mode_sizes_for_version(version):
    if version != int(version):
        raise ValueError('QR version (%s) should be an integer' % (version,))
    if 1 <= version <= 9:
        return MODE_SIZE_SMALL
    elif 10 <= version <= 26:
        return MODE_SIZE_MEDIUM
    elif 27 <= version <= 40:
        return MODE_SIZE_LARGE
    raise ValueError('Unknown QR version: %s' % (version,))


def bits_for_length(version, data_mode):
    size_mode = mode_sizes_for_version(version)

    if data_mode not in size_mode:
        raise TypeError("Unknown data type ID: %s" % (data_mode,))

    return size_mode[data_mode]


def size_by_version(version):
    if version < 1 or version > 40 or not version == int(version):
        raise ValueError('Illegal QR version: %s' % version)
    return 17 + version * 4


def get_dead_zones(version):
    size = size_by_version(version)
    constant_zones = [
        (0, 0, 8, 8),  # top left position
        (size - 8, 0, size - 1, 8),  # top right position
        (0, size - 8, 7, size - 1),  # bottom left position
        (8, size - 7, 8, size - 1),  # bottom left format info
        (8, 6, size - 9, 6),  # top timing array
        (6, 8, 6, size - 9)  # left timing array
    ]

    alignments_zones = []
    alignment_centers = list(permutations(ALIGNMENT_POSITIONS[version - 1], 2))
    alignment_centers.extend((x, x) for x in ALIGNMENT_POSITIONS[version - 1])

    for center_x, center_y in alignment_centers:
        alignment_zone = (center_x - 2, center_y - 2, center_x + 2, center_y + 2)
        if all(not is_overlapping(alignment_zone, dead_zone) for dead_zone in constant_zones):
            alignments_zones.append(alignment_zone)
    return constant_zones + alignments_zones
