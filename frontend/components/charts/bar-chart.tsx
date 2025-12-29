// components/charts/bar-chart.tsx
"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const data = [
  { name: "Jan", leads: 400 },
  { name: "Feb", leads: 300 },
  { name: "Mar", leads: 600 },
  { name: "Apr", leads: 800 },
  { name: "May", leads: 500 },
  { name: "Jun", leads: 700 },
];

export function SimpleBarChart() {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="leads" fill="#8884d8" />
      </BarChart>
    </ResponsiveContainer>
  );
}
