import os

from setuptools import setup

PACKAGE_NAME = "qreader"

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, "README.md")) as f:
    long_description = f.read()

setup(
    name=PACKAGE_NAME,
    version="0.1",
    description="A pure python reader for QR codes.",
    url="https://github.com/ewino/qreader/",
    author="Ehud Winograd",
    maintainer="Ehud Winograd",
    long_description=long_description,
    platforms=["Unix", "Windows"],
    packages=["qreader"],
    requires=['Pillow', 'six', 'python_dateutil', 'reedsolo'],
    setup_requires=[
        "nose>=1.3.6",
    ],
)
