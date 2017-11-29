import six
from PIL import Image

from qreader.api import read
from tests.helpers import TestCase, EXAMPLES


class TestRead(TestCase):
    def test_with_image(self):
        read(Image.open(EXAMPLES.simple_1.img_res_path))

    def test_with_path(self):
        read(EXAMPLES.simple_1.img_res_path)

    def test_with_file(self):
        with open(EXAMPLES.simple_1.img_res_path, 'rb') as f:
            read(f)

    def test_with_weird_values(self):
        for val in (None, ['bread', 'eggs', 'sugar'], TestRead, six.moves.xrange(12)):
            self.assertRaises(TypeError, read, val)

    def test_with_wrong_path(self):
        exception_type = FileNotFoundError if six.PY3 else IOError
        self.assertRaises(exception_type, read, EXAMPLES.simple_1.img_res_path.replace('.', '-'))
