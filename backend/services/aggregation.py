"""
Result Aggregation Module
Owner: MEMBER 3

Takes the list of per-cell predictions and produces a summary
suitable for the final API response.
"""


def aggregate_results(cell_predictions: list) -> dict:
    """
    Args:
        cell_predictions: list of dicts, each like:
            {
                "cell_id": int,
                "class": "Parasitized" | "Uninfected",
                "confidence": float,
                "bbox": [x, y, w, h]
            }

    Returns:
        dict summary with counts, percentage, and overall verdict.
    """
    total = len(cell_predictions)
    parasitized = sum(1 for c in cell_predictions if c["class"] == "Parasitized")
    uninfected = total - parasitized

    percentage = round((parasitized / total) * 100, 2) if total > 0 else 0.0

    # Simple overall verdict: if ANY cell is predicted parasitized, flag it.
    # Adjust this threshold/logic later based on Member 2's model calibration
    # and any clinical guidance you receive.
    overall = "Parasitized" if parasitized > 0 else "Uninfected"

    return {
        "total_cells": total,
        "parasitized_cells": parasitized,
        "uninfected_cells": uninfected,
        "parasitized_percentage": percentage,
        "overall_prediction": overall,
    }
