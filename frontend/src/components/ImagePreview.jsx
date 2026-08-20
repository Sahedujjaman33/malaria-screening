import React from "react";

export default function ImagePreview({ file, previewUrl, onAnalyze, onRemove }) {
  return (
    <div className="preview-box">
      <img src={previewUrl} alt="Smear preview" className="preview-image" />
      <p className="preview-filename">{file.name}</p>
      <div className="preview-actions">
        <button className="btn btn-primary" onClick={onAnalyze}>
          Analyze Image
        </button>
        <button className="btn btn-secondary" onClick={onRemove}>
          Remove
        </button>
      </div>
    </div>
  );
}
