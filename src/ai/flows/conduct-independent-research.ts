'use server';

/**
 * @fileOverview An AI agent that conducts independent research to collect additional information and formulate research questions.
 *
 * - conductIndependentResearch - A function that handles the independent research process.
 * - ConductIndependentResearchInput - The input type for the conductIndependentResearch function.
 * - ConductIndependentResearchOutput - The return type for the conductIndependentResearch function.
 */

import {ai, getModelParams} from '@/ai/genkit';
import {z} from 'genkit';
import { ConductIndependentResearchInputSchema } from '@/ai/schemas'; // Import schema object
import { ContentSummarizationTool } from '@/ai/tools/content-summarization-tool'; // Import the new summarization tool
import { use_mcp_tool } from '@modelcontextprotocol/sdk'; // Import use_mcp_tool

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
  summary: z.string().describe('A concise summary of the collected information.'), // New summary field
});
export type ConductIndependentResearchOutput = z.infer<
  typeof ConductIndependentResearchOutputSchema
>;

export async function conductIndependentResearch(
  input: ConductIndependentResearchInput
): Promise<ConductIndependentResearchOutput> {
  return conductIndependentResearchFlow(input);
}

const conductIndependentResearchFlow = ai.defineFlow(
  {
    name: 'conductIndependentResearchFlow',
    inputSchema: ConductIndependentResearchInputSchema, // Use imported schema object
    outputSchema: ConductIndependentResearchOutputSchema,
  },
  async input => {
    // Dynamically get model parameters for 'claude-browser-mode-v2-0' mode
    const { model, thinkingBudget } = getModelParams('claude-browser-mode-v2-0', {
      input_token_count: input.topic.length + (input.researchQuestion?.length || 0), // Estimate token count
      task_intent: "web research",
      complexity_flags: ["web research", "information gathering"]
    });

    const llmResponse = await ai.generate({
      model: model,
      prompt: `You are an AI assistant helping a standards expert conduct independent research.

  The expert is researching the following topic: {{{topic}}}

  Here's an initial research question, if provided: {{{researchQuestion}}}

  Your goal is to:
  1. Collect additional information related to the topic using the brave_web_search tool.
  2. Formulate research questions aimed at collecting the right data and identifying the right sources.

  Output the collected information, formulated research questions, and identified sources in the specified JSON format.

  Make sure that you invoke the brave_web_search tool multiple times (at least 2, ideally 3-4 if the topic is broad) to collect enough information for the expert. For each search, use a refined or different query to gather diverse information.
  Synthesize the search results into a coherent "collectedInformation" string.
  List all unique, actionable "formulatedQuestions".
  List the "sources" based on information provided by the brave_web_search tool if any (e.g. URLs mentioned in results).
  `,
      tools: [
        ai.defineTool(
          {
            name: 'brave_web_search',
            description: 'Performs a web search using the Brave Search API.',
            inputSchema: z.object({
              query: z.string().describe('The search query.'),
              count: z.number().optional().describe('Number of results (1-20, default 10).'),
              offset: z.number().optional().describe('Pagination offset (max 9, default 0).'),
            }),
            outputSchema: z.object({
              results: z.array(z.string()).describe('The search results.'),
            }),
          },
          async (args) => {
            const result = await use_mcp_tool({
              server_name: 'brave-search',
              tool_name: 'brave_web_search',
              arguments: args,
            });
            if (result.isError) {
              throw new Error(result.content[0].text);
            }
            return { results: [result.content[0].text] };
          }
        ),
      ],
      config: {
        maxOutputTokens: thinkingBudget === -1 ? undefined : thinkingBudget,
      },
      output: { schema: ConductIndependentResearchOutputSchema },
    });

    const collectedInformation = llmResponse.output!.collectedInformation;
    const formulatedQuestions = llmResponse.output!.formulatedQuestions;
    const sources = llmResponse.output!.sources;

    // Use the new summarization tool
    const summarizationTool = new ContentSummarizationTool();
    const { summary } = await summarizationTool.summarize({ text: collectedInformation });

    return {
      collectedInformation,
      formulatedQuestions,
      sources,
      summary, // Include the generated summary
    };
  }
);
