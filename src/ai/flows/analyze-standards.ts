// src/ai/flows/analyze-standards.ts
'use server';

/**
 * @fileOverview Analyzes existing standards for inconsistencies and structural issues.
 *
 * - analyzeStandards - A function that analyzes standards documents.
 * - AnalyzeStandardsInput - The input type for the analyzeStandards function.
 * - AnalyzeStandardsOutput - The return type for the analyzeStandards function.
 */

import {ai, getModelParams} from '@/ai/genkit';
import {z} from 'genkit';
import { AnalyzeStandardsInputSchema } from '@/ai/schemas'; // Import schema object

// Type export remains, Zod object definition removed from here
export type AnalyzeStandardsInput = z.infer<typeof AnalyzeStandardsInputSchema>;

const AnalyzeStandardsOutputSchema = z.object({
  inconsistencies: z
    .array(z.string())
    .describe('A list of inconsistencies found in the document.'),
  structuralIssues: z
    .array(z.string())
    .describe('A list of structural issues found in the document.'),
  summary: z.string().describe('A summary of the analysis.'),
});
export type AnalyzeStandardsOutput = z.infer<typeof AnalyzeStandardsOutputSchema>;

export async function analyzeStandards(input: AnalyzeStandardsInput): Promise<AnalyzeStandardsOutput> {
  return analyzeStandardsFlow(input);
}

const analyzeStandardsFlow = ai.defineFlow(
  {
    name: 'analyzeStandardsFlow',
    inputSchema: AnalyzeStandardsInputSchema, // Use imported schema object
    outputSchema: AnalyzeStandardsOutputSchema,
  },
  async input => {
    // Dynamically get model parameters for 'architect' mode as this is a complex analysis task
    const { model, thinkingBudget } = getModelParams('architect', {
      input_token_count: input.documentContent.length, // Estimate token count
      task_intent: "deep analysis",
      complexity_flags: ["architect", "complex", "deep analysis"]
    });

    const llmResponse = await ai.generate({
      model: model,
      prompt: `You are an expert standards analyst. Your task is to analyze the provided standards document for inconsistencies and structural issues.
Document Content: {{{documentContent}}}
Identify any inconsistencies, overlapping definitions, or structural problems in the document. Provide a summary of your analysis.
Output the inconsistencies and structural issues as lists of strings, and a summary.
`,
      config: {
        maxOutputTokens: thinkingBudget === -1 ? undefined : thinkingBudget,
      },
      output: { schema: AnalyzeStandardsOutputSchema },
    });
    return llmResponse.output!;
  }
);
