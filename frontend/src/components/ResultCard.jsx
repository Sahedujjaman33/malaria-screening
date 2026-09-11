import React from "react";
import { resolveResultImageUrl } from "../services/api";

export default function ResultCard({ result, onReset }) {
  const {
    overall_prediction,
    total_cells,
    parasitized_cells,
    uninfected_cells,
    parasitized_percentage,
    annotated_image_url,
  } = result;

  const isParasitized = overall_prediction === "Parasitized";

  return (
    <div className="result-card">
      <h2 className={isParasitized ? "verdict-positive" : "verdict-negative"}>
        {isParasitized ? "Parasitized RBC Detected" : "No Parasites Detected"}
      </h2>
      <h2 className={isParasitized ? "verdict-positive" : "verdict-negative"} > {isParasitized ? `Parasitized RBC Detected (${result.parasitized_percentage}% of ${result.total_cells} cells)`: "No Parasites Detected"}
      </h2>
      <div className="stats-grid">
        <div className="stat">
          <span className="stat-value">{total_cells}</span>
          <span className="stat-label">RBCs analyzed</span>
        </div>
        <div className="stat">
          <span className="stat-value">{parasitized_cells}</span>
          <span className="stat-label">Parasitized</span>
        </div>
        <div className="stat">
          <span className="stat-value">{uninfected_cells}</span>
          <span className="stat-label">Uninfected</span>
        </div>
        <div className="stat">
          <span className="stat-value">{parasitized_percentage}%</span>
          <span className="stat-label">Parasitized ratio</span>
        </div>
      </div>

      {annotated_image_url && (
        <img
          src={resolveResultImageUrl(annotated_image_url)}
          alt="Annotated smear"
          className="annotated-image"
        />
      )}

      <p className="disclaimer">
        AI-assisted screening result — not a substitute for professional
        medical diagnosis.
      </p>

      <button className="btn btn-primary" onClick={onReset}>
        Analyze Another Image
      </button>
    </div>
  );
}
