"""
RBC Detection & Segmentation Module
Owner: MEMBER 1

Interface contract (DO NOT change the function name/signature without
team agreement - see docs/interface_contract.md):

    segment_smear(image: np.ndarray) -> list[dict]

Each returned dict must have exactly these keys:
    {
        "cell_id": int,
        "image": np.ndarray,       # cropped single-cell RGB image, uint8
        "bbox": [x, y, w, h],      # coordinates in the ORIGINAL image
        "center": [cx, cy]
    }

------------------------------------------------------------------
THIS IS A DUMMY IMPLEMENTATION.
Member 1 should replace the body of segment_smear() with the real
LoG / Hough Circle / Watershed based detection + segmentation logic,
while keeping the function name and return format identical.
------------------------------------------------------------------
"""

import numpy as np


def segment_smear(image: np.ndarray) -> list:
    """
    DUMMY VERSION - returns a fixed grid of fake "cells" cropped from the
    uploaded image, purely so the rest of the pipeline (classification,
    aggregation, visualization, API) can be built and tested before the
    real segmentation algorithm is ready.

    Replace this function body with real RBC detection/segmentation.
    """
    h, w = image.shape[0], image.shape[1]

    # Create a fake 4x4 grid of "detected cells" for demo/testing purposes
    grid_size = 4
    cell_w = w // grid_size
    cell_h = h // grid_size

    results = []
    cell_id = 1
    for row in range(grid_size):
        for col in range(grid_size):
            x = col * cell_w
            y = row * cell_h
            cw = min(cell_w, w - x)
            ch = min(cell_h, h - y)

            crop = image[y:y + ch, x:x + cw]

            results.append({
                "cell_id": cell_id,
                "image": crop,
                "bbox": [int(x), int(y), int(cw), int(ch)],
                "center": [int(x + cw / 2), int(y + ch / 2)],
            })
            cell_id += 1

    return results
