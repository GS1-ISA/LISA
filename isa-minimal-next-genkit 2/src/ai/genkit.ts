import { defineFlow } from 'genkit';
import { z } from 'zod';
import { generate } from '@genkit-ai/googleai';

export const helloISA = defineFlow(
  { name: "helloISA", inputSchema: z.string(), outputSchema: z.string() },
  async (name) => {
    const response = await generate({
      model: process.env.GEMINI_MODEL_OVERRIDE || "googleai/gemini-2.0-flash",
      prompt: `Say hello to ${name}`,
    });
    return response.text();
  }
);
