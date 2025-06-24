
// src/ai/flows/answer-gs1-questions-with-vector-search.ts
'use server';

/**
 * @fileOverview An AI agent that answers questions about GS1 standards
 * documents by:
 * 1. Generating an embedding for the user's question (simulated).
 * 2. Querying a vector store tool with this embedding to get relevant document chunks (simulated).
 * 3. Synthesizing an answer from these chunks using an LLM.
 * This flow demonstrates an advanced RAG (Retrieval Augmented Generation) pattern
 * with explicit pipeline steps.
 *
 * - answerGs1QuestionsWithVectorSearch - A function that answers questions using vector search.
 * - AnswerGs1QuestionsWithVectorSearchInput - The input type for the function.
 * - AnswerGs1QuestionsWithVectorSearchOutput - The return type for the function.
 */

import {ai, getModelParams} from '@/ai/genkit';
import {z} from 'genkit';
import { AnswerGs1QuestionsWithVectorSearchInputSchema, DocumentChunkSchema } from '@/ai/schemas';
import { queryVectorStoreTool } from '@/ai/tools/vector-store-tools';
import { logger } from '@/lib/logger';


export type AnswerGs1QuestionsWithVectorSearchInput = z.infer<typeof AnswerGs1QuestionsWithVectorSearchInputSchema>;


const CitedSourceSchema = z.object({
  sourceName: z.string().describe('The name or identifier of the cited source document.'),
  pageNumber: z.number().optional().describe('The page number in the cited source document.'),
  sectionTitle: z.string().optional().describe('The title of the section in the cited source document.'),
});

export const AnswerGs1QuestionsWithVectorSearchOutputSchema = z.object({
  answer: z.string().describe('The answer to the question, synthesized from retrieved document chunks.'),
  citedSources: z.array(CitedSourceSchema).optional().describe('A list of sources (document chunks) cited by the AI.'),
  reasoningSteps: z.array(z.string()).optional().describe('The steps the AI took to arrive at the answer.'),
  retrievedChunksCount: z.number().optional().describe('Number of chunks retrieved from the vector store.')
});
export type AnswerGs1QuestionsWithVectorSearchOutput = z.infer<typeof AnswerGs1QuestionsWithVectorSearchOutputSchema>;


const SynthesisPromptInputSchema = z.object({
  question: z.string(),
  documentChunks: z.array(DocumentChunkSchema),
});


export async function answerGs1QuestionsWithVectorSearch(
  input: AnswerGs1QuestionsWithVectorSearchInput
): Promise<AnswerGs1QuestionsWithVectorSearchOutput> {
  let retrievedChunksCount = 0;
  logger.info(`[FLOW_VECTOR_SEARCH] Received input: question="${input.question}"`);
  try {
    // Dynamically get model parameters for 'ask' mode, as this is a question-answering task
    const { model, thinkingBudget } = getModelParams('ask', {
      input_token_count: input.question.length, // Estimate token count
      task_intent: "quick lookups",
      complexity_flags: ["simple", "quick"]
    });

    // Step 1: Call the (mocked) vector store tool to retrieve document chunks.
    const toolInput = {
      query: input.question,
    };
    logger.info(`[FLOW_VECTOR_SEARCH] Calling queryVectorStoreTool with input: ${JSON.stringify(toolInput, null, 2)}`);
    const toolOutput = await queryVectorStoreTool(toolInput);

    if (!toolOutput || !toolOutput.results) {
        logger.error("[FLOW_VECTOR_SEARCH] queryVectorStoreTool did not return valid results.");
        return {
            answer: "Failed to retrieve information from the conceptual vector store. The tool did not provide valid results.",
            citedSources: [],
            reasoningSteps: ["Error querying the conceptual vector store: Tool returned invalid or no results."],
            retrievedChunksCount: 0,
        };
    }
    const retrievedDocumentChunks = toolOutput.results;
    retrievedChunksCount = retrievedDocumentChunks.length;
    logger.info(`[FLOW_VECTOR_SEARCH] queryVectorStoreTool returned ${retrievedChunksCount} chunk(s).`);
    if (retrievedChunksCount > 0) {
        logger.info('[FLOW_VECTOR_SEARCH] First retrieved chunk content (preview): ' + retrievedDocumentChunks[0].content.substring(0, 100) + '...');
    } else {
        logger.info('[FLOW_VECTOR_SEARCH] No chunks retrieved by queryVectorStoreTool.');
    }
    
    // Step 3: Synthesize an answer from the retrieved chunks using an LLM.
    const synthesisInput = {
      question: input.question,
      documentChunks: retrievedDocumentChunks,
    };
    logger.info(`[FLOW_VECTOR_SEARCH] Calling LLM for synthesis with ${retrievedDocumentChunks.length} chunks.`);

    const llmResponse = await ai.generate({
      model: model,
      prompt: `You are an AI assistant that answers questions about GS1 standards based *only* on the provided document content snippets.

Provided Document Chunks:
{{#if documentChunks.length}}
  {{#each documentChunks}}
  ---
  Source Document: "{{this.sourceName}}"
  {{#if this.pageNumber}}Page: {{this.pageNumber}}{{/if}}
  {{#if this.sectionTitle}}Section: "{{this.sectionTitle}}"{{/if}}

  Content Snippet:
  {{{this.content}}}
  ---
  {{/each}}
{{else}}
  (No document chunks were retrieved from the knowledge base.)
{{/if}}

User's Original Question: {{{question}}}

Based solely on the provided content snippets (if any), synthesize a comprehensive and accurate answer.
Consider the following to improve the answer for complex queries:
1.  **Multi-part Questions**: Break down the user's question into sub-questions if it has multiple parts and address each part using the provided chunks.
2.  **Nuanced Queries**: Pay close attention to subtle distinctions or specific conditions mentioned in the question and reflect them in the answer.
3.  **Synthesize from Multiple Chunks**: If information relevant to the answer is spread across several chunks, combine and synthesize it coherently. Avoid simply concatenating information.
4.  **Confidence Score (Implicit)**: If the information is sparse or contradictory, reflect this uncertainty in the answer (e.g., "Based on the available information, it appears...", "The document suggests...").

For your output:
1.  Provide a clear and concise 'answer' to the user's original 'question'.
2.  Populate the 'citedSources' field with details from *all* document chunks that contributed to your answer. If no chunks were used or available, this should be an empty array.
3.  Provide a detailed list of 'reasoningSteps' outlining your thought process, especially how you handled complex queries and synthesized information.
    If document chunks were used, steps should include:
      - "Analyzed user question: '{{{question}}}' for complexity and sub-parts."
      - "Identified X relevant document chunks from vector search."
      - "Strategically combined and synthesized information from chunk(s) [mention key sources if possible, e.g., from '{{documentChunks.0.sourceName}}' and '{{documentChunks.1.sourceName}}'] to formulate a comprehensive answer, addressing all nuances."
      - "Constructed final answer and identified all contributing cited sources."
    If no document chunks are available or used, steps should be like:
      - "Analyzed user question: '{{{question}}}'."
      - "Simulated query embedding generation for the question."
      - "Queried conceptual vector store with the embedding."
      - "Vector store returned no relevant document chunks."
      - "Unable to synthesize answer due to lack of relevant information from the knowledge base."

Begin.`,
       config: {
         maxOutputTokens: thinkingBudget === -1 ? undefined : thinkingBudget,
       },
       output: { schema: AnswerGs1QuestionsWithVectorSearchOutputSchema.omit({ retrievedChunksCount: true }) },
     });

     const synthesisOutput = llmResponse.output;

     if (!synthesisOutput) {
       logger.error('[FLOW_VECTOR_SEARCH] LLM synthesis did not return a valid output.');
       return {
         answer: "I encountered an issue generating an answer from the retrieved information. The AI model failed to produce a structured response during synthesis. Please try again.",
         citedSources: [],
         reasoningSteps: ["The AI model failed to produce a structured response during the synthesis stage."],
         retrievedChunksCount: retrievedChunksCount,
       };
     }
     
     logger.info(`[FLOW_VECTOR_SEARCH] Synthesis successful. Answer preview: ${synthesisOutput.answer.substring(0,100)}...`);
     return {
       ...synthesisOutput,
       retrievedChunksCount: retrievedChunksCount,
     };

   } catch (error: any) {
     logger.error({ err: error }, '[FLOW_VECTOR_SEARCH] Error in answerGs1QuestionsWithVectorSearch flow');
     return {
       answer: `An unexpected error occurred while processing your request with vector search: ${error.message || error}. Please check the input or try again later.`,
       citedSources: [],
       reasoningSteps: ["An unexpected error occurred in the RAG pipeline."],
       retrievedChunksCount: retrievedChunksCount,
     };
   }
 }
