import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

/**
 * DepartmentBarChart
 * Props:
 *   data — array of { department, total, open_count, resolved_count, resolution_rate }
 */
const DepartmentBarChart = ({ data = [] }) => {
  const chartData = data.map((d) => ({
    name: d.department,
    Total:    d.total,
    Open:     d.open_count,
    Resolved: d.resolved_count,
  }));

  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
        <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} />
        <YAxis type="category" dataKey="name" tick={{ fontSize: 12 }} width={80} />
        <Tooltip
          contentStyle={{ borderRadius: 8, fontSize: 13 }}
        />
        <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
        <Bar dataKey="Total"    fill="#6366f1" radius={[0, 4, 4, 0]} barSize={10} />
        <Bar dataKey="Open"     fill="#f59e0b" radius={[0, 4, 4, 0]} barSize={10} />
        <Bar dataKey="Resolved" fill="#10b981" radius={[0, 4, 4, 0]} barSize={10} />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default DepartmentBarChart;
