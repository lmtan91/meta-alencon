#!/bin/bash

if [[ ! -f /data/wpa_supplicant.conf ]]; then
  cp /etc/wpa_supplicant.conf /data
fi
