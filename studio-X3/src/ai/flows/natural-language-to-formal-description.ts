'use server';

/**
 * @fileOverview Transforms natural language descriptions of standards into formal standard descriptions.
 *
 * - naturalLanguageToFormalDescription - A function that transforms natural language into formal descriptions.
 * - NaturalLanguageToFormalDescriptionInput - The input type for the naturalLanguageToFormalDescription function.
 * - NaturalLanguageToFormalDescriptionOutput - The return type for the naturalLanguageToFormalDescription function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';
import { NaturalLanguageToFormalDescriptionInputSchema } from '@/ai/schemas'; // Import schema object

// Type export remains, Zod object definition removed from here
export type NaturalLanguageToFormalDescriptionInput = z.infer<
  typeof NaturalLanguageToFormalDescriptionInputSchema
>;

const FormalStandardDescriptionSchema = z.object({
  formalDescription: z
    .string()
    .describe('A formal description of the standard.'),
});

const NaturalLanguageToFormalDescriptionOutputSchema = z.object({
  formalStandardDescription: FormalStandardDescriptionSchema.describe(
    'The formal standard description generated from the natural language input.'
  ),
});
export type NaturalLanguageToFormalDescriptionOutput = z.infer<
  typeof NaturalLanguageToFormalDescriptionOutputSchema
>;

export async function naturalLanguageToFormalDescription(
  input: NaturalLanguageToFormalDescriptionInput
): Promise<NaturalLanguageToFormalDescriptionOutput> {
  return naturalLanguageToFormalDescriptionFlow(input);
}

const prompt = ai.definePrompt({
  name: 'naturalLanguageToFormalDescriptionPrompt',
  input: {
    schema: NaturalLanguageToFormalDescriptionInputSchema, // Use imported schema object
  },
  output: {
    schema: NaturalLanguageToFormalDescriptionOutputSchema,
  },
  prompt: `You are an expert in transforming natural language descriptions of standards into formal standard descriptions.

  Given the following natural language description, create a formal standard description.
  Natural Language Description: {{{naturalLanguageDescription}}}

  Follow these guidelines when creating the formal standard description:
  - Be precise and unambiguous.
  - Use formal language.
  - Ensure the description is complete and self-contained.
  - Focus on the key requirements and specifications.
  - Use correct grammar and punctuation.
  - Use appropriate terminology for standards documents.
  - Omit conversational language.
  `,
});

const naturalLanguageToFormalDescriptionFlow = ai.defineFlow(
  {
    name: 'naturalLanguageToFormalDescriptionFlow',
    inputSchema: NaturalLanguageToFormalDescriptionInputSchema, // Use imported schema object
    outputSchema: NaturalLanguageToFormalDescriptionOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
