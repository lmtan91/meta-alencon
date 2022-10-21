SUMMARY = "A fully featured modbus protocol stack in python"
HOMEPAGE = "https://github.com/riptideio/pymodbus/"
LICENSE = "CLOSED"
#LIC_FILES_CHKSUM = "file://LICENSE;md5=2c2223d66c7e674b40527b5a4c35bd76"
DEPENDS += "python3-six-native"


SRC_URI = "git://github.com/tcsmith13/pymodbus;branch=dev_v2.2.0rc3"

SRCREV_pn-${PN} = "c01f0d76711ff1f89f5f09b6c0e6507b03285ce0"

S = "${WORKDIR}/git/"

inherit setuptools3

PACKAGECONFIG ??= ""
PACKAGECONFIG[repl] = ",,,python3-aiohttp python3-click python3-prompt-toolkit python3-pygments python3-pyserial-asyncio"
PACKAGECONFIG[asyncio] = ",,,python3-pyserial-asyncio"
PACKAGECONFIG[tornado] = ",,,python3-tornado"
PACKAGECONFIG[twisted] = ",,,python3-twisted-conch"
PACKAGECONFIG[redis] = ",,,python3-redis"
PACKAGECONFIG[sql] = ",,,python3-sqlalchemy"

RDEPENDS:${PN} += " \
    python3-asyncio \
    python3-core \
    python3-io \
    python3-json \
    python3-logging \
    python3-math \
    python3-netserver \
"

RDEPENDS:${PN} += " \
    python3-pyserial \
    python3-six \
"
