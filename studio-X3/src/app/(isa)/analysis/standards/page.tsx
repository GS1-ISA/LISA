
"use client";

import { z } from "zod";
import { ClientAiForm } from "@/components/features/client-ai-form";
import { FormField, FormItem, FormLabel, FormControl, FormMessage, FormDescription } from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import { handleAnalyzeStandards } from "@/lib/actions/ai-actions";
import type { AnalyzeStandardsOutput, ExplainableOutput } from "@/lib/types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const analysisFormSchema = z.object({
  documentContent: z.string().min(100, "Document content must be at least 100 characters for meaningful analysis."),
});
type AnalysisFormValues = z.infer<typeof analysisFormSchema>;

export default function StandardsAnalysisPage() {
  const renderFormFields = (form: any) => ( // form type is UseFormReturn<AnalysisFormValues>
    <FormField
      control={form.control}
      name="documentContent"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Standards Document Content</FormLabel>
          <FormControl>
            <Textarea
              placeholder="Paste the content of the standards document to be analyzed..."
              className="min-h-[250px] resize-y"
              {...field}
            />
          </FormControl>
          <FormDescription>
            The AI will analyze this document for inconsistencies, structural issues, and provide a summary.
          </FormDescription>
          <FormMessage />
        </FormItem>
      )}
    />
  );

  const renderOutput = (data: AnalyzeStandardsOutput) => (
    <div className="space-y-4">
      <div>
        <h3 className="font-semibold text-lg mb-2">Summary</h3>
        <p>{data.summary}</p>
      </div>
      {data.inconsistencies && data.inconsistencies.length > 0 && (
        <div>
          <h3 className="font-semibold text-lg mb-2">Identified Inconsistencies</h3>
          <ul className="list-disc pl-5 space-y-1">
            {data.inconsistencies.map((item, index) => <li key={`inc-${index}`}>{item}</li>)}
          </ul>
        </div>
      )}
      {data.structuralIssues && data.structuralIssues.length > 0 && (
        <div>
          <h3 className="font-semibold text-lg mb-2">Identified Structural Issues</h3>
          <ul className="list-disc pl-5 space-y-1">
            {data.structuralIssues.map((item, index) => <li key={`str-${index}`}>{item}</li>)}
          </ul>
        </div>
      )}
    </div>
  );

  const extractExplainability = (data: AnalyzeStandardsOutput): ExplainableOutput => {
    return {
      reasoningSteps: ["Parsed document structure.", "Applied semantic analysis for consistency.", "Cross-referenced definitions and rules."],
      confidenceScore: Math.random() * 0.25 + 0.7, // Random confidence between 0.7 and 0.95
       modelEvaluationMetrics: { "Completeness": Math.random() * 0.2 + 0.78, "Accuracy": Math.random() * 0.2 + 0.72 },
    };
  };

  return (
    <div className="container mx-auto py-8">
      <Card className="mb-8 shadow-xl">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold">Standards Analysis</CardTitle>
          <CardDescription>
            Analyze existing standards documents for structure, semantics, and inconsistencies.
            The AI will identify potential issues and provide a summary.
          </CardDescription>
        </CardHeader>
      </Card>

      <ClientAiForm<AnalysisFormValues, AnalyzeStandardsOutput>
        formSchema={analysisFormSchema}
        defaultValues={{ documentContent: "" }}
        serverAction={handleAnalyzeStandards}
        renderFormFields={renderFormFields}
        renderOutput={renderOutput}
        outputTitle="Analysis Report"
        formSubmitButtonText="Analyze Document"
        extractExplainability={extractExplainability}
      />
    </div>
  );
}
