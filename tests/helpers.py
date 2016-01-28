import os
from unittest import TestCase as BaseTestCase

from PIL import Image


class TestCase(BaseTestCase):

    def _get_img_res_path(self, *path):
        return os.path.join(os.path.dirname(__file__), 'resources', 'scanner', *path)

    def _get_img_res(self, name):
        return Image.open(self._get_img_res_path(name))

    def _get_txt_res_path(self, *path):
        if path and '.' not in path[-1]:
            path = list(path)  # as it's a tuple that doesn't support item assignment
            path[-1] += '.txt'
        return os.path.join(os.path.dirname(__file__), 'resources', 'decoder', *path)
