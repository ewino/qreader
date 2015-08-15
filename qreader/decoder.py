from qreader.constants import MODE_NUMBER, MODE_ALPHA_NUM, ALPHANUM_CHARS, MODE_BYTES, MODE_KANJI, MODE_ECI, \
    MODE_STRUCTURED_APPEND
from qreader.scanner import Scanner
from qreader.utils import bits_for_length, ints_to_bytes

__author__ = 'ewino'


class QRDecoder(object):

    def __init__(self, source):
        self.scanner = Scanner(source)  # pragma: no cover

    @property
    def version(self):
        return self.scanner.info.version

    def get_first(self):
        return self._decode_next_message()

    def __iter__(self):
        yield self._decode_next_message()

    def get_all(self):
        return list(self)

    def _decode_next_message(self):
        mode = self.scanner.get_int(4)
        return self._decode_message(mode)

    def _decode_message(self, mode):
        if mode == MODE_NUMBER:
            message = self._decode_numeric_message()
        elif mode == MODE_ALPHA_NUM:
            message = self._decode_alpha_num_message()
        elif mode == MODE_BYTES:
            message = self._decode_bytes_message()
        elif mode == MODE_KANJI:
            message = self._decode_kanji_message()
        elif mode == MODE_STRUCTURED_APPEND:
            raise NotImplementedError('Structured append encoding not implemented yet')
        elif mode == MODE_ECI:
            raise NotImplementedError('Extended Channel Interpretation encoding not implemented yet')
        else:  # pragma: no cover
            raise TypeError('Unknown mode number: %s' % mode)
        return message

    def _decode_numeric_message(self):
        char_count = self.scanner.get_int(bits_for_length(self.version, MODE_NUMBER))
        val = 0
        triples, rest = divmod(char_count, 3)
        for _ in range(triples):
            val = val * 1000 + self.scanner.get_int(10)
        if rest == 2:
            val = val * 100 + self.scanner.get_int(7)
        elif rest == 1:
            val = val * 10 + self.scanner.get_int(4)

        return val

    def _decode_alpha_num_message(self):
        char_count = self.scanner.get_int(bits_for_length(self.version, MODE_ALPHA_NUM))
        val = ''
        doubles, has_single = divmod(char_count, 2)
        for _ in range(doubles):
            double = self.scanner.get_int(11)
            val += ALPHANUM_CHARS[double // 45] + ALPHANUM_CHARS[double % 45]
        if has_single:
            val += ALPHANUM_CHARS[self.scanner.get_int(6)]
        return val

    def _decode_bytes_message(self):
        char_count = self.scanner.get_int(bits_for_length(self.version, MODE_BYTES))
        raw = ints_to_bytes(self.scanner.get_int(8) for _ in range(char_count))
        try:
            return raw.decode('utf-8')
        except UnicodeDecodeError:
            return raw.decode('iso-8859-1')

    def _decode_kanji_message(self):
        char_count = self.scanner.get_int(bits_for_length(self.version, MODE_KANJI))
        nums = []
        for _ in range(char_count):
            mashed = self.scanner.get_int(13)
            num = ((mashed // 0xC0) << 8) + mashed % 0xC0
            num += 0x8140 if num < 0x1F00 else 0xC140
            nums.extend(divmod(num, 2 ** 8))
        return ints_to_bytes(nums).decode('shift-jis')
