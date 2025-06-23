// src/ai/flows/answer-gs1-questions.ts
'use server';

/**
 * @fileOverview An AI agent that answers questions about GS1 standards documents.
 *
 * - answerGs1Questions - A function that answers questions about GS1 standards documents.
 * - AnswerGs1QuestionsInput - The input type for the answerGs1Questions function.
 * - AnswerGs1QuestionsOutput - The return type for the answerGs1Questions function.
 */

import {ai, getModelParams} from '@/ai/genkit';
import {z} from 'genkit';
import { AnswerGs1QuestionsInputSchema } from '@/ai/schemas'; // Import schema object

// Type export remains, Zod object definition removed from here
export type AnswerGs1QuestionsInput = z.infer<typeof AnswerGs1QuestionsInputSchema>;

const AnswerGs1QuestionsOutputSchema = z.object({
  answer: z.string().describe('The answer to the question about the GS1 standards document.'),
});
export type AnswerGs1QuestionsOutput = z.infer<typeof AnswerGs1QuestionsOutputSchema>;

export async function answerGs1Questions(input: AnswerGs1QuestionsInput): Promise<AnswerGs1QuestionsOutput> {
  return answerGs1QuestionsFlow(input);
}

const answerGs1QuestionsFlow = ai.defineFlow(
  {
    name: 'answerGs1QuestionsFlow',
    inputSchema: AnswerGs1QuestionsInputSchema, // Use imported schema object
    outputSchema: AnswerGs1QuestionsOutputSchema,
  },
  async input => {
    // Dynamically get model parameters for 'ask' mode
    const { model, thinkingBudget } = getModelParams('ask', {
      input_token_count: input.question.length + input.documentContent.length, // Estimate token count
      task_intent: "quick lookups",
      complexity_flags: ["simple", "quick"]
    });

    const thoughtProcessResponse = await ai.generate({
      model: model,
      prompt: `You are an AI assistant that helps in breaking down complex questions about GS1 standards documents.
      
      Given a question and a document, your task is to outline a step-by-step thought process to arrive at the answer.
      This thought process should guide the main AI in answering the question accurately based on the provided document.
      
      Question: {{{question}}}
      Document Content: {{{documentContent}}}
      
      Thought Process:`,
      config: {
        maxOutputTokens: thinkingBudget === -1 ? undefined : thinkingBudget,
      },
      output: { schema: z.object({ thoughtProcess: z.string() }) },
    });

    const thoughtProcess = thoughtProcessResponse.output.thoughtProcess;

    const initialAnswerResponse = await ai.generate({
      model: model,
      prompt: `You are an AI assistant that answers questions about GS1 standards documents.
      
      You will be provided with a question, the content of a GS1 standards document, and a thought process to guide your answer.
      Your task is to answer the question based on the information in the document, following the thought process.
      
      Question: {{{question}}}
      Document Content: {{{documentContent}}}
      Thought Process: {{{thoughtProcess}}}
      
      Answer:`,
      config: {
        maxOutputTokens: thinkingBudget === -1 ? undefined : thinkingBudget,
      },
      output: { schema: AnswerGs1QuestionsOutputSchema },
    });

    const initialAnswer = initialAnswerResponse.output.answer;

    const refinedAnswerResponse = await ai.generate({
      model: model,
      prompt: `You are an AI assistant that refines answers to questions about GS1 standards documents.
      
      You will be provided with the original question, the document content, the thought process used, and an initial answer.
      Your task is to review the initial answer, self-reflect on its accuracy and completeness based on the document and thought process, and then provide a refined answer. If the initial answer is already perfect, simply return it as is.
      
      Question: {{{question}}}
      Document Content: {{{documentContent}}}
      Thought Process: {{{thoughtProcess}}}
      Initial Answer: {{{initialAnswer}}}
      
      Refined Answer:`,
      config: {
        maxOutputTokens: thinkingBudget === -1 ? undefined : thinkingBudget,
      },
      output: { schema: AnswerGs1QuestionsOutputSchema },
    });

    return refinedAnswerResponse.output!;
  }
);
