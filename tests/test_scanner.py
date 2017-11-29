from qreader.exceptions import QrImageRecognitionException
from qreader.scanner import ImageScanner, Scanner
from tests.helpers import TestCase, EXAMPLES

__author__ = 'ewino'


class TestScanner(TestCase):

    def _get_res_scanner(self, res):
        """
        :type res: tests.helpers.Example
        :rtype: qreader.scanner.ImageScanner
        """
        return ImageScanner(res.get_img_res())

    def _assert_info(self, res):
        info = self._get_res_scanner(res).info
        self.assertEqual(res.version, info.version)
        self.assertEqual(res.ec_mode, info.error_correction_level)
        self.assertEqual(res.mask, info.mask_id)

    def test_canvas_size(self):
        self.assertEqual((0, 0, 146, 146), self._get_res_scanner(EXAMPLES.noborder_1).info.canvas)
        self.assertEqual((0, 0, 199, 199), self._get_res_scanner(EXAMPLES.noborder_2).info.canvas)
        self.assertEqual((36, 36, 182, 182), self._get_res_scanner(EXAMPLES.simple_1).info.canvas)
        self.assertEqual((35, 35, 184, 184), self._get_res_scanner(EXAMPLES.simple_2).info.canvas)
        self.assertEqual((14, 14, 235, 235), self._get_res_scanner(EXAMPLES.transparent_border).info.canvas)

    def test_broken_canvas_sizes(self):
        self.assertRaisesMsg(QrImageRecognitionException, self._get_res_scanner(EXAMPLES.broken_pattern_1).read,
                             'Top-left position pattern not aligned with the top-right one')
        self.assertRaisesMsg(QrImageRecognitionException, self._get_res_scanner(EXAMPLES.broken_pattern_2).read,
                             'Top-left position pattern not aligned with the top-right one')
        self.assertRaisesMsg(QrImageRecognitionException, self._get_res_scanner(EXAMPLES.broken_pattern_3).read,
                             'Top-left position pattern not aligned with the bottom-left one')
        self.assertRaisesMsg(QrImageRecognitionException, self._get_res_scanner(EXAMPLES.broken_too_light).read,
                             "Couldn't find one of the edges (top-left)")

    def test_info(self):
        self._assert_info(EXAMPLES.simple_1)
        self._assert_info(EXAMPLES.simple_2)
        self._assert_info(EXAMPLES.noborder_1)
        self._assert_info(EXAMPLES.noborder_2)
        self._assert_info(EXAMPLES.kanji)
        self._assert_info(EXAMPLES.numeric)
        self._assert_info(EXAMPLES.alphanum)
        self._assert_info(EXAMPLES.vcard)
        self._assert_info(EXAMPLES.transparent_border)

    def test_jpg(self):
        self._assert_info(EXAMPLES.simple_3)
        self._assert_info(EXAMPLES.url)

    def test_gif(self):
        self._assert_info(EXAMPLES.numeric_2)

    def test_size(self):
        self.assertEqual(209, len(list(self._get_res_scanner(EXAMPLES.simple_1))))
        self.assertEqual(209, len(list(self._get_res_scanner(EXAMPLES.noborder_1))))
        self.assertEqual(360, len(list(self._get_res_scanner(EXAMPLES.simple_2))))
        self.assertEqual(360, len(list(self._get_res_scanner(EXAMPLES.noborder_2))))
        # TODO: Add check for version >= 7 (ewino@2015-08-30)

    def test_info_str(self):
        for res in (EXAMPLES.noborder_1, EXAMPLES.simple_2):
            self.assertEqual('<version %d, ec %d, mask %d>' % (res.version, res.ec_mode, res.mask),
                             str(self._get_res_scanner(res).info))


class TestAbstractScanner(TestCase):
    """ Made mostly to appease the coverage runner :P """
    def test_that_its_abstract(self):
        scanner = Scanner()
        self.assertRaises(NotImplementedError, scanner._read_all_data)
        self.assertRaises(NotImplementedError, scanner.read_info)
