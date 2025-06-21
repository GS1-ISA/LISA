import { ai } from '@/ai/genkit';
import { z } from 'zod';
import type { Tool } from 'genkit';
import { logger } from '@/lib/logger';
import { execa } from 'execa'; // Import execa for running external commands

export const queryVectorStoreTool = ai.defineTool(
  {
    name: 'queryVectorStore',
    description:
      'Queries a vector store with a natural language question to find relevant document chunks using the Python semantic search interface.',
    inputSchema: z.object({
      query: z.string().describe('The natural language question for the vector store.'),
    }),
    outputSchema: z.object({
      results: z.array(
        z.object({
          content: z.string(),
          sourceName: z.string().optional(), // Source name might not be available from Python mock
        })
      ),
    }),
  },
  async ({ query }: { query: string }) => {
    logger.info(`[TOOL_VECTOR_STORE] Calling Python semantic search with query: "${query}"`);
    try {
      // Execute the Python script
      const { stdout } = await execa('python', ['isa/core/run_semantic_search.py', query]);
      const output = JSON.parse(stdout);

      if (output.error) {
        logger.error(`[TOOL_VECTOR_STORE] Python script error: ${output.error}`);
        return { results: [] };
      }

      // The Python script returns a list of strings, so we map them to the expected DocumentChunk format.
      // For now, sourceName is omitted as the mock Python script doesn't provide it.
      const results = output.results.map((chunkContent: string) => ({
        content: chunkContent,
        sourceName: 'Indexed Project Knowledge', // Default source name
      }));

      logger.info(`[TOOL_VECTOR_STORE] Python script returned ${results.length} results.`);
      return { results };
    } catch (error: any) {
      logger.error({ err: error }, '[TOOL_VECTOR_STORE] Error executing Python semantic search script.');
      return { results: [] };
    }
  }
);

export const vectorStoreTools: Tool[] = [queryVectorStoreTool];
