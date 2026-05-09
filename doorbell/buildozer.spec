[app]
title          = Doorbell Detector
package.name   = doorbelldetector
package.domain = com.qwerty
source.dir     = .
source.include_exts = py,kv,tflite,csv
version        = 0.1

requirements   = python3,kivy,numpy,tflite-runtime,pyaudio,plyer,python-osc

# Declare the background service (foreground keeps Android from killing it)
services       = Service:service/doorbell_service.py:foreground

android.permissions = RECORD_AUDIO, FOREGROUND_SERVICE, FOREGROUND_SERVICE_MICROPHONE, POST_NOTIFICATIONS
android.minapi  = 26
android.api     = 34
android.archs   = arm64-v8a
android.orientation = portrait
android.allow_backup = True

# Application versioning
version.code = 1

# Icon (32-bit PNG with alpha channel)
# icon.filename = %(source.dir)s/data/icon.png

[buildozer]
log_level = 2
warn_on_root = 1