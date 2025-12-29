// app/leads/page.tsx
"use client";

import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { api, Lead } from "@/lib/api";

const LEADS_PER_PAGE = 10;

import { LeadDetailsDialog } from "@/components/lead-details-dialog";

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [scoreFilter, setScoreFilter] = useState("all");
  const [currentPage, setCurrentPage] = useState(1);

  // Dialog state
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  useEffect(() => {
    const fetchLeads = async () => {
      try {
        const data = await api.getLeads();
        setLeads(data);
      } catch (error) {
        console.error("Failed to fetch leads:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchLeads();
  }, []);

  const filteredLeads = leads
    .filter(
      (lead) =>
        lead.first_name.toLowerCase().includes(search.toLowerCase()) ||
        lead.last_name.toLowerCase().includes(search.toLowerCase()) ||
        lead.email.toLowerCase().includes(search.toLowerCase()) ||
        lead.company_name.toLowerCase().includes(search.toLowerCase())
    )
    .filter((lead) => {
      // Status isn't explicitly in DB model yet aside from Queue, mapping Queue -> Status approximately
      if (statusFilter === "all") return true;
      return true; // Placeholder until status is unified
    })
    .filter((lead) => {
      if (scoreFilter === "all") return true;
      const score = lead.score;
      if (scoreFilter === "low") return score < 60;
      if (scoreFilter === "medium") return score >= 60 && score < 80;
      if (scoreFilter === "high") return score >= 80;
      return true;
    });

  const totalPages = Math.ceil(filteredLeads.length / LEADS_PER_PAGE);
  const paginatedLeads = filteredLeads.slice(
    (currentPage - 1) * LEADS_PER_PAGE,
    currentPage * LEADS_PER_PAGE
  );

  if (loading) {
    return <div>Loading leads...</div>;
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-3xl font-bold">Leads</h1>
      <div className="flex items-center gap-4">
        <Input
          placeholder="Search leads..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setCurrentPage(1);
          }}
          className="max-w-sm"
        />
        <Select
          value={statusFilter}
          onValueChange={(value) => {
            setStatusFilter(value);
            setCurrentPage(1);
          }}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="qualified">Qualified</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="rejected">Rejected</SelectItem>
          </SelectContent>
        </Select>
        <Select
          value={scoreFilter}
          onValueChange={(value) => {
            setScoreFilter(value);
            setCurrentPage(1);
          }}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by score" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Scores</SelectItem>
            <SelectItem value="low">Low (&lt;60)</SelectItem>
            <SelectItem value="medium">Medium (60-80)</SelectItem>
            <SelectItem value="high">High (&gt;80)</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Company</TableHead>
              <TableHead>Budget</TableHead>
              <TableHead>Score</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedLeads.map((lead) => (
              <TableRow
                key={lead.id}
                className="cursor-pointer hover:bg-muted/50"
                onClick={() => {
                  setSelectedLead(lead);
                  setDetailsOpen(true);
                }}
              >
                <TableCell>
                  <div className="font-medium">
                    {lead.first_name} {lead.last_name}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {lead.email}
                  </div>
                </TableCell>
                <TableCell>{lead.company_name}</TableCell>
                {/* Budget is text in DB ("$100k"), not necessarily number, so no toLocaleString() */}
                <TableCell>
                  {lead.budget_analysis.substring(0, 20)}...
                </TableCell>
                <TableCell>{lead.score}</TableCell>
                <TableCell>
                  <Badge
                    variant={
                      lead.category === "Hot"
                        ? "default"
                        : lead.category === "Cold"
                        ? "destructive"
                        : "outline"
                    }
                  >
                    {lead.category}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      <LeadDetailsDialog
        lead={selectedLead}
        open={detailsOpen}
        onOpenChange={setDetailsOpen}
      />
      <div className="flex items-center justify-end space-x-2 py-4">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
          disabled={currentPage === 1}
        >
          Previous
        </Button>
        <span className="text-sm">
          Page {currentPage} of {totalPages}
        </span>
        <Button
          variant="outline"
          size="sm"
          onClick={() =>
            setCurrentPage((prev) => Math.min(prev + 1, totalPages))
          }
          disabled={currentPage === totalPages}
        >
          Next
        </Button>
      </div>
    </div>
  );
}
