
SUMMARY = "Construct is a powerful declarative and symmetrical parser and builder for binary data."
HOMEPAGE = "https://construct.readthedocs.io/en/latest/"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=3fd0f2c25089e629957285e6bc402a20"

inherit setuptools3 pypi

SRC_URI[md5sum] = "147ae4d55da29c961438480ca16832fb"
SRC_URI[sha256sum] = "9c3f4273e8978b7a5ef17b1a54e8858fb11d0f1e50f3d51d399cce3efc434bf1"

BBCLASSEXTEND = "native nativesdk"
