from io import BufferedIOBase

import six
import PIL.Image

from qreader.decoder import QRDecoder
from qreader.scanner import ImageScanner

__author__ = 'ewino'

__all__ = ['read']


def read(image_or_path, raw_in_bytes_mode=False):
    """
    Accepts either a path to a file, a PIL image, or a file-like object and reads a QR code data from it.
    :param str|PIL.Image.Image|file|BufferedIOBase image_or_path: The source containing the QR code.
    :return: The data encoded in the QR code.
    :rtype: str|unicode|int|qreader.vcard.vCard
    """
    if isinstance(image_or_path, (six.string_types + (BufferedIOBase,))) or \
            (six.PY2 and isinstance(image_or_path, file)):
        image_or_path = PIL.Image.open(image_or_path)
    if isinstance(image_or_path, PIL.Image.Image):
        data = ImageScanner(image_or_path)
        decoder = QRDecoder(data, raw_in_bytes_mode=raw_in_bytes_mode)
        return decoder.get_first()
        # result = decoder.get_all()
        # if len(result) == 0:
        #     return None
        # elif len(result) == 1:
        #     return result[0]
        # else:
        #     return result
    raise TypeError('parameter should be a PIL image object, a file-like object, or a path to an image file')
