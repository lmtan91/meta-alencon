FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI += "file://wpa_supplicant.service"

SYSTEMD_AUTO_ENABLE_${PN} = "enable"

do_install_append () {
        if ${@bb.utils.contains('DISTRO_FEATURES','systemd','true','false',d)}; then
                install -d ${D}/${systemd_unitdir}/system
                install -m 644 ${WORKDIR}/wpa_supplicant.service ${D}/${systemd_unitdir}/system
        fi
}

