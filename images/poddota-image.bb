SUMMARY = "A console development image"
HOMEPAGE = "http://www.jumpnowtek.com"

require images/basic-dev-image.bb

WIFI = " \
    bbgw-wireless \
    crda \
    iw \
    linux-firmware-wl12xx \
    linux-firmware-wl18xx \
    wpa-supplicant \
"

DEV_EXTRAS = " \
    serialecho \
    spiloop \
"

IMAGE_INSTALL += " \
    emmc-upgrader \
    firewall \
    ${DEV_EXTRAS} \
    ${WIFI} \
    ${SECURITY_TOOLS} \
    ${WIREGUARD} \
"
IMAGE_INSTALL_append = " jq p7zip rtl8821cu dhcp-client"

export IMAGE_BASENAME = "console-image"
