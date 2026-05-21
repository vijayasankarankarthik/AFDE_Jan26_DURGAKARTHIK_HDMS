import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

/**
 * VolumeTrendChart
 * Props:
 *   data        — array of { period, count, resolved, open }
 *   granularity — "daily" | "weekly" | "monthly" (for axis label formatting)
 */
const VolumeTrendChart = ({ data = [], granularity = "monthly" }) => {
  // Shorten labels for monthly and weekly views
  const formatLabel = (value) => {
    if (!value) return "";
    if (granularity === "monthly") return value.slice(0, 7); // "2024-03"
    return value.slice(5);  // "03-15"
  };

  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="gradTotal" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#6366f1" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#6366f1" stopOpacity={0.02} />
          </linearGradient>
          <linearGradient id="gradResolved" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#10b981" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#10b981" stopOpacity={0.02} />
          </linearGradient>
          <linearGradient id="gradOpen" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#f59e0b" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis
          dataKey="period"
          tickFormatter={formatLabel}
          tick={{ fontSize: 11 }}
          interval="preserveStartEnd"
        />
        <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
        <Tooltip
          contentStyle={{ borderRadius: 8, fontSize: 13 }}
          labelFormatter={(v) => `Period: ${v}`}
        />
        <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
        <Area
          type="monotone"
          dataKey="count"
          name="Total"
          stroke="#6366f1"
          fill="url(#gradTotal)"
          strokeWidth={2}
          dot={false}
        />
        <Area
          type="monotone"
          dataKey="resolved"
          name="Resolved"
          stroke="#10b981"
          fill="url(#gradResolved)"
          strokeWidth={2}
          dot={false}
        />
        <Area
          type="monotone"
          dataKey="open"
          name="Open"
          stroke="#f59e0b"
          fill="url(#gradOpen)"
          strokeWidth={2}
          dot={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
};

export default VolumeTrendChart;
