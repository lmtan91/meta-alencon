SUMMARY = "Cross-platform locking library"
DESCRIPTION = "Portalocker is a library to provide an easy API to file locking"
LICENSE = "PSF-2.0"

LIC_FILES_CHKSUM = "file://LICENSE;md5=152634da660a374ca18c0734ed07c63c"

SRC_URI[sha256sum] = "964f6830fb42a74b5d32bce99ed37d8308c1d7d44ddf18f3dd89f4680de97b39"

inherit pypi setuptools3

BBCLASSEXTEND = "native nativesdk"
