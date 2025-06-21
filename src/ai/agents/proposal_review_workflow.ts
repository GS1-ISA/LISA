import { Graph, StateGraph } from '@langchain/langgraph';
import { BaseMessage } from '@langchain/core/messages';
import {
  ProposalReviewState,
  IngestDocumentInput,
  KnowledgeGraphRetrieverInput,
  VectorSearchRetrieverInput,
  GenSpecValidatorInput,
  ImpactAnalyzerInput,
  ReportDrafterInput,
  HumanFeedbackRequesterInput,
} from '@isa-schemas/agentic_workflows/proposal_review_schemas';
import {
  ingestDocumentTool,
  knowledgeGraphRetriever,
  vectorSearchRetriever,
  genSpecValidator,
  impactAnalyzer,
  reportDrafter,
  humanFeedbackRequester,
} from '../tools/agentic_workflows/proposal_review_tools';

// Define the state for the LangGraph
const workflowState: ProposalReviewState = {
  proposalId: '',
  rawProposalContent: '',
  status: 'INGESTED',
};

// Define the nodes for the graph
const nodes = {
  ingest: async (state: ProposalReviewState) => {
    const input: IngestDocumentInput = { documentPath: state.rawProposalContent };
    // Directly call the handler function of the Genkit tool
    const result = await ingestDocumentTool.handler(input);
    return { ...state, parsedContent: result.parsedContent, status: 'RETRIEVING_CONTEXT' };
  },
  retrieveContext: async (state: ProposalReviewState) => {
    const kgInput: KnowledgeGraphRetrieverInput = { query: state.parsedContent || '', concepts: [] };
    // Directly call the handler function of the Genkit tool
    const kgResult = await knowledgeGraphRetriever.handler(kgInput);

    const vectorInput: VectorSearchRetrieverInput = { query: state.parsedContent || '', topK: 5 };
    // Directly call the handler function of the Genkit tool
    const vectorResult = await vectorSearchRetriever.handler(vectorInput);

    return {
      ...state,
      retrievedKgContext: kgResult.structuredData,
      retrievedVectorContext: vectorResult.relevantChunks,
      status: 'VALIDATING',
    };
  },
  validateProposal: async (state: ProposalReviewState) => {
    const input: GenSpecValidatorInput = {
      proposalContent: state.parsedContent || '',
      kgContext: state.retrievedKgContext,
      vectorContext: state.retrievedVectorContext,
    };
    // Directly call the handler function of the Genkit tool
    const result = await genSpecValidator.handler(input);
    return { ...state, validationResults: result, status: 'ANALYZING_IMPACT' };
  },
  analyzeImpact: async (state: ProposalReviewState) => {
    const input: ImpactAnalyzerInput = {
      proposalContent: state.parsedContent || '',
      validationResults: state.validationResults,
      kgContext: state.retrievedKgContext,
    };
    // Directly call the handler function of the Genkit tool
    const result = await impactAnalyzer.handler(input);
    return { ...state, impactAnalysisResults: result, status: 'GENERATING_REPORT' };
  },
  generateDraftReport: async (state: ProposalReviewState) => {
    const input: ReportDrafterInput = {
      proposalContent: state.parsedContent || '',
      validationResults: state.validationResults,
      impactAnalysisResults: state.impactAnalysisResults,
      humanFeedback: state.humanFeedback, // Pass human feedback for re-drafting
    };
    // Directly call the handler function of the Genkit tool
    const result = await reportDrafter.handler(input);
    return { ...state, draftReport: result.draftReport, status: 'AWAITING_HUMAN_FEEDBACK' };
  },
  requestHumanFeedback: async (state: ProposalReviewState) => {
    const input: HumanFeedbackRequesterInput = {
      proposalSummary: state.parsedContent?.substring(0, 100) || '',
      draftReport: state.draftReport || '',
      identifiedIssues: state.validationResults?.errors || [],
    };
    // In a real scenario, this tool would trigger an external notification
    // and the workflow would pause until external human input updates the state.
    // For this simulation, we'll directly invoke it and get a mock response.
    const result = await humanFeedbackRequester.handler(input);
    return { ...state, humanFeedback: result, status: 'GENERATING_REPORT' }; // Loop back to generate report after feedback
  },
  finalizeReport: async (state: ProposalReviewState) => {
    // This node simply marks the report as final.
    return { ...state, finalReport: state.draftReport, status: 'COMPLETED' };
  },
};

// Define the conditional edges
const conditionalEdges = {
  // After validation, decide whether to analyze impact or request human feedback
  afterValidate: (state: ProposalReviewState) => {
    if (state.validationResults && (!state.validationResults.isValid || state.validationResults.conflicts?.length > 0)) {
      return 'requestHumanFeedback';
    }
    return 'analyzeImpact';
  },
  // After generating a draft, decide whether to finalize or request more human feedback
  afterGenerateDraft: (state: ProposalReviewState) => {
    if (state.humanFeedback && !state.humanFeedback.approval) {
      return 'requestHumanFeedback'; // Loop back for revisions
    }
    return 'finalizeReport';
  },
};

// Build the graph
export const proposalReviewGraph = new StateGraph({
  nodes,
  edges: [
    ['ingest', 'retrieveContext'],
    ['retrieveContext', 'validateProposal'],
    ['analyzeImpact', 'generateDraftReport'],
    ['finalizeReport', Graph.END], // End the workflow
  ],
  conditionalEdges: {
    validateProposal: conditionalEdges.afterValidate,
    generateDraftReport: conditionalEdges.afterGenerateDraft,
  },
  entryPoint: 'ingest',
});

// Example of how to run the graph (for testing/demonstration)
/*
async function runProposalReview(proposalContent: string) {
  const initialInput: ProposalReviewState = {
    proposalId: `prop-${Date.now()}`,
    rawProposalContent: proposalContent,
    status: 'INGESTED',
  };

  let currentState = initialInput;
  for await (const snapshot of proposalReviewGraph.stream(initialInput)) {
    currentState = snapshot.values;
    console.log('Current State:', currentState.status);
    if (currentState.status === 'COMPLETED' || currentState.status === 'FAILED') {
      break;
    }
  }
  console.log('Final State:', currentState);
  return currentState;
}

// To run:
// runProposalReview("This is a new proposal with some ambiguous language.");
*/