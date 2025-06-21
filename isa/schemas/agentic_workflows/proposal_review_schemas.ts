import { z } from 'zod';

// 1. Genkit Tool Input/Output Schemas

// ingestDocumentTool
export const IngestDocumentInputSchema = z.object({
  documentPath: z.string().describe('Path or URL to the raw proposal document.'),
});
export const IngestDocumentOutputSchema = z.object({
  parsedContent: z.string().describe('Extracted and parsed text content of the document.'),
  metadata: z.record(z.any()).optional().describe('Extracted metadata from the document.'),
});

// knowledgeGraphRetriever
export const KnowledgeGraphRetrieverInputSchema = z.object({
  query: z.string().describe('Natural language query or TypeQL query for the Knowledge Graph.'),
  concepts: z.array(z.string()).optional().describe('Key concepts or entities to retrieve context for.'),
});
export const KnowledgeGraphRetrieverOutputSchema = z.object({
  structuredData: z.record(z.any()).describe('Structured data (entities, relationships, rules) from the Knowledge Graph.'),
  citations: z.array(z.string()).optional().describe('List of sources/citations from the KG.'),
});

// vectorSearchRetriever
export const VectorSearchRetrieverInputSchema = z.object({
  query: z.string().describe('Semantic query for the Vector Database.'),
  topK: z.number().int().positive().default(5).describe('Number of top relevant results to retrieve.'),
});
export const VectorSearchRetrieverOutputSchema = z.object({
  relevantChunks: z.array(z.object({
    content: z.string(),
    source: z.string().optional(),
    score: z.number().optional(),
  })).describe('Array of relevant text chunks from the Vector Database.'),
});

// genSpecValidator
export const GenSpecValidatorInputSchema = z.object({
  proposalContent: z.string().describe('Content of the standard proposal to validate.'),
  kgContext: KnowledgeGraphRetrieverOutputSchema.shape.structuredData.optional().describe('Structured context from the Knowledge Graph.'),
  vectorContext: VectorSearchRetrieverOutputSchema.shape.relevantChunks.optional().describe('Relevant text chunks from vector search.'),
});
export const GenSpecValidatorOutputSchema = z.object({
  isValid: z.boolean().describe('True if the proposal is valid, false otherwise.'),
  errors: z.array(z.string()).optional().describe('List of validation errors.'),
  conflicts: z.array(z.string()).optional().describe('List of identified conflicts with existing standards.'),
  recommendations: z.array(z.string()).optional().describe('Suggestions for resolving issues.'),
});

// impactAnalyzer
export const ImpactAnalyzerInputSchema = z.object({
  proposalContent: z.string().describe('Content of the standard proposal.'),
  validationResults: GenSpecValidatorOutputSchema.optional().describe('Results from the validation step.'),
  kgContext: KnowledgeGraphRetrieverOutputSchema.shape.structuredData.optional().describe('Structured context from the Knowledge Graph.'),
});
export const ImpactAnalyzerOutputSchema = z.object({
  riskLevel: z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']).describe('Assessed risk level of the proposal.'),
  affectedStandards: z.array(z.string()).describe('List of existing standards potentially affected.'),
  implications: z.string().describe('Detailed explanation of the implications and potential downstream effects.'),
  suggestedMitigations: z.array(z.string()).optional().describe('Suggested actions to mitigate risks.'),
});

// reportDrafter
export const ReportDrafterInputSchema = z.object({
  proposalContent: z.string().describe('Content of the standard proposal.'),
  validationResults: GenSpecValidatorOutputSchema.optional().describe('Results from the validation step.'),
  impactAnalysisResults: ImpactAnalyzerOutputSchema.optional().describe('Results from the impact analysis step.'),
  humanFeedback: z.record(z.any()).optional().describe('Optional human feedback for report refinement.'),
});
export const ReportDrafterOutputSchema = z.object({
  draftReport: z.string().describe('Generated draft impact report in markdown format.'),
  reasoningTrace: z.string().optional().describe('Chain-of-Thought reasoning trace for report generation.'),
});

// humanFeedbackRequester
export const HumanFeedbackRequesterInputSchema = z.object({
  proposalSummary: z.string().describe('Summary of the proposal.'),
  draftReport: z.string().describe('Draft report requiring human review.'),
  identifiedIssues: z.array(z.string()).optional().describe('Issues identified for human clarification.'),
});
export const HumanFeedbackRequesterOutputSchema = z.object({
  approval: z.boolean().describe('True if the human approves, false otherwise.'),
  clarification: z.string().optional().describe('Optional clarification or revision notes from human.'),
});


// 2. LangGraph State Definition
export const ProposalReviewStateSchema = z.object({
  proposalId: z.string().describe('Unique identifier for the proposal.'),
  rawProposalContent: z.string().describe('Raw content of the proposal.'),
  parsedContent: z.string().optional().describe('Extracted and parsed text content.'),
  retrievedKgContext: KnowledgeGraphRetrieverOutputSchema.shape.structuredData.optional().describe('Structured context from the Knowledge Graph.'),
  retrievedVectorContext: VectorSearchRetrieverOutputSchema.shape.relevantChunks.optional().describe('Relevant text chunks from vector search.'),
  validationResults: GenSpecValidatorOutputSchema.optional().describe('Results from the validation step.'),
  impactAnalysisResults: ImpactAnalyzerOutputSchema.optional().describe('Results from the impact analysis step.'),
  draftReport: z.string().optional().describe('Generated draft impact report.'),
  humanFeedback: HumanFeedbackRequesterOutputSchema.optional().describe('Human feedback received.'),
  finalReport: z.string().optional().describe('Finalized impact report.'),
  status: z.enum([
    "INGESTED",
    "RETRIEVING_CONTEXT",
    "VALIDATING",
    "ANALYZING_IMPACT",
    "GENERATING_REPORT",
    "AWAITING_HUMAN_FEEDBACK",
    "COMPLETED",
    "FAILED"
  ]).describe('Current status of the workflow.'),
  errorMessage: z.string().optional().describe('Error message if the workflow failed.'),
});

export type IngestDocumentInput = z.infer<typeof IngestDocumentInputSchema>;
export type IngestDocumentOutput = z.infer<typeof IngestDocumentOutputSchema>;
export type KnowledgeGraphRetrieverInput = z.infer<typeof KnowledgeGraphRetrieverInputSchema>;
export type KnowledgeGraphRetrieverOutput = z.infer<typeof KnowledgeGraphRetrieverOutputSchema>;
export type VectorSearchRetrieverInput = z.infer<typeof VectorSearchRetrieverInputSchema>;
export type VectorSearchRetrieverOutput = z.infer<typeof VectorSearchRetrieverOutputSchema>;
export type GenSpecValidatorInput = z.infer<typeof GenSpecValidatorInputSchema>;
export type GenSpecValidatorOutput = z.infer<typeof GenSpecValidatorOutputSchema>;
export type ImpactAnalyzerInput = z.infer<typeof ImpactAnalyzerInputSchema>;
export type ImpactAnalyzerOutput = z.infer<typeof ImpactAnalyzerOutputSchema>;
export type ReportDrafterInput = z.infer<typeof ReportDrafterInputSchema>;
export type ReportDrafterOutput = z.infer<typeof ReportDrafterOutputSchema>;
export type HumanFeedbackRequesterInput = z.infer<typeof HumanFeedbackRequesterInputSchema>;
export type HumanFeedbackRequesterOutput = z.infer<typeof HumanFeedbackRequesterOutputSchema>;
export type ProposalReviewState = z.infer<typeof ProposalReviewStateSchema>;