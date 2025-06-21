
"use client";

import { AiOutputCard } from "@/components/features/ai-output-card";
import type { ExplainableOutput } from "@/lib/types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState } from "react";

interface DemoData {
  title: string;
  content: string;
}

export default function ExplainabilityDemoPage() {
  const [demoOutput, setDemoOutput] = useState<DemoData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string|null>(null);

  const mockProcess = () => {
    setIsLoading(true);
    setError(null);
    setDemoOutput(null);
    setTimeout(() => {
      const success = Math.random() > 0.3; // 70% chance of success
      if (success) {
        setDemoOutput({
          title: "Sample AI Analysis Result",
          content: "This is a demonstration of the AI output. The system has analyzed the provided data and generated this summary. Key findings include A, B, and C. Further details can be explored in the reasoning steps.",
        });
      } else {
        setError("A simulated error occurred during processing. Please try again.");
      }
      setIsLoading(false);
    }, 1500);
  };


  const explainabilityData: ExplainableOutput = {
    reasoningSteps: [
      "Received input data.",
      "Preprocessed text for analysis.",
      "Applied core logic model X.",
      "Cross-validated with knowledge base Y.",
      "Generated output summary.",
      "Calculated confidence score.",
    ],
    confidenceScore: 0.88,
    modelEvaluationMetrics: {
      Accuracy: 0.92,
      Precision: 0.89,
      Recall: 0.94,
      "F1-Score": 0.91,
      Faithfulness: "High (qualitative)",
    },
  };

  const renderDemoOutput = (data: DemoData) => (
    <p>{data.content}</p>
  );

  return (
    <div className="container mx-auto py-8 space-y-8">
      <Card className="shadow-xl">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold">Explainable Output Interface Demo</CardTitle>
          <CardDescription>
            This page demonstrates how AI outputs are presented with explainability features.
            Click the button below to simulate an AI process and see the output card.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={mockProcess} disabled={isLoading}>
            {isLoading ? "Processing..." : "Simulate AI Process"}
          </Button>
        </CardContent>
      </Card>

      {(isLoading || error || demoOutput) && (
        <AiOutputCard<DemoData>
          title={demoOutput?.title || "AI Output"}
          data={demoOutput || undefined}
          renderOutput={renderDemoOutput}
          explainability={demoOutput ? explainabilityData : undefined} // Only show explainability if there's data
          isLoading={isLoading}
          error={error}
        />
      )}
    </div>
  );
}
