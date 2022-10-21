SUMMARY = "Pythonic argument parser, that will make you smile"
HOMEPAGE = "https://github.com/beerfactory/hbmqtt"
LICENSE = "CLOSED"
LIC_FILES_CHKSUM = ""

SRC_URI = "git://github.com/tcsmith13/hbmqtt;branch=master"

SRCREV_pn-${PN} = "83c738b7b4111e753aaa40d1cd45fe2a43a9b3c6"

S = "${WORKDIR}/git/"

inherit setuptools3


BBCLASSEXTEND = "native nativesdk"
    