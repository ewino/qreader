from unittest.case import TestCase

from qreader.utils import is_overlapping, range_overlap

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
