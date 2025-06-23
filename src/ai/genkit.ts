import { genkit } from 'genkit';
import { googleAI } from '@genkit-ai/googleai';
import { execSync } from 'child_process';
import path from 'path';
import { queryKnowledgeGraphTool } from './tools/knowledge-graph-tools';

/**
 * Function to get model parameters from the Python ModelManager.
 * This function should be called dynamically before each LLM API call
 * to ensure the correct model and thinkingBudget are applied based on
 * the current mode and task context.
 * @param modeSlug The slug of the current operational mode (e.g., 'code', 'architect').
 * @param promptContext An object containing context for dynamic model selection,
 *                      e.g., { input_token_count: number, task_intent: string, complexity_flags: string[] }.
 * @returns An object containing the selected model name and thinkingBudget.
 */
export function getModelParams(modeSlug: string, promptContext: any = {}): { model: string; thinkingBudget: number } {
  try {
    const scriptPath = path.resolve(__dirname, '../../isa/core/model_manager.py');
    // Ensure the promptContext is properly escaped for shell execution
    const contextString = JSON.stringify(promptContext).replace(/'/g, "\\'");
    const command = `python3 ${scriptPath} "${modeSlug}" '${contextString}'`;
    const output = execSync(command).toString();
    return JSON.parse(output);
  } catch (error: any) {
    console.error(`Error calling ModelManager: ${error.message}`);
    // Fallback to default values in case of an error
    return { model: 'gemini-2.5-flash', thinkingBudget: 5000 };
  }
}

// Initialize Genkit with the Google AI plugin.
// Model and thinkingBudget will be dynamically determined at the call site
// using the getModelParams function and passed directly to model.generate() or model.streamGenerate().
export const ai = genkit({
  plugins: [
    googleAI(), // Initialize without specific model/maxOutputTokens here
  ],
});

// Register the new tool
genkit.addTool(queryKnowledgeGraphTool);

/*
// Example of how to use getModelParams in a Genkit flow:
import { defineFlow, generate } from 'genkit';

export const myDynamicFlow = defineFlow(
  {
    name: 'myDynamicFlow',
    inputSchema: z.object({
      mode: z.string(),
      prompt: z.string(),
      context: z.any().optional(),
    }),
    outputSchema: z.string(),
  },
  async (input) => {
    const { model, thinkingBudget } = getModelParams(input.mode, input.context);

    const llmResponse = await generate({
      model: model, // Use the dynamically selected model
      prompt: input.prompt,
      config: {
        maxOutputTokens: thinkingBudget === -1 ? undefined : thinkingBudget, // Apply thinkingBudget
      },
    });

    return llmResponse.text();
  }
);
*/
