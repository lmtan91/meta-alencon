SUMMARY = "Retry code until it succeeds"
DESCRIPTION = "An open-source, interactive data visualization library for Python"
LICENSE = "MIT"

LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=c7b311a6fbf8f1e2f22c16e2ad556f98"

SRC_URI[sha256sum] = "4d36d9859b7a153b273562deeed8c292587a472eb1fd57cd4158ec89d9defadb"

inherit pypi setuptools3

BBCLASSEXTEND = "native nativesdk"

FILES_${PN} += "${datadir}/*"
FILES_${PN}-dev = "${datadir}/*"
