SUMMARY = "PODD OTA image for developement/debug "

require poddota-image.bb

IMAGE_INSTALL_append = " cmake nano"

export IMAGE_BASENAME = "poddota-image-dev"
