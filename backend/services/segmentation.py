"""
RBC Detection & Segmentation Module
"""

import cv2
import numpy as np


def segment_smear(image: np.ndarray, min_cell_area=400, max_cell_area=8000,
                   black_threshold=25, reference_scale=0.3, max_dimension=1800) -> list:
    original_image = image          # ⭐ crop ও bbox শেষে এই original থেকেই নেওয়া হবে
    orig_h, orig_w = original_image.shape[:2]

    # ---- Processing-এর জন্য ছোট করা (শুধু গণনা দ্রুত করতে, coordinate পরে স্কেল-ব্যাক হবে) ----
    working_image = original_image
    downscale_factor = 1.0
    if max(orig_h, orig_w) > max_dimension:
        downscale_factor = max_dimension / max(orig_h, orig_w)
        working_image = cv2.resize(original_image, None, fx=downscale_factor, fy=downscale_factor)

    h_img, w_img = working_image.shape[:2]

    reference_width = 5312 * reference_scale
    current_scale_factor = w_img / reference_width
    adj_min_area = min_cell_area * (current_scale_factor ** 2)
    adj_max_area = max_cell_area * (current_scale_factor ** 2)

    erosion_size = max(3, int(15 * current_scale_factor))
    if erosion_size % 2 == 0:
        erosion_size += 1

    # ---- ধাপ 1: বৈধ region mask ----
    gray = cv2.cvtColor(working_image, cv2.COLOR_RGB2GRAY)
    valid_mask = (gray > black_threshold).astype(np.uint8) * 255
    erosion_kernel = np.ones((erosion_size, erosion_size), np.uint8)
    valid_mask = cv2.erode(valid_mask, erosion_kernel, iterations=1)

    # ---- ধাপ 2: Saturation + Otsu ----
    hsv = cv2.cvtColor(working_image, cv2.COLOR_RGB2HSV)
    saturation = hsv[:, :, 1]
    saturation_blurred = cv2.GaussianBlur(saturation, (5, 5), 0)

    valid_pixels = saturation_blurred[valid_mask > 0].reshape(-1, 1)
    if len(valid_pixels) == 0:
        return []

    otsu_val, _ = cv2.threshold(valid_pixels, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, thresh = cv2.threshold(saturation_blurred, otsu_val, 255, cv2.THRESH_BINARY_INV)
    thresh = cv2.bitwise_and(thresh, thresh, mask=valid_mask)

    # ---- ধাপ 3: Morphological cleanup ----
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=2)

    # ---- ধাপ 4: Watershed ----
    dist_transform = cv2.distanceTransform(cleaned, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist_transform, 0.35 * dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)

    sure_bg = cv2.dilate(cleaned, kernel, iterations=3)
    unknown = cv2.subtract(sure_bg, sure_fg)

    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    working_bgr = cv2.cvtColor(working_image, cv2.COLOR_RGB2BGR)
    markers = cv2.watershed(working_bgr, markers)

    # ---- ধাপ 5: bounding box বের করে original resolution-এ স্কেল-ব্যাক করা ----
    results = []
    cell_id = 1
    valid_mask_bool = (valid_mask > 0).astype(np.uint8)
    inverse_scale = 1.0 / downscale_factor   # ⭐ original-এ ফিরিয়ে আনার factor

    for marker_id in np.unique(markers):
        if marker_id <= 1:
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
        x, y, w, h = cv2.boundingRect(contours[0])

        aspect_ratio = w / max(h, 1)
        if aspect_ratio < 0.5 or aspect_ratio > 1.8:
            continue

        # ⭐ এই coordinate গুলো (এখনো working_image scale-এ) original scale-এ রূপান্তর করা
        x_o = x * inverse_scale
        y_o = y * inverse_scale
        w_o = w * inverse_scale
        h_o = h * inverse_scale

        pad = max(2, int(3 * current_scale_factor * inverse_scale))
        x1 = max(0, int(x_o - pad))
        y1 = max(0, int(y_o - pad))
        x2 = min(orig_w, int(x_o + w_o + pad))
        y2 = min(orig_h, int(y_o + h_o + pad))

        # ⭐ crop এখন ORIGINAL full-resolution image থেকে নেওয়া হচ্ছে — ভালো মানের crop
        crop = original_image[y1:y2, x1:x2]

        results.append({
            "cell_id": cell_id,
            "image": crop,
            "bbox": [int(x1), int(y1), int(x2 - x1), int(y2 - y1)],
            "center": [int((x1 + x2) / 2), int((y1 + y2) / 2)],
        })
        cell_id += 1

    return results