# encoding=utf-8

import os
from unittest import TestCase
from qreader.constants import MODE_ECI, MODE_STRUCTURED_APPEND
from qreader.decoder import QRDecoder
from qreader.scanner import Scanner, QRCodeInfo

__author__ = 'ewino'


# noinspection PyMissingConstructor
class TextFileScanner(Scanner):

    def __init__(self, filepath, version):
        with open(filepath, 'r') as f:
            self.data = f.read()
        self.info = QRCodeInfo()
        self.info.version = version
        self.position = 0
        self.reset()

    def read_bit(self):
        self.position += 1
        return self.data[min(self.position - 1, len(self.data) - 1)]

    def reset(self):
        self.position = 0


# noinspection PyMissingConstructor
class MockDecoder(QRDecoder):
    def __init__(self, source, version):
        self.scanner = TextFileScanner(source, version)


class TestDecoder(TestCase):
    def _get_res_path(self, *path):
        return os.path.join(os.path.dirname(__file__), 'resources', *path)

    def _get_decoder(self, filename, version):
        return MockDecoder(self._get_res_path(filename), version)

    def test_numeric(self):
        self.assertEqual(self._get_decoder('nums-H.txt', 2).get_first(), 1112223330020159990)
        self.assertEqual(self._get_decoder('Numeric-Mod-2-M.txt', 5).get_first(), 55)

    def test_alphanumeric(self):
        self.assertEqual(self._get_decoder('HELLOW-H.txt', 2).get_first(), 'HELLO WORLD')

    def test_bytes(self):
        self.assertEqual(self._get_decoder('Pi-L.txt', 2).get_first(), 'pi=3.14159265358979')
        self.assertEqual(self._get_decoder('Version2-H.txt', 2).get_first(), 'Version 2')
        self.assertEqual(self._get_decoder('Latin-L.txt', 3).get_first(), u'û ü ý þ')

    def test_kanji(self):
        self.assertEqual(self._get_decoder('shintaka-Q.txt', 1).get_first(), u'新高')

    def test_eci(self):
        self.assertRaises(NotImplementedError, lambda: self._get_decoder('shintaka-Q.txt', 1)._decode_message(MODE_ECI))

    def test_multi(self):
        self.assertRaises(NotImplementedError, lambda: self._get_decoder('shintaka-Q.txt', 1)
                          ._decode_message(MODE_STRUCTURED_APPEND))

    def test_iteration(self):
        messages = self._get_decoder('HELLOW-H.txt', 2).get_all()
        messages2 = []
        for message in self._get_decoder('HELLOW-H.txt', 2):
            messages2.append(message)
        self.assertEqual(messages, messages2)
        self.assertEqual(1, len(messages))
        self.assertEqual(messages[0], 'HELLO WORLD')
