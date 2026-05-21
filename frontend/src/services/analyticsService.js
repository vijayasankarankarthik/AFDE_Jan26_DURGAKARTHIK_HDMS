/**
 * analyticsService.js — Axios wrappers for all analytics + upload API endpoints.
 */

import axios from "axios";

const BASE = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

const api = axios.create({ baseURL: BASE });

// ---------------------------------------------------------------------------
// Analytics endpoints
// ---------------------------------------------------------------------------

/** @param {"live"|"reporting"} source */
export const getSummary = (source = "live") =>
  api.get("/analytics/summary", { params: { source } }).then((r) => r.data);

export const getCategoryBreakdown = (source = "live") =>
  api.get("/analytics/by-category", { params: { source } }).then((r) => r.data);

export const getPriorityBreakdown = (source = "live") =>
  api.get("/analytics/by-priority", { params: { source } }).then((r) => r.data);

export const getStatusBreakdown = (source = "live") =>
  api.get("/analytics/by-status", { params: { source } }).then((r) => r.data);

export const getDepartmentBreakdown = (source = "live") =>
  api.get("/analytics/by-department", { params: { source } }).then((r) => r.data);

/** @param {"daily"|"weekly"|"monthly"} granularity */
export const getVolumeTrend = (granularity = "monthly", source = "live") =>
  api
    .get("/analytics/trend", { params: { granularity, source } })
    .then((r) => r.data);

export const getResolutionTime = (source = "live") =>
  api.get("/analytics/resolution-time", { params: { source } }).then((r) => r.data);

export const getTopDepartments = (limit = 10, source = "live") =>
  api
    .get("/analytics/top-departments", { params: { limit, source } })
    .then((r) => r.data);

export const getEtlJobs = (limit = 20) =>
  api.get("/analytics/etl-jobs", { params: { limit } }).then((r) => r.data);

// ---------------------------------------------------------------------------
// Upload endpoint
// ---------------------------------------------------------------------------

/**
 * Upload a CSV file for ETL ingestion.
 * @param {File} file - Browser File object
 * @param {Function} onProgress - optional upload progress callback (0-100)
 */
export const uploadTicketsCsv = (file, onProgress) => {
  const formData = new FormData();
  formData.append("file", file);

  return api
    .post("/upload/tickets-csv", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: onProgress
        ? (e) => onProgress(Math.round((e.loaded * 100) / e.total))
        : undefined,
    })
    .then((r) => r.data);
};
