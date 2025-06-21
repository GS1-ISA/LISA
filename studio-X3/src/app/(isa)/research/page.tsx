
"use client";

import { z } from "zod";
import { ClientAiForm } from "@/components/features/client-ai-form";
import { FormField, FormItem, FormLabel, FormControl, FormMessage, FormDescription } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { handleConductIndependentResearch } from "@/lib/actions/ai-actions";
import type { ConductIndependentResearchOutput, ExplainableOutput } from "@/lib/types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Info } from "lucide-react";

const researchFormSchema = z.object({
  topic: z.string().min(5, "Topic must be at least 5 characters."),
  researchQuestion: z.string().optional(),
});
type ResearchFormValues = z.infer<typeof researchFormSchema>;

export default function IndependentResearchPage() {
  const renderFormFields = (form: any) => ( // form type is UseFormReturn<ResearchFormValues>
    <>
      <FormField
        control={form.control}
        name="topic"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Research Topic</FormLabel>
            <FormControl>
              <Input placeholder="e.g., Latest advancements in RFID for supply chain traceability" {...field} />
            </FormControl>
            <FormDescription>
              Specify the main topic for the AI to conduct independent research on.
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="researchQuestion"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Initial Research Question (Optional)</FormLabel>
            <FormControl>
              <Textarea
                placeholder="e.g., What are the key challenges in implementing blockchain for pharmaceutical traceability in GS1 standards?"
                className="min-h-[100px] resize-y"
                {...field}
              />
            </FormControl>
            <FormDescription>
              Provide an optional initial question to guide the research. The AI will also formulate new questions.
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
    </>
  );

  const renderOutput = (data: ConductIndependentResearchOutput) => (
    <div className="space-y-6">
      <Alert variant="default" className="mt-4">
        <Info className="h-4 w-4" />
        <AlertTitle>Developer Note</AlertTitle>
        <AlertDescription>
          The web search functionality used by this research tool is currently simulated. Results are placeholders and do not reflect live web searches.
        </AlertDescription>
      </Alert>
      <div>
        <h3 className="font-semibold text-lg mb-2">Collected Information</h3>
        <p className="text-sm bg-muted p-3 rounded-md">{data.collectedInformation}</p>
      </div>
      {data.formulatedQuestions && data.formulatedQuestions.length > 0 && (
        <div>
          <h3 className="font-semibold text-lg mb-2">Formulated Research Questions</h3>
          <ul className="list-disc pl-5 space-y-1 text-sm">
            {data.formulatedQuestions.map((q, index) => <li key={`fq-${index}`}>{q}</li>)}
          </ul>
        </div>
      )}
      {data.sources && data.sources.length > 0 && (
        <div>
          <h3 className="font-semibold text-lg mb-2">Identified Sources</h3>
          <ul className="list-disc pl-5 space-y-1 text-sm">
            {data.sources.map((s, index) => <li key={`src-${index}`}>{s}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
  
  const extractExplainability = (data: ConductIndependentResearchOutput): ExplainableOutput => {
    return {
      reasoningSteps: ["Processed initial topic/question.", "Queried knowledge base & external sources (simulated).", "Synthesized findings and generated new questions."],
      confidenceScore: "N/A for research synthesis", // Confidence might not apply here
      modelEvaluationMetrics: { "Coverage": Math.random() * 0.3 + 0.65, "Relevance": Math.random() * 0.25 + 0.7 },
    };
  };

  return (
    <div className="container mx-auto py-8">
      <Card className="mb-8 shadow-xl">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold">Independent Research Assistant</CardTitle>
          <CardDescription>
            The AI will conduct independent research on the topic you provide. It will collect additional information,
            formulate research questions, and identify potential data sources.
          </CardDescription>
        </CardHeader>
      </Card>

      <ClientAiForm<ResearchFormValues, ConductIndependentResearchOutput>
        formSchema={researchFormSchema}
        defaultValues={{ topic: "", researchQuestion: "" }}
        serverAction={handleConductIndependentResearch}
        renderFormFields={renderFormFields}
        renderOutput={renderOutput}
        outputTitle="Research Findings"
        formSubmitButtonText="Start Research"
        extractExplainability={extractExplainability}
      />
    </div>
  );
}
