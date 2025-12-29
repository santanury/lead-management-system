import axios from "axios";

// Models matching Backend Pydantic models
export interface LeadInput {
  first_name: string;
  last_name: string;
  email: string;
  company_name: string;
  notes: string;
}

export interface BANTAnalysis {
  budget: string;
  authority: string;
  need: string;
  timeline: string;
}

export interface EnrichmentData {
  company_info?: Record<string, any>;
  email_valid: boolean;
}

export interface LeadScore {
  score: number;
  category: string;
  explanation: string;
}

export interface RoutingDecision {
  queue: string;
  reason: string;
}

export interface AnalyzedLead {
  lead_input: LeadInput;
  bant_analysis: BANTAnalysis;
  enrichment_data: EnrichmentData;
  lead_score: LeadScore;
  routing_decision: RoutingDecision;
}

// Database Lead model (flattens some fields + adds ID)
export interface Lead {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  company_name: string;
  notes: string;

  // Flattened Analysis
  budget_analysis: string;
  authority_analysis: string;
  need_analysis: string;
  timeline_analysis: string;

  score: number;
  category: string;
  explanation: string;

  queue: string;
  routing_reason: string;
}

const API_BASE_URL = "http://localhost:8000/api/v1";

export interface DashboardStats {
  total_leads: number;
  qualified_leads: number;
  avg_score: number;
  new_leads_today: number;
}

export const api = {
  // Fetch all leads
  getLeads: async (): Promise<Lead[]> => {
    const response = await axios.get(`${API_BASE_URL}/`);
    return response.data;
  },

  // Get dashboard stats
  getStats: async (): Promise<DashboardStats> => {
    const response = await axios.get(`${API_BASE_URL}/stats`);
    return response.data;
  },

  // Analyze a new lead
  analyzeLead: async (data: LeadInput): Promise<AnalyzedLead> => {
    const response = await axios.post(`${API_BASE_URL}/analyze`, data);
    return response.data;
  },
};
