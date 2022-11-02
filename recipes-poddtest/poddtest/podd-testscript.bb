DESCRIPTION = "Install PODD Test Script"
LICENSE = "CLOSED"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI = "file://pmic.py \
	   file://PODD_factory_test.py \
           file://PODD_factory_test_config.json \
           file://comms.py \
           file://gpio.py \
           file://power_monitor.py"

do_install() {
    install -d ${D}/${base_dir}/home/root
    install -m 0644 ${WORKDIR}/pmic.py ${D}/${base_dir}/home/root
    install -m 0644 ${WORKDIR}/PODD_factory_test_config.json ${D}/${base_dir}/home/root
    install -m 0644 ${WORKDIR}/PODD_factory_test.py ${D}/${base_dir}/home/root
    install -m 0644 ${WORKDIR}/comms.py ${D}/${base_dir}/home/root
    install -m 0644 ${WORKDIR}/gpio.py ${D}/${base_dir}/home/root
    install -m 0644 ${WORKDIR}/power_monitor.py ${D}/${base_dir}/home/root
}

FILES_${PN} = "/home/root/*"
