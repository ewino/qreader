import os
from unittest import TestCase
from PIL import Image
from qreader.constants import ERROR_CORRECT_L, ERROR_CORRECT_H
from qreader.scanner import Scanner

__author__ = 'ewino'


class TestScanner(TestCase):

    def _get_img_res(self, name):
        return Image.open(os.path.join(os.path.dirname(__file__), 'resources', name))

    def _get_res_scanner(self, res_name):
        return Scanner(self._get_img_res(res_name))

    def test_canvas_size(self):
        self.assertEqual((0, 0, 146, 146), self._get_res_scanner('Qr-1-noborder.png').info.canvas)
        self.assertEqual((0, 0, 199, 199), self._get_res_scanner('Qr-2-noborder.png').info.canvas)
        self.assertEqual((36, 36, 182, 182), self._get_res_scanner('Qr-1.png').info.canvas)
        self.assertEqual((35, 35, 184, 184), self._get_res_scanner('Qr-2.png').info.canvas)

    def test_info(self):
        def _assert_info(res_name, version, ec, mask):
            info = self._get_res_scanner(res_name).info
            self.assertEqual(version, info.version)
            self.assertEqual(ec, info.error_correction_level)
            self.assertEqual(mask, info.mask_id)

        _assert_info('Qr-1-noborder.png', 1, ERROR_CORRECT_H, 1)
        _assert_info('Qr-1.png', 1, ERROR_CORRECT_H, 1)
        _assert_info('Qr-2-noborder.png', 2, ERROR_CORRECT_L, 2)
        _assert_info('Qr-2.png', 2, ERROR_CORRECT_H, 2)
        _assert_info('Qr-2-numeric.png', 2, ERROR_CORRECT_H, 4)
        _assert_info('Qr-2-alphanumeric.png', 2, ERROR_CORRECT_H, 5)

    def test_size(self):
        self.assertEqual(209, len(list(self._get_res_scanner('Qr-1-noborder.png'))))
        self.assertEqual(360, len(list(self._get_res_scanner('Qr-2-noborder.png'))))
        self.assertEqual(209, len(list(self._get_res_scanner('Qr-1.png'))))
        self.assertEqual(360, len(list(self._get_res_scanner('Qr-2.png'))))

    def test_info_str(self):
        self.assertEqual('<version 1, size 21, ec 2, mask 1>', str(self._get_res_scanner('Qr-1-noborder.png').info))
        self.assertEqual('<version 2, size 25, ec 2, mask 2>', str(self._get_res_scanner('Qr-2.png').info))