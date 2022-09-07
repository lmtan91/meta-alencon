FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI += "file://wpa_supplicant.service \
            file://interfaces"

SYSTEMD_AUTO_ENABLE_${PN} = "disable"

do_install_append () {
        if ${@bb.utils.contains('DISTRO_FEATURES','systemd','true','false',d)}; then
                install -d ${D}/${systemd_unitdir}/system
                install -m 644 ${WORKDIR}/wpa_supplicant.service ${D}/${systemd_unitdir}/system
        fi
	install -d ${D}${sysconfdir}/network
	install -m 644 ${WORKDIR}/interfaces ${D}${sysconfdir}/network/
}

