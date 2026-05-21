import React, { useEffect, useState, useCallback } from "react";
import {
  getSummary,
  getCategoryBreakdown,
  getPriorityBreakdown,
  getDepartmentBreakdown,
  getVolumeTrend,
  getResolutionTime,
} from "../services/analyticsService";
import CategoryPieChart    from "../components/charts/CategoryPieChart";
import PriorityBarChart    from "../components/charts/PriorityBarChart";
import VolumeTrendChart    from "../components/charts/VolumeTrendChart";
import DepartmentBarChart  from "../components/charts/DepartmentBarChart";
import ResolutionTimeChart from "../components/charts/ResolutionTimeChart";
import "../styles/Analytics.css";

const KPI = ({ label, value, sub, accent }) => (
  <div className={`kpi-card ${accent || ""}`}>
    <span className="kpi-value">{value ?? "—"}</span>
    <span className="kpi-label">{label}</span>
    {sub && <span className="kpi-sub">{sub}</span>}
  </div>
);

const Analytics = () => {
  const [source,      setSource]      = useState("live");
  const [granularity, setGranularity] = useState("monthly");
  const [loading,     setLoading]     = useState(true);
  const [error,       setError]       = useState(null);

  const [summary,     setSummary]     = useState(null);
  const [categories,  setCategories]  = useState([]);
  const [priorities,  setPriorities]  = useState([]);
  const [departments, setDepartments] = useState([]);
  const [trend,       setTrend]       = useState({ data: [] });
  const [resTimes,    setResTimes]    = useState({ by_category: [] });

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [sum, cat, pri, dep, vol, res] = await Promise.all([
        getSummary(source),
        getCategoryBreakdown(source),
        getPriorityBreakdown(source),
        getDepartmentBreakdown(source),
        getVolumeTrend(granularity, source),
        getResolutionTime(source),
      ]);
      setSummary(sum);
      setCategories(cat.categories || []);
      setPriorities(pri.priorities || []);
      setDepartments(dep.departments || []);
      setTrend(vol);
      setResTimes(res);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, [source, granularity]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  return (
    <div className="analytics-page">
      {/* Header */}
      <div className="analytics-header">
        <div>
          <h1>Analytics Dashboard</h1>
          <p>Aggregated insights across all helpdesk tickets.</p>
        </div>
        <div className="analytics-controls">
          <label>Data source
            <select value={source} onChange={(e) => setSource(e.target.value)}>
              <option value="live">Live tickets</option>
              <option value="reporting">Reporting DB</option>
            </select>
          </label>
          <label>Trend granularity
            <select value={granularity} onChange={(e) => setGranularity(e.target.value)}>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </label>
          <button className="btn-refresh" onClick={fetchAll} disabled={loading}>
            {loading ? "Loading…" : "↻ Refresh"}
          </button>
        </div>
      </div>

      {error && <div className="analytics-error">⚠ {error}</div>}

      {/* KPI strip */}
      {summary && (
        <div className="kpi-strip">
          <KPI label="Total Tickets"      value={summary.total_tickets} />
          <KPI label="Open"               value={summary.open_tickets}       accent="accent-yellow" />
          <KPI label="In Progress"        value={summary.in_progress_tickets} accent="accent-blue" />
          <KPI label="Resolved"           value={summary.resolved_tickets}   accent="accent-green" />
          <KPI label="Resolution Rate"
               value={`${(summary.resolution_rate * 100).toFixed(1)}%`}
               accent="accent-purple" />
          <KPI label="Avg. Resolution"
               value={summary.avg_resolution_days != null
                 ? `${summary.avg_resolution_days}d`
                 : "N/A"}
               sub="days to resolve" />
        </div>
      )}

      {/* Charts grid */}
      {loading ? (
        <div className="analytics-loading">Loading charts…</div>
      ) : (
        <div className="charts-grid">
          <div className="chart-card">
            <h3>Tickets by Category</h3>
            <CategoryPieChart data={categories} />
          </div>

          <div className="chart-card">
            <h3>Tickets by Priority</h3>
            <PriorityBarChart data={priorities} />
          </div>

          <div className="chart-card chart-wide">
            <h3>Ticket Volume Over Time</h3>
            <VolumeTrendChart data={trend.data} granularity={trend.granularity} />
          </div>

          <div className="chart-card chart-wide">
            <h3>Tickets by Department</h3>
            <DepartmentBarChart data={departments} />
          </div>

          <div className="chart-card chart-wide">
            <h3>Average Resolution Time by Category (days)</h3>
            <ResolutionTimeChart data={resTimes.by_category} />
          </div>
        </div>
      )}
    </div>
  );
};

export default Analytics;
