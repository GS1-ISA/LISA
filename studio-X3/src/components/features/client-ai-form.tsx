
"use client";

import React, { useState, type ReactNode } from "react";
import { useForm, type UseFormReturn, type FieldValues, type SubmitHandler } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { ZodSchema } from "zod";
import { Button } from "@/components/ui/button";
import { AiOutputCard } from "./ai-output-card";
import type { ExplainableOutput } from "@/lib/types";
import { Form } from "@/components/ui/form";

interface ClientAiFormProps<TFormValues extends FieldValues, TResponseData> {
  formSchema: ZodSchema<TFormValues>;
  defaultValues?: Partial<TFormValues>;
  serverAction: (data: TFormValues) => Promise<{ success: boolean; data?: TResponseData; error?: string }>;
  renderFormFields: (form: UseFormReturn<TFormValues>) => ReactNode;
  renderOutput: (data: TResponseData) => ReactNode;
  outputTitle: string;
  formSubmitButtonText?: string;
  extractExplainability?: (data: TResponseData) => ExplainableOutput;
}

export function ClientAiForm<TFormValues extends FieldValues, TResponseData>({
  formSchema,
  defaultValues,
  serverAction,
  renderFormFields,
  renderOutput,
  outputTitle,
  formSubmitButtonText = "Submit",
  extractExplainability,
}: ClientAiFormProps<TFormValues, TResponseData>) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [responseData, setResponseData] = useState<TResponseData | null>(null);
  const [explainabilityData, setExplainabilityData] = useState<ExplainableOutput | undefined>(undefined);

  const form = useForm<TFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: defaultValues as any, // Casting because defaultValues can be partial
  });

  const onSubmit: SubmitHandler<TFormValues> = async (data) => {
    setIsLoading(true);
    setError(null);
    setResponseData(null);
    setExplainabilityData(undefined);

    const result = await serverAction(data);

    if (result.success && result.data) {
      setResponseData(result.data);
      if (extractExplainability) {
        setExplainabilityData(extractExplainability(result.data));
      }
    } else {
      setError(result.error || "An unknown error occurred.");
    }
    setIsLoading(false);
  };

  return (
    <div className="space-y-6">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {renderFormFields(form)}
          <Button type="submit" disabled={isLoading} className="w-full sm:w-auto bg-primary hover:bg-primary/90 text-primary-foreground">
            {isLoading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-foreground mr-2"></div>
            ) : null}
            {formSubmitButtonText}
          </Button>
        </form>
      </Form>

      {(isLoading || error || responseData) && (
         <AiOutputCard
          title={outputTitle}
          data={responseData}
          renderOutput={renderOutput as (data: any) => React.ReactNode} // Cast needed due to TResponseData | null
          explainability={explainabilityData}
          isLoading={isLoading}
          error={error}
        />
      )}
    </div>
  );
}
