from qreader.scanner import Scanner

__author__ = 'ewino'


class QRDecoder(object):
    def __init__(self, source):
        self.scanner = Scanner(source)

    def get_first(self):
        for item in self:
            return item
        return None

    def __iter__(self):
        yield self._decode_next_message()

    def _decode_next_message(self):
        mode = self.scanner.get_int(4)
        print(mode)

    def get_all(self):
        return list(self)
