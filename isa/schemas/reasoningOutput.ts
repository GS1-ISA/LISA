import { z } from 'zod';

export const ReasoningOutputSchema = z.object({
  agent: z.string(),
  decision: z.enum(['pass', 'fail', 'warn']),
  explanation: z.string(),
  evidence: z.array(z.string()),
  confidence: z.number().min(0).max(1),
});

export type ReasoningOutput = z.infer<typeof ReasoningOutputSchema>;
