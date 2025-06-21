// src/ai/schemas.ts
import { z } from 'zod';

// Schemas previously defined in src/ai/flows/analyze-standards.ts
export const AnalyzeStandardsInputSchema = z.object({
  documentContent: z
    .string()
    .describe('The content of the standards document to analyze.'),
});

// Schemas previously defined in src/ai/flows/answer-gs1-questions.ts
export const AnswerGs1QuestionsInputSchema = z.object({
  question: z.string().describe('The question about the GS1 standards document.'),
  documentContent: z.string().describe('The content of the GS1 standards document.'),
});

// Schemas previously defined in src/ai/flows/conduct-independent-research.ts
export const ConductIndependentResearchInputSchema = z.object({
  topic: z.string().describe('The topic for independent research.'),
  researchQuestion: z
    .string()
    .optional()
    .describe('Optional initial research question to guide the research.'),
});

// Schemas previously defined in src/ai/flows/natural-language-to-formal-description.ts
export const NaturalLanguageToFormalDescriptionInputSchema = z.object({
  naturalLanguageDescription: z
    .string()
    .describe('A natural language description of a standard.'),
});
