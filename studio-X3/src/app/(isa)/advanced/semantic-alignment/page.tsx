
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Construction } from "lucide-react";

export default function SemanticAlignmentPage() {
  return (
    <div className="container mx-auto py-8">
      <Card className="shadow-xl">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold">Semantic Alignment</CardTitle>
          <CardDescription>
            This feature will facilitate semantic alignment between international versions of standards.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center min-h-[300px] text-center">
          <Construction className="w-16 h-16 text-muted-foreground mb-4" />
          <h3 className="text-xl font-medium text-muted-foreground">Feature Under Construction</h3>
          <p className="text-muted-foreground">
            Semantic alignment tools are currently in development. Please check back later.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
