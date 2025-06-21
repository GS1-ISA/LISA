
"use client";

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Separator } from "@/components/ui/separator";
import { FeedbackButtons } from "./feedback-buttons";
import { OutputActions } from "./output-actions";
import type { ExplainableOutput } from "@/lib/types";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Info } from "lucide-react";

interface AiOutputCardProps<T> {
  title: string;
  data: T;
  renderOutput: (data: T) => React.ReactNode;
  explainability?: ExplainableOutput;
  isLoading?: boolean;
  error?: string | null;
}

const metricDefinitions: Record<string, string> = {
  Accuracy: "The proportion of correct predictions among the total number of cases evaluated.",
  Precision: "The proportion of true positive predictions among all positive predictions made by the model.",
  Recall: "The proportion of true positive predictions among all actual positive cases (sensitivity).",
  "F1-Score": "The harmonic mean of Precision and Recall, providing a single score that balances both.",
  Faithfulness: "How accurately the explanation reflects the model's true internal reasoning process.",
  Completeness: "The extent to which the analysis or output captures all relevant aspects of the input.",
  Clarity: "How clear, understandable, and unambiguous the output or explanation is.",
  Fidelity: "How well the AI's output aligns with the provided source information or ground truth.",
  Robustness: "The model's ability to maintain performance despite noise or variations in the input.",
  Coverage: "The extent to which the research or analysis addresses the breadth of the requested topic.",
  Relevance: "The degree to which the output is pertinent and applicable to the posed question or task.",
};

export function AiOutputCard<T>({
  title,
  data,
  renderOutput,
  explainability,
  isLoading,
  error,
}: AiOutputCardProps<T>) {
  if (isLoading) {
    return (
      <Card className="w-full shadow-lg">
        <CardHeader>
          <CardTitle>{title}</CardTitle>
          <CardDescription>Processing your request...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full shadow-lg border-destructive">
        <CardHeader>
          <CardTitle className="text-destructive">{title} - Error</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-destructive-foreground bg-destructive p-3 rounded-md">{error}</p>
        </CardContent>
      </Card>
    );
  }
  
  if (!data) {
    return null; // Or some placeholder if no data yet but not loading/error
  }

  return (
    <TooltipProvider>
      <Card className="w-full shadow-lg">
        <CardHeader>
          <CardTitle>{title}</CardTitle>
          {explainability?.confidenceScore && (
            <CardDescription>
              Confidence: {typeof explainability.confidenceScore === 'number' ? explainability.confidenceScore.toFixed(2) : explainability.confidenceScore}
            </CardDescription>
          )}
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-auto max-h-[400px] pr-4">
           <div className="prose prose-sm dark:prose-invert max-w-none">
              {renderOutput(data)}
            </div>
          </ScrollArea>
          
          {(explainability?.reasoningSteps || explainability?.modelEvaluationMetrics) && (
            <>
              <Separator className="my-4" />
              <Accordion type="single" collapsible className="w-full">
                {explainability.reasoningSteps && explainability.reasoningSteps.length > 0 && (
                  <AccordionItem value="reasoning">
                    <AccordionTrigger>Reasoning Steps</AccordionTrigger>
                    <AccordionContent>
                      <ul className="list-disc pl-5 space-y-1 text-sm">
                        {explainability.reasoningSteps.map((step, index) => (
                          <li key={index}>{step}</li>
                        ))}
                      </ul>
                    </AccordionContent>
                  </AccordionItem>
                )}
                {explainability.modelEvaluationMetrics && Object.keys(explainability.modelEvaluationMetrics).length > 0 && (
                   <AccordionItem value="metrics">
                    <AccordionTrigger>Model Evaluation Metrics</AccordionTrigger>
                    <AccordionContent>
                      <ul className="space-y-1 text-sm">
                        {Object.entries(explainability.modelEvaluationMetrics).map(([key, value]) => (
                          <li key={key} className="flex items-center">
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <strong className="flex items-center cursor-help hover:text-primary">
                                  {key}
                                  <Info className="h-3 w-3 ml-1.5 opacity-70" />
                                </strong>
                              </TooltipTrigger>
                              <TooltipContent side="top" className="max-w-xs text-xs">
                                <p>{metricDefinitions[key] || "No definition available."}</p>
                              </TooltipContent>
                            </Tooltip>
                            <span className="ml-1">: {typeof value === 'number' ? value.toFixed(2) : value}</span>
                          </li>
                        ))}
                      </ul>
                    </AccordionContent>
                  </AccordionItem>
                )}
              </Accordion>
            </>
          )}
        </CardContent>
        <CardFooter className="flex flex-col sm:flex-row justify-between items-center gap-4 pt-4">
          <FeedbackButtons />
          <OutputActions dataToExport={data} />
        </CardFooter>
      </Card>
    </TooltipProvider>
  );
}
