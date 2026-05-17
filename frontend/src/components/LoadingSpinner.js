/**
 * components/LoadingSpinner.js — Centered loading indicator.
 *
 * Props:
 *   text  {string}  — optional loading message (default "Loading…")
 *   small {boolean} — render a smaller inline spinner
 */

import React from 'react';
import '../styles/components.css';

function LoadingSpinner({ text = 'Loading…', small = false }) {
  if (small) {
    return <span className="spinner spinner-sm" role="status" aria-label="Loading" />;
  }

  return (
    <div className="spinner-overlay" role="status">
      <div className="spinner" />
      <span className="spinner-text">{text}</span>
    </div>
  );
}

export default LoadingSpinner;
