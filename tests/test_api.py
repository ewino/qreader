import six
from PIL import Image

from qreader.api import read
from tests.helpers import TestCase


class TestReadImage(TestCase):
    def test_with_image(self):
        read(Image.open(self._get_img_res_path('Qr-1.png')))

    def test_with_path(self):
        read(self._get_img_res_path('Qr-1.png'))

    def test_with_file(self):
        read(open(self._get_img_res_path('Qr-1.png'), 'rb'))

    def test_with_weird_values(self):
        for val in (None, ['bread', 'eggs', 'sugar'], TestReadImage, six.moves.xrange(12)):
            self.assertRaises(TypeError, read, val)

    def test_with_wrong_path(self):
        exception_type = FileNotFoundError if six.PY3 else IOError
        self.assertRaises(exception_type, read, self._get_img_res_path('Qr-91.png'))
