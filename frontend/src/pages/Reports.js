import React, { useEffect, useState } from "react";
import { getEtlJobs, getSummary, getTopDepartments } from "../services/analyticsService";
import "../styles/Analytics.css";

const STATUS_BADGE = {
  completed: "badge-green",
  failed:    "badge-red",
  running:   "badge-yellow",
};

const Reports = () => {
  const [jobs,        setJobs]        = useState([]);
  const [summary,     setSummary]     = useState(null);
  const [topDepts,    setTopDepts]    = useState([]);
  const [loading,     setLoading]     = useState(true);
  const [error,       setError]       = useState(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [j, s, d] = await Promise.all([
          getEtlJobs(30),
          getSummary("reporting"),
          getTopDepartments(8, "reporting"),
        ]);
        setJobs(j);
        setSummary(s);
        setTopDepts(d.departments || []);
      } catch (err) {
        setError(err.response?.data?.detail || err.message);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const fmt = (iso) => iso ? new Date(iso).toLocaleString() : "—";

  return (
    <div className="analytics-page">
      <div className="analytics-header">
        <div>
          <h1>Reports</h1>
          <p>ETL import history and reporting database summary.</p>
        </div>
      </div>

      {error && <div className="analytics-error">⚠ {error}</div>}

      {/* Reporting DB KPIs */}
      {summary && (
        <section className="reports-section">
          <h2>Reporting Database Summary</h2>
          <div className="kpi-strip">
            <div className="kpi-card"><span className="kpi-value">{summary.total_tickets}</span><span className="kpi-label">Total records</span></div>
            <div className="kpi-card accent-yellow"><span className="kpi-value">{summary.open_tickets}</span><span className="kpi-label">Open</span></div>
            <div className="kpi-card accent-green"><span className="kpi-value">{summary.resolved_tickets}</span><span className="kpi-label">Resolved</span></div>
            <div className="kpi-card accent-purple">
              <span className="kpi-value">{(summary.resolution_rate * 100).toFixed(1)}%</span>
              <span className="kpi-label">Resolution Rate</span>
            </div>
          </div>
        </section>
      )}

      {/* Top departments from reporting DB */}
      {topDepts.length > 0 && (
        <section className="reports-section">
          <h2>Top Departments (Reporting DB)</h2>
          <table className="reports-table">
            <thead>
              <tr>
                <th>Department</th>
                <th>Total</th>
                <th>Open</th>
                <th>High Priority</th>
              </tr>
            </thead>
            <tbody>
              {topDepts.map((d, i) => (
                <tr key={i}>
                  <td>{d.department}</td>
                  <td>{d.ticket_count}</td>
                  <td>{d.open_count}</td>
                  <td>{d.high_priority_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {/* ETL Jobs */}
      <section className="reports-section">
        <h2>ETL Import History</h2>
        {loading ? (
          <p>Loading…</p>
        ) : jobs.length === 0 ? (
          <p className="no-data">No import jobs found. Upload a CSV to get started.</p>
        ) : (
          <table className="reports-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Filename</th>
                <th>Status</th>
                <th>Total</th>
                <th>Inserted</th>
                <th>Duplicates</th>
                <th>Errors</th>
                <th>Started</th>
                <th>Completed</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((j) => (
                <tr key={j.job_id}>
                  <td>{j.job_id}</td>
                  <td className="filename-cell" title={j.filename}>{j.filename}</td>
                  <td>
                    <span className={`badge ${STATUS_BADGE[j.status] || ""}`}>
                      {j.status}
                    </span>
                  </td>
                  <td>{j.total_rows    ?? "—"}</td>
                  <td>{j.inserted_rows ?? "—"}</td>
                  <td>{j.duplicate_rows ?? "—"}</td>
                  <td>{j.error_rows    ?? "—"}</td>
                  <td>{fmt(j.started_at)}</td>
                  <td>{fmt(j.completed_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
};

export default Reports;
