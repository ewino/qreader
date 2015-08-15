from unittest.case import TestCase
from qreader.constants import MODE_SIZE_SMALL, MODE_SIZE_MEDIUM, MODE_SIZE_LARGE, MODE_NUMBER, MODE_ALPHA_NUM, \
    MODE_BYTES, MODE_KANJI
from qreader.utils import is_overlapping, range_overlap, get_mask_func, mode_sizes_for_version, bits_for_length

__author__ = 'ewino'


class TestOverlap(TestCase):
    def test_overlapping_ranges(self):
        # partial overlap
        self.assertTrue(range_overlap((1, 3), (2, 4)))
        self.assertTrue(range_overlap((-8, -2), (-5, 4)))
        # a contains b
        self.assertTrue(range_overlap((1, 5), (2, 4)))
        # b contains a
        self.assertTrue(range_overlap((1, 5), (0, 6)))

    def test_non_overlapping_ranges(self):
        # negatives
        self.assertFalse(range_overlap((-8, -6), (-4, -2)))
        self.assertFalse(range_overlap((-4, -2), (-8, -6)))
        # positives
        self.assertFalse(range_overlap((8, 6), (4, 2)))
        self.assertFalse(range_overlap((4, 2), (8, 6)))
        # both
        self.assertFalse(range_overlap((-8, -2), (2, 8)))
        self.assertFalse(range_overlap((-1, 1), (2, 3)))

    def test_overlapping_zones(self):
        # [-----[-]----]
        # [     [ ]    ]
        # [_____[_]____]
        self.assertTrue(is_overlapping((1, 1, 4, 4), (3, 1, 6, 4)))
        # [-------]
        # [     [-]----]
        # [_____[_]    ]
        #       [______]
        self.assertTrue(is_overlapping((1, 1, 4, 4), (3, 3, 6, 6)))
        # [-------]
        # [-------]
        # [_______]
        # [_______]
        self.assertTrue(is_overlapping((1, 1, 4, 4), (1, 3, 4, 6)))
        # a contains b
        self.assertTrue(is_overlapping((1, 1, 4, 4), (2, 2, 4, 4)))
        self.assertTrue(is_overlapping((1, 1, 4, 4), (2, 2, 3, 3)))
        # b contains a
        self.assertTrue(is_overlapping((2, 2, 4, 4), (1, 1, 4, 4)))
        self.assertTrue(is_overlapping((2, 2, 3, 3), (1, 1, 4, 4)))
        # point rect
        self.assertTrue(is_overlapping((2, 2, 4, 4), (4, 4, 4, 4)))

    def test_non_overlapping_zones(self):
        # [-----] [-----]
        # [     ] [     ]
        # [_____] [_____]
        self.assertFalse(is_overlapping((1, 1, 4, 4), (5, 1, 8, 4)))
        # [--]
        # [__]
        #      [--]
        #      [__]
        self.assertFalse(is_overlapping((1, 1, 4, 4), (5, 5, 8, 8)))
        # [-------]
        # [_______]
        #
        # [-------]
        # [_______]
        self.assertFalse(is_overlapping((1, 1, 4, 4), (1, 5, 4, 8)))


class TestMasks(TestCase):
    def test_mask_bounds(self):
        for mask_id in range(8):
            mask_func = get_mask_func(mask_id)
            for i in range(177):
                for j in range(177):
                    self.assertIn(mask_func(i, j), (0, 1))

    def test_nonexistent_masks(self):
        self.assertRaises(TypeError, lambda: get_mask_func(-1))
        self.assertRaises(TypeError, lambda: get_mask_func(8))

    def test_mask_formula_correctness(self):
        mask_samples = {
            0: '1010101010101010101010101010101010101010101010101',
            1: '1111111000000011111110000000111111100000001111111',
            2: '1001001100100110010011001001100100110010011001001',
            3: '1001001001001001001001001001001001001001001001001',
            4: '1110001111000100011100001110111000111100010001110',
            5: '1111111100000110010011010101100100110000011111111',
            6: '1111111111000111011011010101101101110001111111111',
            7: '1010101000111010001110101010111000101110001010101',
        }

        for mask_id in range(8):
            mask_func = get_mask_func(mask_id)
            mask_result = ''
            for i in range(7):
                for j in range(7):
                    mask_result += '1' if mask_func(i, j) else '0'
            self.assertEqual(mask_samples[mask_id], mask_result)


class TestCharCounts(TestCase):
    
    def test_size_for_version(self):
        self.assertEqual(MODE_SIZE_SMALL, mode_sizes_for_version(1))
        self.assertEqual(MODE_SIZE_SMALL, mode_sizes_for_version(2))
        self.assertEqual(MODE_SIZE_SMALL, mode_sizes_for_version(5))
        self.assertEqual(MODE_SIZE_SMALL, mode_sizes_for_version(9))
        self.assertEqual(MODE_SIZE_MEDIUM, mode_sizes_for_version(10))
        self.assertEqual(MODE_SIZE_MEDIUM, mode_sizes_for_version(11))
        self.assertEqual(MODE_SIZE_MEDIUM, mode_sizes_for_version(12))
        self.assertEqual(MODE_SIZE_MEDIUM, mode_sizes_for_version(20))
        self.assertEqual(MODE_SIZE_MEDIUM, mode_sizes_for_version(26))
        self.assertEqual(MODE_SIZE_LARGE, mode_sizes_for_version(27))
        self.assertEqual(MODE_SIZE_LARGE, mode_sizes_for_version(28))
        self.assertEqual(MODE_SIZE_LARGE, mode_sizes_for_version(39))
        self.assertEqual(MODE_SIZE_LARGE, mode_sizes_for_version(40))

    def test_size_for_illegal_versions(self):
        self.assertRaises(ValueError, lambda: mode_sizes_for_version(0))
        self.assertRaises(ValueError, lambda: mode_sizes_for_version(-1))
        self.assertRaises(ValueError, lambda: mode_sizes_for_version(41))
        self.assertRaises(ValueError, lambda: mode_sizes_for_version(0.5))
        self.assertRaises(ValueError, lambda: mode_sizes_for_version(-1.5))
        self.assertRaises(ValueError, lambda: mode_sizes_for_version(10.5))
        self.assertRaises(ValueError, lambda: mode_sizes_for_version(9.5))
        self.assertRaises(ValueError, lambda: mode_sizes_for_version(40.5))

    def test_char_counts(self):
        self.assertEqual(8, bits_for_length(8, MODE_KANJI))
        self.assertEqual(9, bits_for_length(8, MODE_ALPHA_NUM))
        self.assertEqual(10, bits_for_length(8, MODE_NUMBER))

        self.assertEqual(10, bits_for_length(18, MODE_KANJI))
        self.assertEqual(11, bits_for_length(18, MODE_ALPHA_NUM))
        self.assertEqual(12, bits_for_length(18, MODE_NUMBER))

        self.assertEqual(12, bits_for_length(28, MODE_KANJI))
        self.assertEqual(13, bits_for_length(28, MODE_ALPHA_NUM))
        self.assertEqual(14, bits_for_length(28, MODE_NUMBER))

        self.assertEqual(8, bits_for_length(8, MODE_BYTES))
        self.assertEqual(16, bits_for_length(18, MODE_BYTES))
        self.assertEqual(16, bits_for_length(28, MODE_BYTES))

    def test_illegal_char_counts(self):
        # illegal version
        self.assertRaises(ValueError, lambda: bits_for_length(0, 1))
        self.assertRaises(ValueError, lambda: bits_for_length(41, 1))
        self.assertRaises(ValueError, lambda: bits_for_length(8.5, 1))

        # illegal modes
        self.assertRaises(TypeError, lambda: bits_for_length(8, 0))
        self.assertRaises(TypeError, lambda: bits_for_length(8, -1))
        self.assertRaises(TypeError, lambda: bits_for_length(8, 3))
        self.assertRaises(TypeError, lambda: bits_for_length(8, 7))
        self.assertRaises(TypeError, lambda: bits_for_length(8, 9))