# encoding=utf-8

import os
from unittest import TestCase
from qreader.constants import MODE_ECI, MODE_STRUCTURED_APPEND
from qreader.decoder import QRDecoder
from qreader.scanner import Scanner, QRCodeInfo
from qreader.vcard import vCard

__author__ = 'ewino'


class TextFileScanner(Scanner):

    def __init__(self, file_path, version):
        self._test_data_path = file_path
        self._test_version = version
        super(TextFileScanner, self).__init__(None)

    def prepare_source(self):
        pass

    def read_info(self):
        info = QRCodeInfo()
        info.version = self._test_version
        return info

    def _read_all_data(self):
        with open(self._test_data_path, 'r') as f:
            return [int(x) for x in f.read()]


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
        self.assertEqual(1112223330020159990, self._get_decoder('nums-H.txt', 2).get_first())
        self.assertEqual(55, self._get_decoder('Numeric-Mod-2-M.txt', 5).get_first())

    def test_alphanumeric(self):
        self.assertEqual('HELLO WORLD', self._get_decoder('HELLOW-H.txt', 2).get_first())
        self.assertEqual('http://google.co.tz', self._get_decoder('URL-M.txt', 2).get_first())

    def test_bytes(self):
        self.assertEqual('pi=3.14159265358979', self._get_decoder('Pi-L.txt', 2).get_first())
        self.assertEqual('Version 2', self._get_decoder('Version2-H.txt', 2).get_first())
        self.assertEqual(u'û ü ý þ', self._get_decoder('Latin-L.txt', 3).get_first())

    def test_kanji(self):
        self.assertEqual(u'新高', self._get_decoder('shintaka-Q.txt', 1).get_first())

    def test_unknown_type(self):
        with self.assertRaises(TypeError) as cm:
            self._get_decoder('nums-malformed-H.txt', 1).get_first()
        self.assertEqual('Unknown mode number: 15', cm.exception.args[0])

    def test_eci(self):
        self.assertRaises(NotImplementedError, lambda: self._get_decoder('shintaka-Q.txt', 1)._decode_message(MODE_ECI))

    def test_multi(self):
        self.assertRaises(NotImplementedError, lambda: self._get_decoder('shintaka-Q.txt', 1)
                          ._decode_message(MODE_STRUCTURED_APPEND))

    def test_vcard(self):
        card = self._get_decoder('vCard-L.txt', 3).get_first()
        self.assertTrue(vCard, type(card))
        self.assertEqual(('Blabla', 'Bla Bla'), card.name)
        self.assertEqual(('CELL', '123456789'), card.phones[0])

    def test_iteration(self):
        messages = self._get_decoder('HELLOW-H.txt', 2).get_all()
        messages2 = []
        for message in self._get_decoder('HELLOW-H.txt', 2):
            messages2.append(message)
        self.assertEqual(messages, messages2)
        self.assertEqual(1, len(messages))
        self.assertEqual('HELLO WORLD', messages[0])
