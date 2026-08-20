"""
CNN Classification Module
Owner: MEMBER 2

Interface contract (DO NOT change the function name/signature without
team agreement - see docs/interface_contract.md):

    predict_rbc(cell_image: np.ndarray) -> dict

Return format:
    {
        "class": "Parasitized" | "Uninfected",
        "parasitized_probability": float,   # 0.0 - 1.0
        "uninfected_probability": float,    # 0.0 - 1.0, sums to 1.0
    }

------------------------------------------------------------------
THIS IS A DUMMY IMPLEMENTATION.
Member 2 should replace the body with the real trained CNN
(e.g. ResNet-50 transfer-learning model) inference logic:

    1. Load the trained model ONCE at module import time (see
       `_load_model()` below) - never reload per-request.
    2. Inside predict_rbc(): resize + normalize the incoming image
       EXACTLY as done during training, then run model.predict().
    3. Keep the function name, input, and output format identical
       so Member 3's backend does not need to change.
------------------------------------------------------------------
"""

import random
import numpy as np

MODEL = None  # will hold the loaded Keras/PyTorch model
MODEL_INPUT_SIZE = (224, 224)  # <-- Member 2: set this to your real model's input size


def _load_model():
    """
    Loads the trained model once when this module is first imported.

    Example real implementation (uncomment and adapt once model is ready):

        import tensorflow as tf
        global MODEL
        MODEL = tf.keras.models.load_model("models/malaria_resnet50.keras")
    """
    global MODEL
    MODEL = None  # dummy: no real model loaded yet
    print("[classification.py] Using DUMMY classifier - no real model loaded.")


def predict_rbc(cell_image: np.ndarray) -> dict:
    """
    DUMMY VERSION - returns a random prediction so the rest of the
    pipeline can be developed and tested before the real trained
    model is available.

    Replace the body of this function with real preprocessing +
    model.predict() logic once Member 2's model is ready.
    """
    if MODEL is None:
        # ---- DUMMY LOGIC (remove once real model is integrated) ----
        p_parasitized = round(random.random(), 4)
    else:
        # ---- REAL MODEL LOGIC (Member 2 fills this in) ----
        # img = cv2.resize(cell_image, MODEL_INPUT_SIZE)
        # img = img.astype("float32") / 255.0
        # img = np.expand_dims(img, axis=0)
        # pred = MODEL.predict(img)[0]
        # p_parasitized = float(pred[0])   # adjust index to match your label order
        p_parasitized = round(random.random(), 4)  # placeholder until wired up

    p_uninfected = round(1.0 - p_parasitized, 4)
    predicted_class = "Parasitized" if p_parasitized >= 0.5 else "Uninfected"

    return {
        "class": predicted_class,
        "parasitized_probability": p_parasitized,
        "uninfected_probability": p_uninfected,
    }


# Load model as soon as this module is imported (not on every request)
_load_model()
