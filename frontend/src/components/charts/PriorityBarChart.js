import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ResponsiveContainer,
} from "recharts";

const PRIORITY_COLORS = {
  Critical: "#ef4444",
  High:     "#f97316",
  Medium:   "#f59e0b",
  Low:      "#10b981",
};

/**
 * PriorityBarChart
 * Props:
 *   data — array of { priority, count, percentage }
 */
const PriorityBarChart = ({ data = [] }) => {
  const chartData = data.map((d) => ({ name: d.priority, count: d.count }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="name" tick={{ fontSize: 13 }} />
        <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
        <Tooltip
          contentStyle={{ borderRadius: 8, fontSize: 13 }}
          formatter={(value) => [value, "Tickets"]}
        />
        <Bar dataKey="count" radius={[6, 6, 0, 0]}>
          {chartData.map((entry, idx) => (
            <Cell
              key={idx}
              fill={PRIORITY_COLORS[entry.name] || "#6366f1"}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

export default PriorityBarChart;
