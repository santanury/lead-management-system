import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Lead } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

interface LeadDetailsDialogProps {
  lead: Lead | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function LeadDetailsDialog({
  lead,
  open,
  onOpenChange,
}: LeadDetailsDialogProps) {
  if (!lead) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[85vh]">
        <DialogHeader>
          <div className="flex items-center justify-between pr-8">
            <DialogTitle className="text-2xl">
              {lead.first_name} {lead.last_name}
            </DialogTitle>
            <Badge
              className="text-lg px-4 py-1"
              variant={
                lead.category === "Hot"
                  ? "default"
                  : lead.category === "Cold"
                  ? "destructive"
                  : "outline"
              }
            >
              {lead.score} - {lead.category}
            </Badge>
          </div>
          <DialogDescription>
            {lead.email} • {lead.company_name}
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="h-[60vh] pr-4">
          <div className="space-y-6">
            {/* Summary */}
            <div className="p-4 bg-muted rounded-lg">
              <h3 className="font-semibold mb-2">AI Summary</h3>
              <p className="text-sm text-muted-foreground">
                {lead.explanation}
              </p>
            </div>

            <Separator />

            {/* BANT Analysis */}
            <div>
              <h3 className="text-lg font-semibold mb-3">BANT Analysis</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <span className="font-medium text-sm">Budget</span>
                  <p className="text-sm text-muted-foreground bg-secondary/50 p-2 rounded">
                    {lead.budget_analysis}
                  </p>
                </div>
                <div className="space-y-1">
                  <span className="font-medium text-sm">Authority</span>
                  <p className="text-sm text-muted-foreground bg-secondary/50 p-2 rounded">
                    {lead.authority_analysis}
                  </p>
                </div>
                <div className="space-y-1">
                  <span className="font-medium text-sm">Need</span>
                  <p className="text-sm text-muted-foreground bg-secondary/50 p-2 rounded">
                    {lead.need_analysis}
                  </p>
                </div>
                <div className="space-y-1">
                  <span className="font-medium text-sm">Timeline</span>
                  <p className="text-sm text-muted-foreground bg-secondary/50 p-2 rounded">
                    {lead.timeline_analysis}
                  </p>
                </div>
              </div>
            </div>

            <Separator />

            {/* Enrichment Data */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Company Enrichment</h3>
              {lead.company_info ? (
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Industry:</span>{" "}
                    {lead.company_info.industry}
                  </div>
                  <div>
                    <span className="font-medium">Size:</span>{" "}
                    {lead.company_info.size}
                  </div>
                  <div className="col-span-2">
                    <span className="font-medium">Website:</span>{" "}
                    <a
                      href={lead.company_info.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-500 hover:underline"
                    >
                      {lead.company_info.website}
                    </a>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  No enrichment data available.
                </p>
              )}
            </div>

            <Separator />

            {/* Original Message */}
            <div>
              <h3 className="font-semibold mb-2">Original Message</h3>
              <p className="text-sm text-muted-foreground italic border-l-2 pl-4">
                "{lead.notes}"
              </p>
            </div>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
