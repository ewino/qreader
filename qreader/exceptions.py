
class QrReadingException(Exception):
    pass


class QrImageException(QrReadingException):
    pass


class QrCorruptError(QrReadingException):
    pass


class QrImageRecognitionException(QrImageException):
    pass


class QrFormatError(Exception):
    pass


class IllegalQrMessageModeId(QrFormatError):
    def __init__(self, mode_id):
        super(IllegalQrMessageModeId, self).__init__('Unknown mode ID: {0!r:s}'.format(mode_id, ))


class IllegalQrVersionError(QrFormatError):
    def __init__(self, version):
        super(IllegalQrVersionError, self).__init__(
            'Illegal QR version: {0!r:s} (should be integer between 1-40)'.format(version, ))
