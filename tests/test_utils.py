from qreader.utils import is_rect_overlapping, is_range_overlapping, ints_to_bytes, bytes_to_ints, bits_to_ints, \
    ints_to_bits
from tests.helpers import TestCase

__author__ = 'ewino'


class TestOverlap(TestCase):
    def test_overlapping_ranges(self):
        # partial overlap
        self.assertTrue(is_range_overlapping((1, 3), (2, 4)))
        self.assertTrue(is_range_overlapping((-8, -2), (-5, 4)))
        # a contains b
        self.assertTrue(is_range_overlapping((1, 5), (2, 4)))
        # b contains a
        self.assertTrue(is_range_overlapping((1, 5), (0, 6)))

    def test_non_overlapping_ranges(self):
        # negatives
        self.assertFalse(is_range_overlapping((-8, -6), (-4, -2)))
        self.assertFalse(is_range_overlapping((-4, -2), (-8, -6)))
        # positives
        self.assertFalse(is_range_overlapping((8, 6), (4, 2)))
        self.assertFalse(is_range_overlapping((4, 2), (8, 6)))
        # both
        self.assertFalse(is_range_overlapping((-8, -2), (2, 8)))
        self.assertFalse(is_range_overlapping((-1, 1), (2, 3)))

    def test_overlapping_zones(self):
        # [-----[-]----]
        # [     [ ]    ]
        # [_____[_]____]
        self.assertTrue(is_rect_overlapping((1, 1, 4, 4), (3, 1, 6, 4)))
        # [-------]
        # [     [-]----]
        # [_____[_]    ]
        #       [______]
        self.assertTrue(is_rect_overlapping((1, 1, 4, 4), (3, 3, 6, 6)))
        # [-------]
        # [-------]
        # [_______]
        # [_______]
        self.assertTrue(is_rect_overlapping((1, 1, 4, 4), (1, 3, 4, 6)))
        # a contains b
        self.assertTrue(is_rect_overlapping((1, 1, 4, 4), (2, 2, 4, 4)))
        self.assertTrue(is_rect_overlapping((1, 1, 4, 4), (2, 2, 3, 3)))
        # b contains a
        self.assertTrue(is_rect_overlapping((2, 2, 4, 4), (1, 1, 4, 4)))
        self.assertTrue(is_rect_overlapping((2, 2, 3, 3), (1, 1, 4, 4)))
        # point rect
        self.assertTrue(is_rect_overlapping((2, 2, 4, 4), (4, 4, 4, 4)))

    def test_non_overlapping_zones(self):
        # [-----] [-----]
        # [     ] [     ]
        # [_____] [_____]
        self.assertFalse(is_rect_overlapping((1, 1, 4, 4), (5, 1, 8, 4)))
        # [--]
        # [__]
        #      [--]
        #      [__]
        self.assertFalse(is_rect_overlapping((1, 1, 4, 4), (5, 5, 8, 8)))
        # [-------]
        # [_______]
        #
        # [-------]
        # [_______]
        self.assertFalse(is_rect_overlapping((1, 1, 4, 4), (1, 5, 4, 8)))


class TestIntsToBytes(TestCase):
    def test_normal(self):
        self.assertEqual('Hello', ints_to_bytes([72, 101, 108, 108, 111]).decode('utf-8'))

    def test_empty(self):
        self.assertEqual(0, len(ints_to_bytes([])))


class TestBytesToInts(TestCase):
    def test_normal(self):
        self.assertEqual([72, 101, 108, 108, 111], bytes_to_ints('Hello'.encode('utf-8')))

    def test_empty(self):
        self.assertEqual(0, len(bytes_to_ints([])))


class TestBitsToInts(TestCase):
    def test_default_params(self):
        self.assertEqual([], bits_to_ints([]))
        self.assertEqual([0], bits_to_ints([0, 0, 0, 0, 0, 0, 0, 0]))
        self.assertEqual([1], bits_to_ints([0, 0, 0, 0, 0, 0, 0, 1]))
        self.assertEqual([2], bits_to_ints([0, 0, 0, 0, 0, 0, 1, 0]))
        self.assertEqual([7], bits_to_ints([0, 0, 0, 0, 0, 1, 1, 1]))
        self.assertEqual([0, 1, 2], bits_to_ints([0, 0, 0, 0, 0, 0, 0, 0,
                                                  0, 0, 0, 0, 0, 0, 0, 1,
                                                  0, 0, 0, 0, 0, 0, 1, 0]))

    def test_with_offset(self):
        self.assertEqual([0], bits_to_ints([0, 0, 0, 0, 0, 0, 0, 0, 0], offset=1))
        self.assertEqual([2], bits_to_ints([0, 0, 0, 0, 0, 0, 0, 1, 0], offset=1))

    def test_with_different_int_size(self):
        self.assertEqual([0, 1, 0, 1, 1, 1], bits_to_ints([0, 1, 0, 1, 1, 1], bits_in_byte=1))
        self.assertEqual([0, 1, 2, 3, 4], bits_to_ints([0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0], bits_in_byte=3))

    def test_with_both(self):
        self.assertEqual([2, 1, 0], bits_to_ints([0, 1, 0, 0, 1, 0, 0], bits_in_byte=2, offset=1))


class TestIntsToBits(TestCase):
    def test_normal(self):
        self.assertEqual([], ints_to_bits([]))
        self.assertEqual([0, 0, 0, 0, 0, 0, 0, 0], ints_to_bits([0]))
        self.assertEqual([0, 0, 0, 0, 0, 0, 0, 1], ints_to_bits([1]))
        self.assertEqual([0, 0, 0, 0, 0, 0, 1, 0], ints_to_bits([2]))
        self.assertEqual([0, 0, 0, 0, 0, 1, 1, 1], ints_to_bits([7]))
        self.assertEqual([0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0, 0, 1,
                          0, 0, 0, 0, 0, 0, 1, 0], ints_to_bits([0, 1, 2]))
        self.assertEqual([1] * 8, ints_to_bits([0xff]))

    def test_exceeding_size(self):
        self.assertEqual([0, 0, 0, 0, 0, 0, 0, 1], ints_to_bits([0x101]))

    def test_with_different_bits_amount(self):
        self.assertEqual([0, 1, 0, 1, 1, 1], ints_to_bits([0, 1, 0, 1, 1, 1], bits_in_byte=1))
        self.assertEqual([0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0], ints_to_bits([0, 1, 2, 3, 4], bits_in_byte=3))
