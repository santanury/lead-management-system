// app/settings/page.tsx
"use client";

import { useEffect, useState } from "react";
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
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import axios from "axios";

// Using simple axios calls here, could be moved to api.ts
const API_BASE_URL = "http://localhost:8000/api/v1";

export default function SettingsPage() {
  const [autoRouting, setAutoRouting] = useState(true);
  const [enrichment, setEnrichment] = useState(false);
  const [llm, setLlm] = useState("gemini-2.5-flash");
  const [availableModels, setAvailableModels] = useState<
    { id: string; name: string }[]
  >([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load settings from backend
    axios
      .get(`${API_BASE_URL}/settings`)
      .then((response) => {
        const data = response.data;
        setAutoRouting(data.auto_routing_enabled);
        setEnrichment(data.enrichment_enabled);
        setLlm(data.selected_model);
        if (data.available_models) {
          setAvailableModels(data.available_models);
        }
      })
      .catch((err) => console.error("Failed to load settings", err))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    try {
      await axios.put(`${API_BASE_URL}/settings`, {
        selected_model: llm,
        auto_routing_enabled: autoRouting,
        enrichment_enabled: enrichment,
      });
      alert("Settings saved!");
    } catch (error) {
      console.error("Failed to save settings", error);
      alert("Failed to save settings.");
    }
  };

  if (loading) return <div className="p-8">Loading settings...</div>;

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
                Select the Gemini model for analysis.
              </span>
            </Label>
            <Select value={llm} onValueChange={setLlm}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                {availableModels.map((model) => (
                  <SelectItem key={model.id} value={model.id}>
                    {model.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button onClick={handleSave}>Save Settings</Button>
        </CardContent>
      </Card>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Appearance Settings</CardTitle>
          <CardDescription>
            Customize the look and feel of the application.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between space-x-2">
            <Label htmlFor="theme-select" className="flex flex-col space-y-1">
              <span>Theme</span>
              <span className="font-normal leading-snug text-muted-foreground">
                Select the application theme.
              </span>
            </Label>
            <ThemeSelector />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

import { useTheme } from "next-themes";

function ThemeSelector() {
  const { theme, setTheme } = useTheme();

  return (
    <Select value={theme} onValueChange={setTheme}>
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="Select theme" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="light">Light</SelectItem>
        <SelectItem value="dark">Dark</SelectItem>
        <SelectItem value="system">System</SelectItem>
      </SelectContent>
    </Select>
  );
}
