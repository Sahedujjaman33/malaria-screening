"""
Prediction Route
Owner: MEMBER 3

Defines POST /predict - the single main endpoint that runs the full
pipeline: validate -> segment -> classify -> aggregate -> visualize.
"""

import io
import numpy as np
from PIL import Image, UnidentifiedImageError
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from services.segmentation import segment_smear
from services.classification import predict_rbc
from services.aggregation import aggregate_results
from services.visualization import draw_annotations

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png"}
MAX_FILE_SIZE_MB = 15


def error_response(error_code: str, message: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "error_code": error_code, "message": message},
    )


@router.post("/predict")
async def predict(image: UploadFile = File(...)):
    # ---- 1. Validate file type ----
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        return error_response(
            "INVALID_FILE",
            "Please upload a valid JPG/PNG image.",
        )

    raw_bytes = await image.read()

    # ---- 2. Validate file size ----
    size_mb = len(raw_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return error_response(
            "FILE_TOO_LARGE",
            f"Image exceeds the {MAX_FILE_SIZE_MB}MB limit.",
        )

    # ---- 3. Validate that it's actually a readable image ----
    try:
        pil_image = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    except UnidentifiedImageError:
        return error_response(
            "INVALID_FILE",
            "The uploaded file could not be read as an image.",
        )

    np_image = np.array(pil_image)  # RGB, uint8

    # ---- 4. Run segmentation (Member 1's module) ----
    try:
        detected_cells = segment_smear(np_image)
    except Exception as e:
        return error_response(
            "PROCESSING_FAILED",
            f"Segmentation failed: {str(e)}",
            status_code=500,
        )

    if len(detected_cells) == 0:
        return error_response(
            "NO_CELLS_DETECTED",
            "No suitable RBCs were detected. Please upload a clear blood-smear image.",
        )

    # ---- 5. Run classification on every detected cell (Member 2's module) ----
    cell_results = []
    for cell in detected_cells:
        try:
            prediction = predict_rbc(cell["image"])
        except Exception as e:
            return error_response(
                "PROCESSING_FAILED",
                f"Classification failed on cell {cell['cell_id']}: {str(e)}",
                status_code=500,
            )

        confidence = max(
            prediction["parasitized_probability"],
            prediction["uninfected_probability"],
        )

        cell_results.append({
            "cell_id": cell["cell_id"],
            "class": prediction["class"],
            "confidence": round(confidence, 4),
            "bbox": cell["bbox"],
        })

    # ---- 6. Aggregate results ----
    summary = aggregate_results(cell_results)

    # ---- 7. Generate annotated image ----
    annotated_filename = draw_annotations(np_image, cell_results)

    # ---- 8. Build final response ----
    return {
        "status": "success",
        **summary,
        "annotated_image_url": f"/results/{annotated_filename}",
        "cell_results": cell_results,
    }
