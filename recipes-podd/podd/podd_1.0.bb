LICENSE = "CLOSED"
inherit systemd

SYSTEMD_AUTO_ENABLE = "enable"
SYSTEMD_SERVICE_${PN} = "podd.service"

SRC_URI_append = " file://podd.service \
		file://hello.py \
"
FILES_${PN} += "${systemd_unitdir}/system/podd.service /home/root/hello.py"

do_install_append() {
  install -d ${D}/${systemd_unitdir}/system
  install -m 0644 ${WORKDIR}/podd.service ${D}/${systemd_unitdir}/system
  install -d ${D}/home/root
  install -m 0644 ${WORKDIR}/hello.py ${D}/home/root
}
