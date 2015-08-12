__author__ = 'ewino'


class QRDecoder(object):
    def __init__(self, source):
        pass

    def get_first(self):
        for item in self:
            return item
        return None

    def __iter__(self):
        yield None

    def get_all(self):
        return list(self)
