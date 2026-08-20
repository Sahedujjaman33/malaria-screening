import React, { useRef } from "react";

export default function ImageUploader({ onImageSelected }) {
  const inputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) onImageSelected(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) onImageSelected(file);
  };

  return (
    <div
      className="uploader-box"
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      onClick={() => inputRef.current.click()}
    >
      <p>Drag & drop a blood smear image here, or click to choose a file</p>
      <p className="uploader-hint">Supported: JPG, JPEG, PNG (max 15MB)</p>
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png"
        style={{ display: "none" }}
        onChange={handleFileChange}
      />
    </div>
  );
}
