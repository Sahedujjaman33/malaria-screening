import React, { useState } from "react";
import ImageUploader from "../components/ImageUploader";
import ImagePreview from "../components/ImagePreview";
import LoadingScreen from "../components/LoadingScreen";
import ResultCard from "../components/ResultCard";
import CellTable from "../components/CellTable";
import { analyzeSmearImage } from "../services/api";

const STAGES = {
  UPLOAD: "upload",
  PREVIEW: "preview",
  LOADING: "loading",
  RESULT: "result",
  ERROR: "error",
};

export default function Home() {
  const [stage, setStage] = useState(STAGES.UPLOAD);
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  const handleImageSelected = (selectedFile) => {
    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
    setStage(STAGES.PREVIEW);
  };

  const handleAnalyze = async () => {
    setStage(STAGES.LOADING);
    try {
      const data = await analyzeSmearImage(file);
      if (data.status === "error") {
        setErrorMessage(data.message || "Something went wrong.");
        setStage(STAGES.ERROR);
        return;
      }
      setResult(data);
      setStage(STAGES.RESULT);
    } catch (err) {
      setErrorMessage(
        err.response?.data?.message ||
          "Unable to reach the analysis service. Please try again."
      );
      setStage(STAGES.ERROR);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setErrorMessage("");
    setStage(STAGES.UPLOAD);
  };

  return (
    <div className="page">
      <header className="page-header">
        <h1>Malaria Parasite Screening</h1>
        <p>Upload a thin blood-smear image for automated RBC analysis</p>
      </header>

      <main className="page-body">
        {stage === STAGES.UPLOAD && (
          <ImageUploader onImageSelected={handleImageSelected} />
        )}

        {stage === STAGES.PREVIEW && (
          <ImagePreview
            file={file}
            previewUrl={previewUrl}
            onAnalyze={handleAnalyze}
            onRemove={handleReset}
          />
        )}

        {stage === STAGES.LOADING && <LoadingScreen />}

        {stage === STAGES.RESULT && result && (
          <>
            <ResultCard result={result} onReset={handleReset} />
            <CellTable cellResults={result.cell_results} />
          </>
        )}

        {stage === STAGES.ERROR && (
          <div className="error-box">
            <p>{errorMessage}</p>
            <button className="btn btn-primary" onClick={handleReset}>
              Try Again
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
