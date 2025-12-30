"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface LeadPieChartProps {
  data?: { name: string; leads: number }[];
}

const COLORS = {
  Hot: "var(--chart-1)",
  Warm: "var(--chart-2)",
  Cold: "var(--chart-3)",
  default: "var(--muted)",
};

export function LeadPieChart({ data }: LeadPieChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-[300px] flex items-center justify-center text-muted-foreground">
        No data available
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={80}
          paddingAngle={5}
          dataKey="leads"
        >
          {data.map((entry, index) => {
            const colorKey = entry.name as keyof typeof COLORS;
            return (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[colorKey] || COLORS.default}
                stroke="var(--background)"
                strokeWidth={2}
              />
            );
          })}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "var(--popover)",
            borderColor: "var(--border)",
            borderRadius: "var(--radius)",
          }}
          itemStyle={{ color: "var(--popover-foreground)" }}
        />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
