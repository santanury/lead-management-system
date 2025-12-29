// app/settings/page.tsx
"use client";

import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { settingsData } from "@/lib/mock-data";

export default function SettingsPage() {
  const [autoRouting, setAutoRouting] = useState(
    settingsData.autoLeadRouting
  );
  const [enrichment, setEnrichment] = useState(
    settingsData.externalEnrichment
  );
  const [llm, setLlm] = useState(settingsData.selectedModel);

  return (
    <div className="flex flex-col gap-8">
      <h1 className="text-3xl font-bold">Settings</h1>
      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Automation Settings</CardTitle>
          <CardDescription>
            Configure automated actions and AI models.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between space-x-2">
            <Label htmlFor="auto-routing" className="flex flex-col space-y-1">
              <span>Auto-Lead Routing</span>
              <span className="font-normal leading-snug text-muted-foreground">
                Automatically assign new leads to team members.
              </span>
            </Label>
            <Switch
              id="auto-routing"
              checked={autoRouting}
              onCheckedChange={setAutoRouting}
            />
          </div>
          <div className="flex items-center justify-between space-x-2">
            <Label htmlFor="enrichment" className="flex flex-col space-y-1">
              <span>External Enrichment</span>
              <span className="font-normal leading-snug text-muted-foreground">
                Use third-party services to enrich lead data.
              </span>
            </Label>
            <Switch
              id="enrichment"
              checked={enrichment}
              onCheckedChange={setEnrichment}
            />
          </div>
          <div className="flex items-center justify-between space-x-2">
            <Label htmlFor="llm-model" className="flex flex-col space-y-1">
              <span>AI Scoring Model</span>
               <span className="font-normal leading-snug text-muted-foreground">
                Select the model for lead scoring and analysis.
              </span>
            </Label>
            <Select value={llm} onValueChange={setLlm}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="GPT-4o">GPT-4o</SelectItem>
                <SelectItem value="Gemini 2.0">Gemini 2.0</SelectItem>
                <SelectItem value="Llama3">Llama3</SelectItem>
              </SelectContent>
            </Select>
          </div>
           <Button>Save Settings</Button>
        </CardContent>
      </Card>
    </div>
  );
}
