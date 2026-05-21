import React, { useState, useRef } from "react";
import { uploadTicketsCsv } from "../services/analyticsService";
import "../styles/Upload.css";

const STATUS_ICONS = { completed: "✅", failed: "❌", running: "⏳" };

const UploadCSV = () => {
  const [file,       setFile]       = useState(null);
  const [dragging,   setDragging]   = useState(false);
  const [uploading,  setUploading]  = useState(false);
  const [progress,   setProgress]   = useState(0);
  const [result,     setResult]     = useState(null);
  const [error,      setError]      = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (selected) => {
    if (!selected) return;
    if (!selected.name.match(/\.(csv|txt)$/i)) {
      setError("Only CSV or TXT files are accepted.");
      return;
    }
    setFile(selected);
    setResult(null);
    setError(null);
    setProgress(0);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFileSelect(e.dataTransfer.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setError(null);
    setResult(null);
    setProgress(0);

    try {
      const job = await uploadTicketsCsv(file, setProgress);
      setResult(job);
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (detail && typeof detail === "object") {
        setError(detail.error_message || detail.message || "Upload failed.");
      } else {
        setError(String(detail || err.message));
      }
    } finally {
      setUploading(false);
    }
  };

  const clearSelection = () => {
    setFile(null);
    setResult(null);
    setError(null);
    setProgress(0);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="upload-page">
      <div className="upload-header">
        <h1>Import Tickets via CSV</h1>
        <p>Upload a historical ticket CSV file to import data into the reporting database.</p>
      </div>

      {/* Format guide */}
      <div className="upload-guide">
        <h3>Required columns</h3>
        <div className="columns-grid">
          {["employee_name","department","issue_category","description","priority","status","created_at"].map((c) => (
            <code key={c}>{c}</code>
          ))}
        </div>
        <p className="guide-note">
          Optional: <code>updated_at</code>, <code>resolution_notes</code>.<br />
          Accepted priority values: <em>Low, Medium, High, Critical</em>.<br />
          Accepted status values: <em>Open, In Progress, Resolved, Closed</em>.
        </p>
      </div>

      {/* Drop zone */}
      <form onSubmit={handleSubmit}>
        <div
          className={`drop-zone ${dragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.txt"
            style={{ display: "none" }}
            onChange={(e) => handleFileSelect(e.target.files[0])}
          />
          {file ? (
            <div className="file-info">
              <span className="file-icon">📄</span>
              <div>
                <strong>{file.name}</strong>
                <span>{(file.size / 1024).toFixed(1)} KB</span>
              </div>
              <button
                type="button"
                className="btn-clear"
                onClick={(e) => { e.stopPropagation(); clearSelection(); }}
              >✕</button>
            </div>
          ) : (
            <>
              <span className="drop-icon">⬆</span>
              <p>Drag &amp; drop a CSV file here, or <span className="link-text">browse</span></p>
              <span className="drop-hint">Max file size: 50 MB</span>
            </>
          )}
        </div>

        {/* Progress bar */}
        {uploading && (
          <div className="progress-wrap">
            <div className="progress-bar" style={{ width: `${progress}%` }} />
            <span>{progress}%</span>
          </div>
        )}

        <button
          type="submit"
          className="btn-upload"
          disabled={!file || uploading}
        >
          {uploading ? "Uploading…" : "Upload & Import"}
        </button>
      </form>

      {/* Result */}
      {result && (
        <div className={`upload-result status-${result.status}`}>
          <h3>{STATUS_ICONS[result.status]} Import {result.status}</h3>
          <div className="result-stats">
            <div><span>Total rows</span><strong>{result.total_rows ?? "—"}</strong></div>
            <div><span>Inserted</span>  <strong>{result.inserted_rows ?? "—"}</strong></div>
            <div><span>Duplicates</span><strong>{result.duplicate_rows ?? "—"}</strong></div>
            <div><span>Errors</span>    <strong>{result.error_rows ?? "—"}</strong></div>
          </div>
          {result.error_message && (
            <p className="result-error">{result.error_message}</p>
          )}
          <p className="result-meta">Batch ID: <code>{result.batch_id}</code></p>
        </div>
      )}

      {error && (
        <div className="upload-result status-failed">
          <h3>❌ Upload failed</h3>
          <p>{error}</p>
        </div>
      )}
    </div>
  );
};

export default UploadCSV;
