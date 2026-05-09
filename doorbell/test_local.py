import pyaudio
import numpy as np
from classifier.yamnet import YamNetClassifier, SAMPLE_RATE, PATCH_SAMPLES

clf = YamNetClassifier("assets/yamnet.tflite", "assets/yamnet_class_map.csv")

pa     = pyaudio.PyAudio()
stream = pa.open(rate=SAMPLE_RATE, channels=1, format=pyaudio.paInt16,
                 input=True, frames_per_buffer=PATCH_SAMPLES)

print("Listening… press Ctrl+C to stop")
while True:
    raw     = stream.read(PATCH_SAMPLES, exception_on_overflow=False)
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    result  = clf.predict(samples)
    print(f"  top={result['top_label']:<30}  doorbell={result['doorbell_score']:.3f}")