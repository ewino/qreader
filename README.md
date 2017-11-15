# qreader
A pure python reader for QR codes. Made to be compatible to Python 2.7 to 3.6+.

We use the easy-to-install Pillow package to load the pictures, so lots of picture formats are supported.

[![Build Status](https://travis-ci.org/ewino/qreader.svg?branch=master)](https://travis-ci.org/ewino/qreader)

Status
-----------
The package is a work in progress. It can currently decode right-side-up QR codes images generated on a computer (not pictures of printed codes).

Features left to be implemented:

* QR data error correction (currently being researched and implemented)
* image recognition to recognize QR codes in camera pictures

Usage
-----------
    qreader.read(source)  # source can be a file-like object, a PIL image, or a path to a local file

For example:

    import qreader
    from urllib.request import urlopen
    
    url = 'https://upload.wikimedia.org/wikipedia/commons/8/8f/Qr-2.png'
    data = qreader.read(urlopen(url))
    print(data)  # prints "Version 2"
    
Any ideas or issues will be gladly received in the issues panel or by PMing me (ewino)
