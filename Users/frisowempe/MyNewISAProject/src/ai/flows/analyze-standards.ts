// src/ai/flows/analyze-standards.ts
'use server';

/**
 * @fileOverview Analyzes existing standards for inconsistencies and structural issues.
 *
 * - analyzeStandards - A function that analyzes standards documents.
 * - AnalyzeStandardsInput - The input type for the analyzeStandards function.
 * - AnalyzeStandardsOutput - The return type for the analyzeStandards function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';
import { AnalyzeStandardsInputSchema } from '@/ai/schemas'; 

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
  try {
    const {output} = await analyzeStandardsPrompt(input);
    if (!output) {
      console.error('analyzeStandardsPrompt did not return a valid output.');
      return {
        inconsistencies: [],
        structuralIssues: [],
        summary: 'Analysis could not be completed as the AI model failed to produce a structured response. Please try again.',
      };
    }
    return output;
  } catch (error) {
    console.error("Error in analyzeStandards flow:", error);
    return {
      inconsistencies: [],
      structuralIssues: [],
      summary: "An unexpected error occurred during standards analysis. Please check the input or try again later."
    };
  }
}

const analyzeStandardsPrompt = ai.definePrompt({
  name: 'analyzeStandardsPrompt',
  input: {schema: AnalyzeStandardsInputSchema}, 
  output: {schema: AnalyzeStandardsOutputSchema},
  prompt: `You are an expert standards analyst. Your task is to analyze the provided standards document for inconsistencies and structural issues.

Document Content: {{{documentContent}}}

Identify any inconsistencies, overlapping definitions, or structural problems in the document. Provide a summary of your analysis.

Output the inconsistencies and structural issues as lists of strings, and a summary.
`,
});

// Previous flow definition removed for brevity and direct error handling in exported function
// const analyzeStandardsFlow = ai.defineFlow( ... );
