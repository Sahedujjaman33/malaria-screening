import React, { useState } from "react";

export default function CellTable({ cellResults }) {
  const [visible, setVisible] = useState(false);

  return (
    <div className="cell-table-wrapper">
      <button className="btn btn-link" onClick={() => setVisible(!visible)}>
        {visible ? "Hide" : "View"} Cell-Level Predictions
      </button>

      {visible && (
        <table className="cell-table">
          <thead>
            <tr>
              <th>Cell ID</th>
              <th>Prediction</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {cellResults.map((cell) => (
              <tr key={cell.cell_id}>
                <td>{String(cell.cell_id).padStart(3, "0")}</td>
                <td className={cell.class === "Parasitized" ? "cell-positive" : "cell-negative"}>
                  {cell.class}
                </td>
                <td>{Math.round(cell.confidence * 100)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
