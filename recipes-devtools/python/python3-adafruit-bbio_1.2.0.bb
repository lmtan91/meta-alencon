DERIPTION = "Library to provide a cross-platform GPIO interface on the Raspberry Pi and Beaglebone Black using the RPi.GPIO and Adafruit_BBIO libraries"
SECTION = "devel/python"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://PKG-INFO;md5=4c8f4d4ff273aabd9e8e46121f10ffd4"

SRC_URI[md5sum] = "0a5e6883af4341bbb40a8e5f3c960ff2"
SRC_URI[sha256sum] = "5edcb8abd32b5f78365f6131f1d24cd78c419d60f469fc828518688cf39fdbad"

PYPI_PACKAGE = "Adafruit_BBIO"
inherit pypi setuptools3
