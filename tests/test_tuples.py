from qreader import tuples
from tests.helpers import TestCase

__author__ = 'ewino'


class TestAdd(TestCase):

    def test_scalar(self):
        t = (-1, 0, 1, 2.5, 3)
        self.assertEqual((-2, -1, 0, 1.5, 2), tuples.add(t, -1))
        self.assertEqual((0, 1, 2, 3.5, 4), tuples.add(t, 1))
        self.assertEqual((.5, 1.5, 2.5, 4, 4.5), tuples.add(t, 1.5))
        self.assertEqual(t, tuples.add(t, 0))

    def test_tuple(self):
        t = (-1, 0, 1, 2.5, 3)
        self.assertEqual((-2, 0, 2, 5, 6), tuples.add(t, (-1, 0, 1, 2.5, 3)))
        self.assertEqual((0,) * 5, tuples.add(t, (1, 0, -1, -2.5, -3)))
        self.assertEqual(t, tuples.add(t, (0,) * 5))

    def test_weird_addition(self):
        t = (-1, 0, 1, 2.5, 3)
        self.assertRaises(TypeError, lambda: tuples.add(t, 'hello'))
        self.assertRaises(TypeError, lambda: tuples.add(t, None))

    def test_too_short_tuple(self):
        t = (-1, 0, 1, 2.5, 3)
        self.assertRaises(IndexError, lambda: tuples.add(t, ()))


class TestMultiply(TestCase):

    def test_scalar(self):
        t = (-1, 0, 1, 2.5, 3)
        self.assertEqual((1, 0, -1, -2.5, -3), tuples.multiply(t, -1))
        self.assertEqual((-1.5, 0, 1.5, 3.75, 4.5), tuples.multiply(t, 1.5))
        self.assertEqual((0,) * 5, tuples.multiply(t, 0))
        self.assertEqual(t, tuples.multiply(t, 1))

    def test_tuple(self):
        t = (-1, 0, 1, 2.5, 3)
        self.assertEqual((0, 0, 1.5, -2.5, 9), tuples.multiply(t, (0, 2, 1.5, -1, 3)))
        self.assertEqual(t, tuples.multiply(t, (1,) * 5))
        self.assertEqual((0,) * 5, tuples.multiply(t, (0,) * 5))

    def test_weird_multiplication(self):
        t = (-1, 0, 1, 2.5, 3)
        self.assertRaises(TypeError, lambda: tuples.multiply(t, 'hello'))
        self.assertRaises(TypeError, lambda: tuples.multiply(t, None))

    def test_too_short_tuple(self):
        t = (-1, 0, 1, 2.5, 3)
        self.assertRaises(IndexError, lambda: tuples.multiply(t, ()))
