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

Please identify the following types of issues:
- **Inconsistencies**: Contradictory statements or requirements.
- **Overlapping Definitions**: Terms defined multiple times with potentially conflicting meanings.
- **Ambiguities**: Phrases or statements open to multiple interpretations.
- **Formatting Issues**: Problems with document structure, numbering, or presentation that could lead to misinterpretation.
- **Grammatical Errors**: Significant grammatical mistakes that affect clarity.
- **Logical Flaws**: Issues in the reasoning or flow of requirements.

For each issue identified, provide:
1.  A clear 'description' of the problem.
2.  A 'locationContext' (a short snippet from the text where the issue occurs, if applicable and helpful for pinpointing).
3.  A 'suggestedCorrection' if a clear and concise correction can be proposed.
4.  An 'errorType' categorizing the issue (e.g., "Inconsistency", "Overlapping Definition", "Ambiguity", "Formatting Issue", "Grammatical Error", "Logical Flaw").

Finally, provide a brief 'summary' of your overall findings, noting the quantity and severity of issues found.

Structure your output according to the provided JSON schema. Focus on actionable and clear feedback.
`,
      config: {
        maxOutputTokens: thinkingBudget === -1 ? undefined : thinkingBudget,
      },
      output: { schema: DetectStandardErrorsOutputSchema },
    });
    return llmResponse.output!;
  }
);
