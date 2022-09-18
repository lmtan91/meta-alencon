FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI += "file://sshd.service"

SYSTEMD_AUTO_ENABLE_${PN} = "enable"

do_install_append () {
        if ${@bb.utils.contains('DISTRO_FEATURES','systemd','true','false',d)}; then
                install -d ${D}/${systemd_unitdir}/system
                install -m 644 ${WORKDIR}/sshd.service ${D}/${systemd_unitdir}/system
        fi

	install -d ${D}${sysconfdir}/systemd/system/multi-user.target.wants
	ln -s ../../../../lib/systemd/system/sshd.service ${D}${sysconfdir}/systemd/system/multi-user.target.wants/sshd.service
}

