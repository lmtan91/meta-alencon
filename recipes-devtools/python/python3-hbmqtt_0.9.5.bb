SUMMARY = "Pythonic argument parser, that will make you smile"
HOMEPAGE = "https://github.com/beerfactory/hbmqtt"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://license.txt;md5=f81edd0ff3453ee3addd2e22ae80f860"

inherit setuptools3 pypi

SRC_URI[md5sum] = "2916f6094808aa8d586e45d8f88c1c8b"
SRC_URI[sha256sum] = "9886b1c8321d16e971376dc609b902e0c84118846642b5e09f08a4ca876a7f2a"

BBCLASSEXTEND = "native nativesdk"
