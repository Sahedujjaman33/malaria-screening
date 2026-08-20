import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

/**
 * Sends the uploaded smear image to the backend /predict endpoint.
 * @param {File} imageFile
 * @returns {Promise<object>} parsed JSON response from the backend
 */
export async function analyzeSmearImage(imageFile) {
  const formData = new FormData();
  formData.append("image", imageFile);

  const response = await axios.post(`${API_BASE_URL}/predict`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
}

/**
 * Builds the full URL for an annotated result image returned by the backend.
 * @param {string} relativeUrl e.g. "/results/annotated_xxx.jpg"
 */
export function resolveResultImageUrl(relativeUrl) {
  return `${API_BASE_URL}${relativeUrl}`;
}

export { API_BASE_URL };
