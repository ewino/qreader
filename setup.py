import glob, os
from distutils.core import setup

PACKAGE_NAME = "qreader"

setup(name=PACKAGE_NAME,
      version="0.1",
      description="A pure python reader for QR codes.",
      url="https://github.com/ewino/qreader/",
      author="Ehud Winograd",
      maintainer="Ehud Winograd",
      long_description='A pure python reader for QR codes. Made to be compatible to Python 2.7 to 3.5+.',
      platforms=["Unix", "Windows"],
      packages=['qreader'],
      data_files=[('', ['README.md'] + glob.glob('doc/*')),
                  (os.path.join('tests'), glob.glob('tests/*.py')),
                  (os.path.join('tests', 'resources', 'decoder'), glob.glob('tests/resources/decoder/*')),
                  (os.path.join('tests', 'resources', 'scanner'), glob.glob('tests/resources/scanner/*'))],
      requires=['Pillow', 'six', 'python_dateutil', 'reedsolo'])
