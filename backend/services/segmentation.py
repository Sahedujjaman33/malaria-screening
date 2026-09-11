import cv2
import numpy as np


def segment_smear(
    image: np.ndarray,
    min_cell_area: int = 400,
    max_cell_area: int = 8000,
    black_threshold: int = 25,
    reference_scale: float = 0.3,
    max_dimension: int = 1800,
) -> list:
    original_h, original_w = image.shape[:2]

    # ---- 0. Downscale very large uploads for speed on free-tier hosting ----
    resize_back_scale = 1.0
    if max(original_h, original_w) > max_dimension:
        resize_back_scale = max_dimension / max(original_h, original_w)
        image = cv2.resize(image, None, fx=resize_back_scale, fy=resize_back_scale)

    h_img, w_img = image.shape[:2]

    # Thresholds were tuned at scale=0.3 of a 5312px-wide reference image;
    # rescale them to whatever resolution we're actually processing at.
    reference_width = 5312 * reference_scale
    current_scale_factor = w_img / reference_width

    adj_min_area = min_cell_area * (current_scale_factor ** 2)
    adj_max_area = max_cell_area * (current_scale_factor ** 2)

    erosion_size = max(3, int(15 * current_scale_factor))
    if erosion_size % 2 == 0:
        erosion_size += 1

    # ---- 1. Non-black "valid region" mask ----
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    valid_mask = (gray > black_threshold).astype(np.uint8) * 255
    erosion_kernel = np.ones((erosion_size, erosion_size), np.uint8)
    valid_mask = cv2.erode(valid_mask, erosion_kernel, iterations=1)

    # ---- 2. Green Channel + Adaptive Thresholding ----
    # In an RGB image, the Green channel is located at index 1
    green_channel = image[:, :, 1]
    green_blurred = cv2.GaussianBlur(green_channel, (5, 5), 0)

    # Ensure there is a valid field of view before proceeding
    if cv2.countNonZero(valid_mask) == 0:
        return []

    # Calculate a dynamic block size for adaptive thresholding based on image scale.
    # It must be an odd number.
    block_size = int(101 * current_scale_factor)
    if block_size % 2 == 0:
        block_size += 1
    block_size = max(11, block_size) # Ensure a minimum safe block size

    # Apply Adaptive Thresholding
    # THRESH_BINARY_INV turns the dark cells WHITE (255) and light background BLACK (0)
    thresh = cv2.adaptiveThreshold(
        green_blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        block_size,
        5  # C-constant: subtracts from the local mean to tune sensitivity
    )

    # Mask out any noise detected in the black area outside the microscope lens
    thresh = cv2.bitwise_and(thresh, thresh, mask=valid_mask)

    # ---- 3. Morphological cleanup ----
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=2)

    # ---- 4. Watershed to split touching cells ----
    dist_transform = cv2.distanceTransform(cleaned, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist_transform, 0.35 * dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)

    sure_bg = cv2.dilate(cleaned, kernel, iterations=3)
    unknown = cv2.subtract(sure_bg, sure_fg)

    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    markers = cv2.watershed(image_bgr, markers)

    # ---- 5. Per-blob filtering + crop ----
    results = []
    cell_id = 1
    valid_mask_bool = (valid_mask > 0).astype(np.uint8)

    for marker_id in np.unique(markers):
        if marker_id <= 1:  # background / watershed boundary
            continue

        mask = np.uint8(markers == marker_id)
        area = cv2.countNonZero(mask)
        if area < adj_min_area or area > adj_max_area:
            continue

        overlap = cv2.bitwise_and(mask, mask, mask=valid_mask_bool)
        if cv2.countNonZero(overlap) < 0.75 * area:
            continue

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue

        contour = contours[0]
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / max(h, 1)
        if aspect_ratio < 0.5 or aspect_ratio > 1.8:
            continue

        # ---- Reject merged/irregular blobs (watershed under-segmentation) ----
        # A single RBC is roughly circular. When 2-4 touching cells (or a
        # cell + a chunk of the FOV boundary) survive as ONE watershed
        # marker, the blob is much less circular and/or much less "solid"
        # (has concave dents) than a real cell. Catching that here stops
        # those giant, multi-cell crops from ever reaching the classifier.
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * area / (perimeter ** 2)

        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0

        if circularity < 0.65 or solidity < 0.85:
            continue

        pad = max(2, int(3 * current_scale_factor))
        x1, y1 = max(0, x - pad), max(0, y - pad)
        x2, y2 = min(w_img, x + w + pad), min(h_img, y + h + pad)
        crop = image[y1:y2, x1:x2]

        # Map bbox back to ORIGINAL (pre-downscale) image coordinates,
        # since the API/annotation layer draws on the original upload.
        inv_scale = 1.0 / resize_back_scale
        ox1, oy1 = int(x1 * inv_scale), int(y1 * inv_scale)
        ow, oh = int((x2 - x1) * inv_scale), int((y2 - y1) * inv_scale)

        results.append({
            "cell_id": cell_id,
            "image": crop,
            "bbox": [ox1, oy1, ow, oh],
            "center": [int(ox1 + ow / 2), int(oy1 + oh / 2)],
        })
        cell_id += 1

    return results