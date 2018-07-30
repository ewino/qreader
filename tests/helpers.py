# encoding=utf-8

import os
from unittest import TestCase as BaseTestCase

from PIL import Image
from qreader.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H


class Example(object):
    def __init__(self, img_name, version, ec_mode, mask, txt_name=None):
        self.img_name = img_name
        if txt_name and '.' not in txt_name:
            txt_name += '.txt'
        self.txt_name = txt_name
        self.version = version
        self.ec_mode = ec_mode
        self.mask = mask
        self._validate()

    def _validate(self):
        if self.img_name:
            assert os.path.exists(self.img_res_path), 'Example image file missing ({0})'.format(self.img_res_path)
        if self.txt_name:
            assert os.path.exists(self.txt_res_path), 'Example text file missing ({0})'.format(self.txt_res_path)

    @property
    def img_res_path(self):
        if not self.img_name:
            raise ValueError('Resource does not have image file')
        return os.path.join(os.path.dirname(__file__), 'resources', 'scanner', self.img_name)

    def get_img_res(self):
        return Image.open(self.img_res_path)

    @property
    def txt_res_path(self):
        if not self.txt_name:
            raise ValueError('Resource does not have content txt file')
        return os.path.join(os.path.dirname(__file__), 'resources', 'decoder', self.txt_name)


class EXAMPLES:
    simple_1 = Example('Qr-1.png', 1, ERROR_CORRECT_H, mask=1)  # Ver1
    simple_2 = Example('Qr-2.png', 2, ERROR_CORRECT_H, mask=2, txt_name='Version2.txt')  # Version 2
    # TODO: LATIN-L doesn't match it's text file (text file version preferred). Should regenerate it (ewino@2016-01-30)
    simple_3 = Example('Qr-3-Latin-L.jpg', 3, ERROR_CORRECT_L, mask=4, txt_name='Latin-L.txt')  # Hello!

    noborder_1 = Example('Qr-1-noborder.png', 1, ERROR_CORRECT_H, mask=1)  # Ver1
    noborder_2 = Example('Qr-2-noborder.png', 2, ERROR_CORRECT_L, mask=2, txt_name='Pi-L.txt')  # pi=3.14159265358979
    transparent_border = Example('Qr-5-transparent-edges.png', 5, ERROR_CORRECT_H, mask=1)  # ???

    kanji = Example('Qr-1-kanji.png', 1, ERROR_CORRECT_Q, mask=2, txt_name='shintaka-Q.txt')  # 新高
    alphanum = Example('Qr-2-alphanumeric.png', 2, ERROR_CORRECT_H, mask=5, txt_name='HELLOW-H.txt')  # HELLO WORLD
    numeric = Example('Qr-2-numeric.png', 2, ERROR_CORRECT_H, mask=4, txt_name='nums-H.txt')  # 1112223330020159990
    numeric_2 = Example('Qr-3-Numeric-Mod-2-M.gif', 3, ERROR_CORRECT_M, mask=4, txt_name='Numeric-Mod-2-M.txt')  # 55
    url = Example('Qr-2-URL.jpg', 2, ERROR_CORRECT_L, mask=2, txt_name='URL-M.txt')  # http://google.co.tz
    # TODO: vCard-L doesn't match it's text file (text file version preferred). Should regenerate it (ewino@2016-01-30)
    vcard = Example('Qr-8-vCard-L.jpg', 8, ERROR_CORRECT_L, mask=3, txt_name='vCard-L.txt')  # vCard

    broken_pattern_1 = Example('Qr-1-broken-pattern-1.png', 1, ERROR_CORRECT_Q, mask=1)  # top-left noise
    broken_pattern_2 = Example('Qr-1-broken-pattern-2.png', 1, ERROR_CORRECT_Q, mask=1)  # top-right noise
    broken_pattern_3 = Example('Qr-1-broken-pattern-3.png', 1, ERROR_CORRECT_Q, mask=1)  # bottom-right noise
    broken_too_light = Example('Qr-1-broken-too-light.png', 1, ERROR_CORRECT_Q, mask=1)  # code is in very light gray

    broken_message_mode = Example(None, 2, ERROR_CORRECT_Q, mask=4, txt_name='nums-malformed-H.txt')  # 1112223330...


class TestCase(BaseTestCase):

    def assertRaisesMsg(self, exc_type, func, exc_msg, *args, **kwargs):
        with self.assertRaises(exc_type) as cm:
            func(*args, **kwargs)
        self.assertEqual(cm.exception.args[0], exc_msg)
