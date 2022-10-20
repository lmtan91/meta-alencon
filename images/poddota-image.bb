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
IMAGE_INSTALL_append = " jq p7zip rtl8821cu dhcp-client openssh python3-pyserial \
                       python3-netifaces python3-adafruitgpio python3-docopt python3-adafruit-bbio \
                       podd-testscript swupdate swupdate-www libubootenv u-boot-fw-utils \
			python3-passlib python3-six python3-click python3-colorama python3-construct python3-flask \
            python3-plotly python3-portalocker python3-pygments python3-pymodbus python3-pyserial \
            python3-pytz python3-pyyaml python3-six python3-tenacity python3-transitions python3-websockets \
            python3-werkzeug python3-numpy"

IMAGE_FSTYPES += "ext4.gz"

export IMAGE_BASENAME = "poddota-image"
