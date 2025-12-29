// app/scoring/page.tsx
"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, LeadInput, AnalyzedLead } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function LeadSubmissionPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<LeadInput>({
    first_name: "",
    last_name: "",
    email: "",
    company_name: "",
    notes: "",
  });
  const [result, setResult] = useState<AnalyzedLead | null>(null);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const data = await api.analyzeLead(formData);
      setResult(data);
      // Optional: redirect to leads page after short delay or show success
      // router.push("/leads");
    } catch (error) {
      console.error("Analysis failed:", error);
      alert("Failed to analyze lead. Check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-8 max-w-4xl mx-auto w-full">
      <h1 className="text-3xl font-bold">New Lead Analysis</h1>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Form Section */}
        <Card className="h-fit">
          <CardHeader>
            <CardTitle>Submit Lead for AI Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="first_name">First Name</Label>
                  <Input
                    id="first_name"
                    name="first_name"
                    required
                    value={formData.first_name}
                    onChange={handleChange}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="last_name">Last Name</Label>
                  <Input
                    id="last_name"
                    name="last_name"
                    required
                    value={formData.last_name}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="company_name">Company Name</Label>
                <Input
                  id="company_name"
                  name="company_name"
                  required
                  value={formData.company_name}
                  onChange={handleChange}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes">Notes / Inquiry</Label>
                <Textarea
                  id="notes"
                  name="notes"
                  required
                  placeholder="Paste email body or call notes here..."
                  className="min-h-[100px]"
                  value={formData.notes}
                  onChange={handleChange}
                />
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Analyzing..." : "Analyze Lead"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Results Section */}
        {result && (
          <Card className="bg-slate-50 border-green-200">
            <CardHeader>
              <CardTitle className="text-green-700">Analysis Result</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center bg-white p-4 rounded border">
                <span className="font-semibold text-lg">Score</span>
                <span className="text-2xl font-bold">
                  {result.lead_score.score}/100
                </span>
              </div>

              <div className="bg-white p-4 rounded border space-y-2">
                <div className="font-semibold text-sm text-gray-500">
                  CATEGORY
                </div>
                <div className="font-medium">{result.lead_score.category}</div>
              </div>

              <div className="bg-white p-4 rounded border space-y-2">
                <div className="font-semibold text-sm text-gray-500">
                  SUMMARY
                </div>
                <p className="text-sm">{result.lead_score.explanation}</p>
              </div>

              <div className="bg-white p-4 rounded border space-y-2">
                <div className="font-semibold text-sm text-gray-500">
                  BANT BREAKDOWN
                </div>
                <ul className="text-sm space-y-1 list-disc pl-4">
                  <li>
                    <span className="font-medium">Budget:</span>{" "}
                    {result.bant_analysis.budget}
                  </li>
                  <li>
                    <span className="font-medium">Authority:</span>{" "}
                    {result.bant_analysis.authority}
                  </li>
                  <li>
                    <span className="font-medium">Need:</span>{" "}
                    {result.bant_analysis.need}
                  </li>
                  <li>
                    <span className="font-medium">Timeline:</span>{" "}
                    {result.bant_analysis.timeline}
                  </li>
                </ul>
              </div>

              <Button
                variant="outline"
                className="w-full"
                onClick={() => router.push("/leads")}
              >
                View All Leads
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
