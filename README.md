# qreader
A pure python reader for QR codes
[![Build Status](https://travis-ci.org/ewino/qreader.svg?branch=master)](https://travis-ci.org/ewino/qreader)[![Coverage Status](https://coveralls.io/repos/ewino/qreader/badge.svg?branch=master&service=github)](https://coveralls.io/github/ewino/qreader?branch=master)

Status
-----------
The package is a work in progress. It can currently decode right-side-up QR codes images generated on a computer (not pictures of printed codes).

Features left to be implemented:

* QR data error correction (currently being researched and implemented)
* image recognition to recognize QR codes in camera pictures

Usage
-----------
    from PIL import Image
    from qreader.decoder import QRDecoder
    
    # we use the pure-python Pillow package to load the pictures.
    # Lots of picture formats are supported
    qr_image = Image.open('qrcode.png')
    
    # the data returned is usually a unicode/str object 
    # (depending on it's content it might be a vCard instance instead)
    qr_data = QRDecoder(qr_image).get_first()
    
For example:

    from urllib.request import urlopen
    from PIL import Image
    from qreader.decoder import QRDecoder
    
    url = 'https://upload.wikimedia.org/wikipedia/commons/8/8f/Qr-2.png'
    qr_image = Image.open(urlopen(url))
    print(QRDecoder(qr_image).get_first())  # prints "Version 2"
    
Any ideas or issues will be gladly received in the issues panel or by PMing me (ewino)
