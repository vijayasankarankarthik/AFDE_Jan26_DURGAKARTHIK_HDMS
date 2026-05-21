import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

/**
 * ResolutionTimeChart — horizontal bar chart of avg resolution days per category.
 * Props:
 *   data — array of { category, avg_days, min_days, max_days, sample_count }
 */
const ResolutionTimeChart = ({ data = [] }) => {
  const COLORS = [
    "#6366f1", "#f59e0b", "#10b981", "#ef4444",
    "#3b82f6", "#8b5cf6", "#f97316", "#14b8a6",
    "#ec4899",
  ];

  const chartData = [...data]
    .sort((a, b) => b.avg_days - a.avg_days)
    .map((d) => ({
      name:     d.category,
      avg_days: d.avg_days,
      samples:  d.sample_count,
    }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
        <XAxis
          type="number"
          dataKey="avg_days"
          tick={{ fontSize: 12 }}
          label={{ value: "Avg. days", position: "insideBottomRight", offset: -5, fontSize: 11 }}
        />
        <YAxis type="category" dataKey="name" tick={{ fontSize: 12 }} width={100} />
        <Tooltip
          contentStyle={{ borderRadius: 8, fontSize: 13 }}
          formatter={(value, name, props) => [
            `${value} days (n=${props.payload.samples})`,
            "Avg. resolution",
          ]}
        />
        <Bar dataKey="avg_days" radius={[0, 6, 6, 0]} barSize={14}>
          {chartData.map((_, idx) => (
            <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

export default ResolutionTimeChart;
