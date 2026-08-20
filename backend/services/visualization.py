"""
Visualization Module
Owner: MEMBER 3

Draws prediction results (bounding boxes + labels) on top of the
original uploaded smear image, so the user can see what the system
analyzed.

Green box  -> Uninfected
Red box    -> Parasitized
"""

import os
import uuid
import cv2
import numpy as np

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)


def draw_annotations(image: np.ndarray, cell_predictions: list) -> str:
    """
    Args:
        image: original RGB image (np.ndarray)
        cell_predictions: list of dicts with keys "bbox" and "class"

    Returns:
        The filename (not full path) of the saved annotated image,
        saved inside RESULTS_DIR. The API will expose it at
        /results/<filename>.
    """
    annotated = image.copy()

    # cv2 drawing functions expect BGR; convert for correct color rendering
    annotated_bgr = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)

    for cell in cell_predictions:
        x, y, w, h = cell["bbox"]
        color = (0, 0, 255) if cell["class"] == "Parasitized" else (0, 200, 0)  # BGR
        cv2.rectangle(annotated_bgr, (x, y), (x + w, y + h), color, 2)
        cv2.putText(
            annotated_bgr,
            str(cell["cell_id"]),
            (x, max(y - 5, 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            color,
            1,
            cv2.LINE_AA,
        )

    filename = f"annotated_{uuid.uuid4().hex[:10]}.jpg"
    filepath = os.path.join(RESULTS_DIR, filename)
    cv2.imwrite(filepath, annotated_bgr)

    return filename
