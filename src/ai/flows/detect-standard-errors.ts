// src/ai/flows/detect-standard-errors.ts
'use server';

/**
 * @fileOverview Detects errors, inconsistencies, and overlapping definitions in standards documents.
 *
 * - detectStandardErrors - A function that analyzes a standards document for errors.
 * - DetectStandardErrorsInput - The input type for the detectStandardErrors function.
 * - DetectStandardErrorsOutput - The return type for the detectStandardErrors function.
 */

import {ai, getModelParams} from '@/ai/genkit';
import {z} from 'genkit';
import { DetectStandardErrorsInputSchema } from '@/ai/schemas';

export type DetectStandardErrorsInput = z.infer<typeof DetectStandardErrorsInputSchema>;

const DetectedErrorSchema = z.object({
  description: z
    .string()
    .describe('Detailed description of the detected error, inconsistency, or overlapping definition.'),
  locationContext: z
    .string()
    .optional()
    .describe('A snippet of text from the document showing the context or location of the error.'),
  suggestedCorrection: z
    .string()
    .optional()
    .describe('A suggested correction or way to resolve the identified issue.'),
  errorType: z
    .string()
    .describe('Category of the error (e.g., "Inconsistency", "Overlapping Definition", "Ambiguity", "Formatting Issue", "Grammatical Error", "Logical Flaw").'),
});

const DetectStandardErrorsOutputSchema = z.object({
  detectedIssues: z
    .array(DetectedErrorSchema)
    .describe('A list of detected errors, inconsistencies, or overlapping definitions found in the document.'),
  summary: z
    .string()
    .describe('A concise summary of the error detection findings, highlighting the most critical issues if any.'),
});
export type DetectStandardErrorsOutput = z.infer<typeof DetectStandardErrorsOutputSchema>;

export async function detectStandardErrors(input: DetectStandardErrorsInput): Promise<DetectStandardErrorsOutput> {
  return detectStandardErrorsFlow(input);
}

const detectStandardErrorsFlow = ai.defineFlow(
  {
    name: 'detectStandardErrorsFlow',
    inputSchema: DetectStandardErrorsInputSchema,
    outputSchema: DetectStandardErrorsOutputSchema,
  },
  async input => {
    // Dynamically get model parameters for 'debug' mode
    const { model, thinkingBudget } = getModelParams('debug', {
      input_token_count: input.documentContent.length, // Estimate token count
      task_intent: "error investigation",
      complexity_flags: ["complex problem diagnosis", "error investigation", "root cause analysis"]
    });

    const llmResponse = await ai.generate({
      model: model,
      prompt: `You are an expert standards auditor with a keen eye for detail. Your task is to meticulously analyze the provided standards document content to identify and report errors, inconsistencies, ambiguities, and overlapping definitions.

Document Content:
\`\`\`
{{{documentContent}}}
\`\`\`

Please identify the following types of issues, providing detailed and actionable feedback for each:
- **Inconsistencies**: Contradictory statements, conflicting requirements, or logical breaks within the document. Provide specific examples.
- **Overlapping Definitions**: Terms or concepts defined redundantly or with subtle, confusing differences. Suggest a unified definition.
- **Ambiguities**: Vague language, unclear phrasing, or statements that can be interpreted in multiple ways. Propose clearer wording.
- **Completeness Gaps**: Missing information, undefined terms, or unaddressed scenarios that should be covered by the standard.
- **Structural/Formatting Issues**: Problems with document organization, inconsistent numbering, incorrect cross-references, or presentation errors that hinder readability or understanding.
- **Grammatical/Typographical Errors**: Significant language errors that impact the professional appearance or clarity of the document.

For each issue identified, provide:
1.  A clear and comprehensive 'description' of the problem, explaining its impact.
2.  A 'locationContext' (a precise snippet of text from the document where the issue occurs, including surrounding sentences for full context).
3.  A 'suggestedCorrection' that is specific, practical, and directly addresses the identified issue.
4.  An 'errorType' categorizing the issue (e.g., "Inconsistency", "Overlapping Definition", "Ambiguity", "Completeness Gap", "Structural Issue", "Grammatical Error").

Finally, provide a brief 'summary' of your overall findings, including the total number of issues found, a breakdown by 'errorType', and a prioritization of the most critical issues.

Structure your output strictly according to the provided JSON schema. Ensure all fields are populated where applicable.
`,
       config: {
         maxOutputTokens: thinkingBudget === -1 ? undefined : thinkingBudget,
       },
       output: { schema: DetectStandardErrorsOutputSchema },
     });
     return llmResponse.output!;
   }
 );
