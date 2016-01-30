# encoding=utf-8

from qreader.constants import MODE_ECI, MODE_STRUCTURED_APPEND, ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, \
    ERROR_CORRECT_H
from qreader.decoder import QRDecoder
from qreader.exceptions import IllegalQrMessageModeId
from qreader.scanner import QRCodeInfo, Scanner
from qreader.vcard import vCard
from tests.helpers import TestCase, EXAMPLES

__author__ = 'ewino'


class TextFileScanner(Scanner):
    def __init__(self, file_path, version, ec_level):
        self._data_path = file_path
        self._version = version
        self._ec_level = ec_level
        super(TextFileScanner, self).__init__()

    def read_info(self):
        self._info = QRCodeInfo()
        self.info.version = self._version
        self.info.error_correction_level = self._ec_level

    def _read_all_data(self):
        with open(self._data_path, 'r') as f:
            return [int(x) for x in f.read()]


class TestDecoder(TestCase):
    def _get_decoder(self, res):
        """
        :type res: tests.helpers.Example
        :rtype: QRDecoder
        """
        return QRDecoder(TextFileScanner(res.txt_res_path, res.version, res.ec_mode))

    def test_numeric(self):
        self.assertEqual(1112223330020159990, self._get_decoder(EXAMPLES.numeric).get_first())
        self.assertEqual(55, self._get_decoder(EXAMPLES.numeric_2).get_first())

    def test_alphanumeric(self):
        self.assertEqual('HELLO WORLD', self._get_decoder(EXAMPLES.alphanum).get_first())
        self.assertEqual('http://google.co.tz', self._get_decoder(EXAMPLES.url).get_first())

    def test_bytes(self):
        self.assertEqual('pi=3.14159265358979', self._get_decoder(EXAMPLES.noborder_2).get_first())
        self.assertEqual('Version 2', self._get_decoder(EXAMPLES.simple_2).get_first())
        self.assertEqual(u'û ü ý þ', self._get_decoder(EXAMPLES.simple_3).get_first())

    def test_kanji(self):
        self.assertEqual(u'新高', self._get_decoder(EXAMPLES.kanji).get_first())

    def test_unknown_type(self):
        self.assertRaisesMsg(IllegalQrMessageModeId, self._get_decoder(EXAMPLES.broken_message_mode).get_first,
                             'Unknown mode ID: 15')

    def test_eci(self):
        self.assertRaises(NotImplementedError, lambda: self._get_decoder(EXAMPLES.kanji)._decode_message(MODE_ECI))

    def test_multi(self):
        self.assertRaises(NotImplementedError,
                          lambda: self._get_decoder(EXAMPLES.kanji)._decode_message(MODE_STRUCTURED_APPEND))

    def test_vcard(self):
        card = self._get_decoder(EXAMPLES.vcard).get_first()
        self.assertTrue(vCard, type(card))
        self.assertEqual(('Blabla', 'Bla Bla'), card.name)
        self.assertEqual(('CELL', '123456789'), card.phones[0])

    def test_iteration(self):
        messages = self._get_decoder(EXAMPLES.alphanum).get_all()
        messages2 = []
        for message in self._get_decoder(EXAMPLES.alphanum):
            messages2.append(message)
        self.assertEqual(messages, messages2)
        self.assertEqual(1, len(messages))
        self.assertEqual('HELLO WORLD', messages[0])
