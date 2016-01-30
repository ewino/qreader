from itertools import permutations
from qreader.constants import MODE_SIZE_SMALL, MODE_SIZE_LARGE, ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, \
    ERROR_CORRECT_H
from qreader.constants import MODE_SIZE_MEDIUM
from qreader.exceptions import QrFormatError, IllegalQrVersionError
from qreader.utils import is_rect_overlapping

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


DATA_BLOCKS_INFO = [
    # For each version: L, M, Q, H: (EC bytes, block size, blocks count, large blocks count)
    ((7, 19, 1), (10, 16, 1), (13, 13, 1), (17, 9, 1)),  # v1
    ((10, 34, 1), (16, 28, 1), (22, 22, 1), (28, 16, 1)),  # v2
    ((15, 55, 1), (26, 44, 1), (18, 17, 2), (22, 13, 2)),  # v3
    ((20, 80, 1), (18, 32, 2), (26, 24, 2), (16, 9, 4)),  # v4
    ((26, 108, 1), (24, 43, 2), (18, 15, 2, 2), (22, 11, 2, 2)),  # v5
    ((18, 68, 2), (16, 27, 4), (24, 19, 4), (28, 15, 4)),  # v6
    ((20, 78, 2), (18, 31, 4), (18, 14, 2, 4), (26, 13, 4, 1)),  # v7
    ((24, 97, 2), (22, 38, 2, 2), (22, 18, 4, 2), (26, 14, 4, 2)),  # v8
    ((30, 116, 2), (22, 36, 3, 2), (20, 16, 4, 4), (24, 12, 4, 4)),  # v9
    ((18, 68, 2, 2), (26, 43, 4, 1), (24, 19, 6, 2), (28, 15, 6, 2)),  # v10
    ((20, 81, 4), (30, 50, 1, 4), (28, 22, 4, 4), (24, 12, 3, 8)),  # v11
    ((24, 92, 2, 2), (22, 36, 6, 2), (26, 20, 4, 6), (28, 14, 7, 4)),  # v12
    ((26, 107, 4), (22, 37, 8, 1), (24, 20, 8, 4), (22, 11, 12, 4)),  # v13
    ((30, 115, 3, 1), (24, 40, 4, 5), (20, 16, 11, 5), (24, 12, 11, 5)),  # v14
    ((22, 87, 5, 1), (24, 41, 5, 5), (30, 24, 5, 7), (24, 12, 11, 7)),  # v15
    ((24, 98, 5, 1), (28, 45, 7, 3), (24, 19, 15, 2), (30, 15, 3, 13)),  # v16
    ((28, 107, 1, 5), (28, 46, 10, 1), (28, 22, 1, 15), (28, 14, 2, 17)),  # v17
    ((30, 120, 5, 1), (26, 43, 9, 4), (28, 22, 17, 1), (28, 14, 2, 19)),  # v18
    ((28, 113, 3, 4), (26, 44, 3, 11), (26, 21, 17, 4), (26, 13, 9, 16)),  # v19
    ((28, 107, 3, 5), (26, 41, 3, 13), (30, 24, 15, 5), (28, 15, 15, 10)),  # v20
    ((28, 116, 4, 4), (26, 42, 17), (28, 22, 17, 6), (30, 16, 19, 6)),  # v21
    ((28, 111, 2, 7), (28, 46, 17), (30, 24, 7, 16), (24, 13, 34)),  # v22
    ((30, 121, 4, 5), (28, 47, 4, 14), (30, 24, 11, 14), (30, 15, 16, 14)),  # v23
    ((30, 117, 6, 4), (28, 45, 6, 14), (30, 24, 11, 16), (30, 16, 30, 2)),  # v24
    ((26, 106, 8, 4), (28, 47, 8, 13), (30, 24, 7, 22), (30, 15, 22, 13)),  # v25
    ((28, 114, 10, 2), (28, 46, 19, 4), (28, 22, 28, 6), (30, 16, 33, 4)),  # v26
    ((30, 122, 8, 4), (28, 45, 22, 3), (30, 23, 8, 26), (30, 15, 12, 28)),  # v27
    ((30, 117, 3, 10), (28, 45, 3, 23), (30, 24, 4, 31), (30, 15, 11, 31)),  # v28
    ((30, 116, 7, 7), (28, 45, 21, 7), (30, 23, 1, 37), (30, 15, 19, 26)),  # v29
    ((30, 115, 5, 10), (28, 47, 19, 10), (30, 24, 15, 25), (30, 15, 23, 25)),  # v30
    ((30, 115, 13, 3), (28, 46, 2, 29), (30, 24, 42, 1), (30, 15, 23, 28)),  # v31
    ((30, 115, 17), (28, 46, 10, 23), (30, 24, 10, 35), (30, 15, 19, 35)),  # v32
    ((30, 115, 17, 1), (28, 46, 14, 21), (30, 24, 29, 19), (30, 15, 11, 46)),  # v33
    ((30, 115, 13, 6), (28, 46, 14, 23), (30, 24, 44, 7), (30, 16, 59, 1)),  # v34
    ((30, 121, 12, 7), (28, 47, 12, 26), (30, 24, 39, 14), (30, 15, 22, 41)),  # v35
    ((30, 121, 6, 14), (28, 47, 6, 34), (30, 24, 46, 10), (30, 15, 2, 64)),  # v36
    ((30, 122, 17, 4), (28, 46, 29, 14), (30, 24, 49, 10), (30, 15, 24, 46)),  # v37
    ((30, 122, 4, 18), (28, 46, 13, 32), (30, 24, 48, 14), (30, 15, 42, 32)),  # v38
    ((30, 117, 20, 4), (28, 47, 40, 7), (30, 24, 43, 22), (30, 15, 10, 67)),  # v39
    ((30, 118, 19, 6), (28, 47, 18, 31), (30, 24, 34, 34), (30, 15, 20, 61)),  # v40
]


# taken from qrcode package
def get_mask_func(mask_id):
    """
    Return the mask function for the given mask pattern.
    :param int mask_id: The mask ID in the range 0-7.
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
    raise QrFormatError("Bad mask pattern: {0!r:s}".format(mask_id))


def mode_sizes_for_version(version):
    if version != int(version):
        raise IllegalQrVersionError(version)
    if 1 <= version <= 9:
        return MODE_SIZE_SMALL
    elif 10 <= version <= 26:
        return MODE_SIZE_MEDIUM
    elif 27 <= version <= 40:
        return MODE_SIZE_LARGE
    raise IllegalQrVersionError(version)


def bits_for_length(version, data_mode):
    size_mode = mode_sizes_for_version(version)

    if data_mode not in size_mode:
        raise QrFormatError(u"Unknown data type ID: {0!r:s}".format(data_mode, ))

    return size_mode[data_mode]


def size_by_version(version):
    if version < 1 or version > 40 or not version == int(version):
        raise IllegalQrVersionError(version)
    return 17 + version * 4


def ec_level_from_format_info_code(info_ec_code):
    levels = {
        0: ERROR_CORRECT_M,
        1: ERROR_CORRECT_L,
        2: ERROR_CORRECT_H,
        3: ERROR_CORRECT_Q
    }
    return levels[info_ec_code]


def get_dead_zones(version):
    size = size_by_version(version)
    constant_zones = [
        (0, 0, 8, 8),  # top left position + format-info
        (size - 8, 0, size - 1, 8),  # top right position + format-info
        (0, size - 8, 7, size - 1),  # bottom left position
        (8, size - 7, 8, size - 1),  # bottom left format info
        (8, 6, size - 9, 6),  # top timing array
        (6, 8, 6, size - 9)  # left timing array
    ]

    if version >= 7:
        constant_zones.append((size - 11, 0, size - 9, 5))  # top version info
        constant_zones.append((0, size - 11, 5, size - 9))  # bottom (left) version info

    alignments_zones = []
    alignment_centers = list(permutations(ALIGNMENT_POSITIONS[version - 1], 2))
    alignment_centers.extend((x, x) for x in ALIGNMENT_POSITIONS[version - 1])

    for center_x, center_y in alignment_centers:
        alignment_zone = (center_x - 2, center_y - 2, center_x + 2, center_y + 2)
        if all(not is_rect_overlapping(alignment_zone, dead_zone) for dead_zone in constant_zones):
            alignments_zones.append(alignment_zone)
    return constant_zones + alignments_zones
