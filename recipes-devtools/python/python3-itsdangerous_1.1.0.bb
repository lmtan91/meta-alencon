SUMMARY = "Various helpers to pass trusted data to untrusted environments and back."
HOMEPAGE = "http://github.com/mitsuhiko/itsdangerous"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.rst;md5=370799bf709a1e4a6a369fa089ac73a6"

SRC_URI[sha256sum] = "321b033d07f2a4136d3ec762eac9f16a10ccd60f53c0c91af90217ace7ba1f19"

inherit pypi setuptools3

CLEANBROKEN = "1"

RDEPENDS:${PN} += " \
    ${PYTHON_PN}-simplejson \
    ${PYTHON_PN}-netclient \
    ${PYTHON_PN}-compression \
    ${PYTHON_PN}-json \
"