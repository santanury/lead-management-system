// lib/mock-data.ts
export const kpiData = {
  totalLeads: 256,
  qualifiedLeads: 78,
  avgScore: 64.5,
  newLeadsToday: 12,
};

export const recentLeads = [
  { id: "LEAD-001", name: "John Doe", company: "Acme Inc.", score: 85, status: "qualified" },
  { id: "LEAD-002", name: "Jane Smith", company: "Globex Corp.", score: 72, status: "pending" },
  { id: "LEAD-003", name: "Sam Wilson", company: "Stark Industries", score: 65, status: "pending" },
  { id: "LEAD-004", name: "Alice Johnson", company: "Wayne Enterprises", score: 91, status: "qualified" },
  { id: "LEAD-005", name: "Bob Brown", company: "Cyberdyne Systems", score: 45, status: "rejected" },
];

export const allLeads = Array.from({ length: 25 }, (_, i) => ({
  id: `LEAD-${String(i + 1).padStart(3, "0")}`,
  name: `User ${i + 1}`,
  email: `user${i + 1}@example.com`,
  company: `Company ${String.fromCharCode(65 + (i % 26))}`,
  budget: 10000 + Math.floor(Math.random() * 40000),
  need: ["Product A", "Service B", "Consulting C"][i % 3],
  timeline: `${i % 6 + 1} months`,
  bant_score: Math.floor(40 + Math.random() * 60),
  status: ["qualified", "pending", "rejected"][i % 3],
}));

export const scoringParams = {
  budget_weight: 0.4,
  need_weight: 0.3,
  timeline_weight: 0.2,
  icp_fit_weight: 0.1,
};

export const mockScoringResponse = {
  lead_id: "LEAD-001",
  bant_score: 85,
  breakdown: {
    budget: { score: 90, details: "Client budget aligns perfectly with proposed pricing." },
    need: { score: 80, details: "Client has a clear and immediate need for the solution." },
    timeline: { score: 75, details: "Client is looking to implement within the next quarter." },
    icp_fit: { score: 95, details: "Client fits the Ideal Customer Profile criteria." },
  },
  summary: "This is a high-quality lead with strong potential. Immediate follow-up is recommended.",
};

export const settingsData = {
  autoLeadRouting: true,
  externalEnrichment: false,
  selectedModel: "GPT-4o",
};
