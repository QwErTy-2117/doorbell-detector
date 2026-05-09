import sys
import os
import time
import threading
import numpy as np

# Add project root to path so classifier/ is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classifier.yamnet import YamNetClassifier, SAMPLE_RATE, PATCH_SAMPLES

from plyer import notification
from pythonosc import udp_client

OSC_UI_PORT    = 3001   # service → UI (status updates)
COOLDOWN_S     = 10.0   # seconds between repeated doorbell alerts
ROLLING_WINDOW = 3      # number of consecutive inferences to average

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")


def send_notification():
    notification.notify(
        title="Doorbell",
        message="Someone is at the door.",
        ticker="Doorbell detected",
        toast=False,
    )


def audio_loop(classifier: YamNetClassifier, ui_client: udp_client.SimpleUDPClient):
    import pyaudio

    pa     = pyaudio.PyAudio()
    stream = pa.open(
        rate=SAMPLE_RATE,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=PATCH_SAMPLES,
    )

    rolling_scores  = []
    last_alert_time = 0.0

    while True:
        raw = stream.read(PATCH_SAMPLES, exception_on_overflow=False)

        # Convert PCM int16 → float32 normalized to [-1, 1]
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0

        result = classifier.predict(samples)

        # Rolling mean over the last ROLLING_WINDOW inferences
        rolling_scores.append(result["doorbell_score"])
        if len(rolling_scores) > ROLLING_WINDOW:
            rolling_scores.pop(0)
        mean_score = sum(rolling_scores) / len(rolling_scores)

        # Broadcast live status to UI
        ui_client.send_message(
            "/status",
            [result["top_label"], round(result["doorbell_score"], 3), round(mean_score, 3)],
        )

        if result["is_doorbell"] and mean_score >= 0.40:
            now = time.time()
            if now - last_alert_time >= COOLDOWN_S:
                last_alert_time = now
                send_notification()
                ui_client.send_message("/alert", [1])


def main():
    model_path  = os.path.join(ASSETS_DIR, "yamnet.tflite")
    labels_path = os.path.join(ASSETS_DIR, "yamnet_class_map.csv")
    classifier  = YamNetClassifier(model_path, labels_path)

    ui_client = udp_client.SimpleUDPClient("127.0.0.1", OSC_UI_PORT)

    t = threading.Thread(target=audio_loop, args=(classifier, ui_client), daemon=True)
    t.start()

    # Keep the service process alive
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()