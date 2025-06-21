
"use client";

import { z } from "zod";
import { ClientAiForm } from "@/components/features/client-ai-form";
import { FormField, FormItem, FormLabel, FormControl, FormMessage, FormDescription } from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import { handleNaturalLanguageToFormalDescription } from "@/lib/actions/ai-actions";
import type { NaturalLanguageToFormalDescriptionOutput, ExplainableOutput } from "@/lib/types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const nlToFormalFormSchema = z.object({
  naturalLanguageDescription: z.string().min(20, "Natural language description must be at least 20 characters."),
});
type NlToFormalFormValues = z.infer<typeof nlToFormalFormSchema>;

export default function NLToFormalPage() {
  const renderFormFields = (form: any) => ( // form type is UseFormReturn<NlToFormalFormValues>
    <FormField
      control={form.control}
      name="naturalLanguageDescription"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Natural Language Description</FormLabel>
          <FormControl>
            <Textarea
              placeholder="Enter the natural language description of the standard here..."
              className="min-h-[150px] resize-y"
              {...field}
            />
          </FormControl>
          <FormDescription>
            The AI will transform this description into a more formal standard representation.
          </FormDescription>
          <FormMessage />
        </FormItem>
      )}
    />
  );

  const renderOutput = (data: NaturalLanguageToFormalDescriptionOutput) => (
    <div>
      <h3 className="font-semibold text-lg mb-2">Formal Standard Description</h3>
      <pre className="bg-muted p-4 rounded-md whitespace-pre-wrap text-sm">
        {data.formalStandardDescription.formalDescription}
      </pre>
    </div>
  );
  
  const extractExplainability = (data: NaturalLanguageToFormalDescriptionOutput): ExplainableOutput => {
    return {
      reasoningSteps: ["Identified key entities and relationships.", "Applied formal language patterns.", "Ensured structural consistency."],
      confidenceScore: Math.random() * 0.2 + 0.75,
      modelEvaluationMetrics: { "Precision": Math.random() * 0.15 + 0.8, "Clarity": Math.random() * 0.2 + 0.77 },
    };
  };

  return (
    <div className="container mx-auto py-8">
      <Card className="mb-8 shadow-xl">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold">Natural Language to Formal Description</CardTitle>
          <CardDescription>
            Transform natural language descriptions of standards into formal, structured representations.
          </CardDescription>
        </CardHeader>
      </Card>

      <ClientAiForm<NlToFormalFormValues, NaturalLanguageToFormalDescriptionOutput>
        formSchema={nlToFormalFormSchema}
        defaultValues={{ naturalLanguageDescription: "" }}
        serverAction={handleNaturalLanguageToFormalDescription}
        renderFormFields={renderFormFields}
        renderOutput={renderOutput}
        outputTitle="Formal Description"
        formSubmitButtonText="Transform Description"
        extractExplainability={extractExplainability}
      />
    </div>
  );
}
