import { ai, getModelParams } from '@/ai/genkit';
import { z } from 'genkit';
import { logger } from '@/lib/logger';
import { ContentSummarizationTool } from '@/ai/tools/content-summarization-tool';
import { DataExtractionTransformationTool } from '@/ai/tools/data-extraction-transformation-tool';

/**
 * @fileOverview An AI flow for automated report generation.
 * This flow demonstrates how to combine multiple AI tools (summarization, data extraction)
 * to create a structured report from various inputs.
 */

// Input schema for the automated report generation flow
const AutomatedReportGenerationInputSchema = z.object({
  reportTitle: z.string().describe('The title of the report.'),
  sourceTexts: z.array(z.string()).describe('An array of text contents to be included and summarized in the report.'),
  dataToExtract: z.string().optional().describe('A description or schema for structured data to extract from the source texts.'),
});
export type AutomatedReportGenerationInput = z.infer<typeof AutomatedReportGenerationInputSchema>;

// Output schema for the automated report generation flow
const AutomatedReportGenerationOutputSchema = z.object({
  generatedReport: z.string().describe('The complete generated report in markdown format.'),
  summaries: z.array(z.string()).describe('Individual summaries of each source text.'),
  extractedData: z.any().optional().describe('Structured data extracted from the source texts, if requested.'),
  reportGenerationSteps: z.array(z.string()).describe('Steps taken to generate the report.'),
});
export type AutomatedReportGenerationOutput = z.infer<typeof AutomatedReportGenerationOutputSchema>;

export async function automatedReportGeneration(
  input: AutomatedReportGenerationInput
): Promise<AutomatedReportGenerationOutput> {
  return automatedReportGenerationFlow(input);
}

const automatedReportGenerationFlow = ai.defineFlow(
  {
    name: 'automatedReportGenerationFlow',
    inputSchema: AutomatedReportGenerationInputSchema,
    outputSchema: AutomatedReportGenerationOutputSchema,
  },
  async (input) => {
    logger.info(`[FLOW_REPORT_GEN] Starting automated report generation for: "${input.reportTitle}"`);

    const reportGenerationSteps: string[] = [];
    const summaries: string[] = [];
    let extractedData: any = null;

    // Dynamically get model parameters for 'code' mode, as this involves content generation
    const { model, thinkingBudget } = getModelParams('code', {
      input_token_count: input.reportTitle.length + input.sourceTexts.join('').length,
      task_intent: "content generation",
      complexity_flags: ["complex content generation", "multi-tool orchestration"]
    });

    reportGenerationSteps.push('Initialized report generation process.');

    // Step 1: Summarize each source text
    const summarizationTool = new ContentSummarizationTool();
    for (const text of input.sourceTexts) {
      logger.info(`[FLOW_REPORT_GEN] Summarizing a source text (length: ${text.length})...`);
      const { summary } = await summarizationTool.summarize({ text });
      summaries.push(summary);
      reportGenerationSteps.push(`Summarized a source text. Summary length: ${summary.length}.`);
    }

    // Step 2: Extract and transform data if requested
    if (input.dataToExtract) {
      const dataExtractionTool = new DataExtractionTransformationTool();
      logger.info(`[FLOW_REPORT_GEN] Extracting data based on schema: "${input.dataToExtract}"`);
      const { extractedData: extracted } = await dataExtractionTool.extractAndTransform({
        text: input.sourceTexts.join('\n\n'), // Combine all texts for extraction
        schema: input.dataToExtract,
      });
      extractedData = extracted;
      reportGenerationSteps.push(`Extracted structured data from source texts.`);
    }

    // Step 3: Generate the final report using an LLM
    logger.info('[FLOW_REPORT_GEN] Generating final report with LLM...');
    const llmResponse = await ai.generate({
      model: model,
      prompt: `You are an expert report writer. Your task is to generate a comprehensive report based on the provided summaries and extracted data.

Report Title: ${input.reportTitle}

Summaries of Source Texts:
${summaries.map((s, i) => `### Summary ${i + 1}\n${s}`).join('\n\n')}

${extractedData ? `Extracted Data:\n\`\`\`json\n${JSON.stringify(extractedData, null, 2)}\n\`\`\`\n` : ''}

Instructions:
1.  Write a well-structured report in markdown format.
2.  Start with an introduction, followed by sections for each summarized text (or a combined analysis if appropriate).
3.  Integrate the extracted data naturally into the report, providing analysis or context as needed.
4.  Conclude with a summary or key findings.
5.  Ensure the report is coherent, professional, and directly addresses the purpose implied by the title and content.
6.  Do NOT include any introductory or concluding remarks outside the markdown report itself. The entire output should be the markdown report.
`,
      config: {
        maxOutputTokens: thinkingBudget === -1 ? undefined : thinkingBudget,
      },
      output: { schema: z.object({ generatedReport: z.string() }) }, // Only expect the report string from LLM
    });

    const generatedReport = llmResponse.output!.generatedReport;
    reportGenerationSteps.push('Generated final report using LLM.');
    logger.info(`[FLOW_REPORT_GEN] Report generation complete. Report length: ${generatedReport.length}`);

    return {
      generatedReport,
      summaries,
      extractedData,
      reportGenerationSteps,
    };
  }
);