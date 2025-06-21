'use server';

/**
 * @fileOverview An AI agent that conducts independent research to collect additional information and formulate research questions.
 *
 * - conductIndependentResearch - A function that handles the independent research process.
 * - ConductIndependentResearchInput - The input type for the conductIndependentResearch function.
 * - ConductIndependentResearchOutput - The return type for the conductIndependentResearch function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';
import { ConductIndependentResearchInputSchema } from '@/ai/schemas'; // Import schema object

// Type export remains, Zod object definition removed from here
export type ConductIndependentResearchInput = z.infer<
  typeof ConductIndependentResearchInputSchema
>;

const ConductIndependentResearchOutputSchema = z.object({
  collectedInformation: z
    .string()
    .describe('The additional information collected from independent research.'),
  formulatedQuestions: z
    .array(z.string())
    .describe('The formulated research questions aimed at collecting the right data and identifying the right sources.'),
  sources: z.array(z.string()).describe('The identified sources for the collected information.'),
});
export type ConductIndependentResearchOutput = z.infer<
  typeof ConductIndependentResearchOutputSchema
>;

export async function conductIndependentResearch(
  input: ConductIndependentResearchInput
): Promise<ConductIndependentResearchOutput> {
  return conductIndependentResearchFlow(input);
}

const researchTool = ai.defineTool(
  {
    name: 'webSearch',
    description: 'Conducts a web search to find relevant information.',
    inputSchema: z.object({
      query: z.string().describe('The search query.'),
    }),
    outputSchema: z.object({
      results: z.array(z.string()).describe('The search results.'),
    }),
  },
  async (input) => {
    // Placeholder implementation for web search.  Replace with actual web search.
    // implementation when available.
    // Simulate a delay and varied results.
    await new Promise(resolve => setTimeout(resolve, Math.random() * 1000 + 500));
    const possibleResults = [
      `Summary of findings for: ${input.query}`,
      `Key data points on ${input.query}`,
      `No specific results found for ${input.query}, broader search recommended.`,
      `Detailed report on ${input.query} available at example.com/report`,
    ];
    return { results: [possibleResults[Math.floor(Math.random() * possibleResults.length)]] };
  }
);

const prompt = ai.definePrompt({
  name: 'conductIndependentResearchPrompt',
  input: {schema: ConductIndependentResearchInputSchema}, // Use imported schema object
  output: {schema: ConductIndependentResearchOutputSchema},
  tools: [researchTool],
  prompt: `You are an AI assistant helping a standards expert conduct independent research.

  The expert is researching the following topic: {{{topic}}}

  Here's an initial research question, if provided: {{{researchQuestion}}}

  Your goal is to:
  1. Collect additional information related to the topic using the webSearch tool.
  2. Formulate research questions aimed at collecting the right data and identifying the right sources.

  Output the collected information, formulated research questions, and identified sources in the specified JSON format.

  Make sure that you invoke the webSearch tool multiple times (at least 2, ideally 3-4 if the topic is broad) to collect enough information for the expert. For each search, use a refined or different query to gather diverse information.
  Synthesize the search results into a coherent "collectedInformation" string.
  List all unique, actionable "formulatedQuestions".
  List the "sources" based on information provided by the webSearch tool if any (e.g. URLs mentioned in results).
  `,
});

const conductIndependentResearchFlow = ai.defineFlow(
  {
    name: 'conductIndependentResearchFlow',
    inputSchema: ConductIndependentResearchInputSchema, // Use imported schema object
    outputSchema: ConductIndependentResearchOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
