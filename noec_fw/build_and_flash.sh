#!/usr/bin/bash

arduino-cli compile -u -p /dev/cu.usbmodem11301 \
            --build-property build.extra_flags=-IEmbeddedProto/src \
            --fqbn arduino:mbed_nano:nano33ble noec_fw
