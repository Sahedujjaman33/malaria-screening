import os
import urllib.request
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.applications.resnet50 import preprocess_input

MODEL = None
MODEL_INPUT_SIZE = (224, 224)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "malaria_resnet50.keras")

MODEL_URL = "https://huggingface.co/Sahedujjaman/malaria-resnet50/resolve/main/malaria_resnet50.keras"

CLASS_LABELS = {0: "Parasitized", 1: "Uninfected"}


def _download_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    tmp_path = MODEL_PATH + ".tmp"

    print("[classification.py] Downloading model from Hugging Face...")
    urllib.request.urlretrieve(MODEL_URL, tmp_path)

    size_mb = os.path.getsize(tmp_path) / (1024 * 1024)
    print(f"[classification.py] Downloaded file size: {size_mb:.2f} MB")
    if size_mb < 10:
        os.remove(tmp_path)
        raise RuntimeError(f"Downloaded file too small ({size_mb:.2f} MB) — download likely failed.")

    os.replace(tmp_path, MODEL_PATH)
    print(f"[classification.py] Download complete and verified.")


def _load_model():
    global MODEL
    if not os.path.exists(MODEL_PATH):
        _download_model()
    else:
        size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
        print(f"[classification.py] Found cached model ({size_mb:.2f} MB) at {MODEL_PATH}")

    MODEL = tf.keras.models.load_model(MODEL_PATH)
    print("[classification.py] Model loaded successfully.")


def predict_rbc(cell_image: np.ndarray) -> dict:
    img = cv2.resize(cell_image, MODEL_INPUT_SIZE)
    img = preprocess_input(img.astype("float32"))
    img = np.expand_dims(img, axis=0)

    pred = MODEL.predict(img, verbose=0)[0]

    p_parasitized = float(pred[0]) if CLASS_LABELS[0] == "Parasitized" else float(pred[1])
    p_uninfected = 1.0 - p_parasitized
    predicted_class = "Parasitized" if p_parasitized >= 0.5 else "Uninfected"

    return {
        "class": predicted_class,
        "parasitized_probability": round(p_parasitized, 4),
        "uninfected_probability": round(p_uninfected, 4),
    }


_load_model()