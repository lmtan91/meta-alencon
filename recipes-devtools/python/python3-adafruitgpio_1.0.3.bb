DERIPTION = "Library to provide a cross-platform GPIO interface on the Raspberry Pi and Beaglebone Black using the RPi.GPIO and Adafruit_BBIO libraries"
SECTION = "devel/python"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://PKG-INFO;md5=e41c52dbe1b96447d1c50129a124f586"

SRC_URI[md5sum] = "dfcdb1ba90188d18ba80b6d2958c8c33"
SRC_URI[sha256sum] = "d6465b92c866c51ca8f3bc1e8f2ec36f5ccdb46d0fd54101c1109756d4a2dcd0"

PYPI_PACKAGE = "Adafruit_GPIO"
inherit pypi setuptools3
