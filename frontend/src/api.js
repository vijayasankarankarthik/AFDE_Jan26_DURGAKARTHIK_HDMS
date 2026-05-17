/**
 * api.js — Axios instance with centralised configuration.
 *
 * - Base URL reads from the REACT_APP_API_URL environment variable,
 *   falling back to an empty string so that the CRA proxy in package.json
 *   transparently forwards /api/* requests to http://localhost:8000.
 * - Request interceptor attaches the Content-Type header.
 * - Response interceptor normalises errors into a consistent shape.
 */

import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─── Request interceptor ──────────────────────────────────────────────────────
api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

// ─── Response interceptor ─────────────────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred.';

    // Re-attach a normalised message so consumers can use error.message
    error.message = Array.isArray(message)
      ? message.map((e) => e.msg || JSON.stringify(e)).join(' | ')
      : message;

    return Promise.reject(error);
  }
);

export default api;
