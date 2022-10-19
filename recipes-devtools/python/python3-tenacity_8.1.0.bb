SUMMARY = "Retry code until it succeeds"
DESCRIPTION = "Tenacity is a general-purpose retrying library to simplify the task of adding retry behavior to just about anything"
LICENSE = "PSF-2.0"

LIC_FILES_CHKSUM = "file://LICENSE;md5=175792518e4ac015ab6696d16c4f607e"

SRC_URI[sha256sum] = "e48c437fdf9340f5666b92cd7990e96bc5fc955e1298baf4a907e3972067a445"

inherit pypi setuptools3

BBCLASSEXTEND = "native nativesdk"

DEPENDS += " python3-setuptools-scm-native"