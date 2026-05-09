import numpy as np
import csv
import tflite_runtime.interpreter as tflite


SAMPLE_RATE          = 16_000
PATCH_SAMPLES        = 15_600   # ~0.975 s
DOORBELL_IDX         = 350
CONFIDENCE_THRESHOLD = 0.40


class YamNetClassifier:

    def __init__(self, model_path: str, labels_path: str):
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        self.input_details  = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        with open(labels_path, newline="") as f:
            reader = csv.DictReader(f)
            self.labels = [row["display_name"] for row in reader]

    def predict(self, audio_float32: np.ndarray) -> dict:
        """
        audio_float32: 1-D float32 numpy array of exactly PATCH_SAMPLES values
                       normalized to [-1.0, 1.0].
        Returns a dict with the top class and the doorbell confidence score.
        """
        input_data = audio_float32.reshape(1, PATCH_SAMPLES).astype(np.float32)
        self.interpreter.set_tensor(self.input_details[0]["index"], input_data)
        self.interpreter.invoke()

        scores = self.interpreter.get_tensor(self.output_details[0]["index"])[0]  # (521,)

        doorbell_score = float(scores[DOORBELL_IDX])
        top_idx        = int(np.argmax(scores))

        return {
            "doorbell_score": doorbell_score,
            "top_label":      self.labels[top_idx],
            "top_score":      float(scores[top_idx]),
            "is_doorbell":    doorbell_score >= CONFIDENCE_THRESHOLD,
        }