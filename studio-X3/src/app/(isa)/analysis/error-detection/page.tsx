
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Construction } from "lucide-react";

export default function ErrorDetectionPage() {
  return (
    <div className="container mx-auto py-8">
      <Card className="shadow-xl">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold">Error Detection and Correction</CardTitle>
          <CardDescription>
            This feature will help detect and correct errors or overlapping definitions in standards documents.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center min-h-[300px] text-center">
          <Construction className="w-16 h-16 text-muted-foreground mb-4" />
          <h3 className="text-xl font-medium text-muted-foreground">Feature Under Construction</h3>
          <p className="text-muted-foreground">
            The AI-powered error detection and correction capabilities are currently in development.
            Check back later for updates!
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
