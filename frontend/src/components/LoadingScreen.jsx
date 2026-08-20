import React from "react";

export default function LoadingScreen() {
  return (
    <div className="loading-box">
      <div className="spinner" />
      <p>Analyzing blood smear...</p>
      <ul className="loading-steps">
        <li>Image uploaded</li>
        <li>Preprocessing image</li>
        <li>Detecting red blood cells</li>
        <li>Classifying cells</li>
        <li>Generating results</li>
      </ul>
    </div>
  );
}
