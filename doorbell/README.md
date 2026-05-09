# Doorbell Detector for Android

A Python/Kivy Android app that detects doorbell sounds using YAMNet (on-device AI) and fires local notifications.

## Requirements

- Buildozer installed on Linux/WSL (Android builds cannot be done on Windows natively)
- Android SDK/NDK
- Python 3.10+

## Building the APK

```bash
cd doorbell
buildozer android debug
```

The first build will download Android SDK/NDK and compile the APK (~30-60 minutes).

## Structure

```
doorbell/
├── main.py              # Kivy UI
├── service/
│   └── doorbell_service.py  # Background audio service
├── classifier/
│   └── yamnet.py        # YAMNet TFLite wrapper
├── assets/
│   ├── yamnet.tflite    # YAMNet model
│   └── yamnet_class_map.csv
├── buildozer.spec       # Build configuration
└── requirements.txt
```

## Local Desktop Testing

Test the classifier before building:

```bash
pip install -r requirements.txt
python test_local.py
```

Play a doorbell sound near your microphone to verify detection.

## Notes

- DOORBELL_IDX = 350 (corrected from 377 in the original spec)
- Uses `tflite-runtime` for lightweight inference
- Foreground service prevents Android from killing the audio process
- OSC (port 3001) communicates between service and UI