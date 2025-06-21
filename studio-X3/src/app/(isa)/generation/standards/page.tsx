
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Construction } from "lucide-react";

export default function StandardsGenerationPage() {
  return (
    <div className="container mx-auto py-8">
      <Card className="shadow-xl">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold">Standards Generation</CardTitle>
          <CardDescription>
            This feature will assist in generating new standards based on specified requirements.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center min-h-[300px] text-center">
          <Construction className="w-16 h-16 text-muted-foreground mb-4" />
          <h3 className="text-xl font-medium text-muted-foreground">Feature Under Construction</h3>
          <p className="text-muted-foreground">
            AI-assisted standards generation is currently under development. Please check back soon.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
