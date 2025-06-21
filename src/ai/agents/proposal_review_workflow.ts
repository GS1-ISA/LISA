import {
  StateGraph,
  Annotation,
  START,
  END,
} from "@langchain/langgraph";
import {
  AIMessage,
  BaseMessage,
  HumanMessage,
} from "@langchain/core/messages";
import {
  IngestDocumentInput,
  KnowledgeGraphRetrieverInput,
  VectorSearchRetrieverInput,
  GenSpecValidatorInput,
  ImpactAnalyzerInput,
  ReportDrafterInput,
  HumanFeedbackRequesterInput,
  ToolAction,
  VectorSearchRetrieverOutput, // Added import
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
import { ai } from '../genkit'; // Corrected import path

// Define the structure of your custom state using Annotation.Root
export const ProposalReviewState = Annotation.Root({
  proposalId: Annotation<string>(),
  rawProposalContent: Annotation<string>(),
  status: Annotation<
    'INGESTED' | 'RETRIEVING_CONTEXT' | 'VALIDATING' | 'ANALYZING_IMPACT' | 'GENERATING_REPORT' | 'AWAITING_HUMAN_FEEDBACK' | 'COMPLETED' | 'FAILED'
  >(),
  parsedContent: Annotation<string | undefined>(),
  retrievedKgContext: Annotation<Record<string, any> | undefined>(),
  retrievedVectorContext: Annotation<VectorSearchRetrieverOutput['relevantChunks'] | undefined>(), // Corrected type
  validationResults: Annotation<any | undefined>(), // Use 'any' for now, refine later
  impactAnalysisResults: Annotation<any | undefined>(),
  draftReport: Annotation<string | undefined>(),
  humanFeedback: Annotation<any | undefined>(),
  finalReport: Annotation<string | undefined>(),
  lastToolAction: Annotation<ToolAction | undefined>(),
  lastToolOutput: Annotation<any | undefined>(),
  // Add a messages channel as suggested by the user, even if not directly used by current nodes
  messages: Annotation<BaseMessage[]>({
    reducer: (x, y) => x.concat(y),
    default: () => [],
  }),
});

// Get the TypeScript type from the Annotation for use in node functions
type ProposalReviewStateType = typeof ProposalReviewState.State;

// Adding a comment to force TypeScript re-evaluation

// Custom node to execute Genkit tools
const executeGenkitTool = async (state: ProposalReviewStateType): Promise<Partial<ProposalReviewStateType>> => {
  const toolAction = state.lastToolAction;
  if (!toolAction) {
    throw new Error("No tool action found in state.");
  }

  // Reverting to direct tool invocation with type assertion
  const toolToExecute = {
    ingestDocumentTool,
    knowledgeGraphRetriever,
    vectorSearchRetriever,
    genSpecValidator,
    impactAnalyzer,
    reportDrafter,
    humanFeedbackRequester,
  }[toolAction.toolName];

  if (!toolToExecute) {
    throw new Error(`Tool ${toolAction.toolName} not found.`);
  }

  const result = await (toolToExecute as any).invoke(toolAction.toolInput); // Directly invoke the tool with type assertion
  
  return { lastToolOutput: result }; // Return partial state update
};

// Define the nodes for the graph
const nodes = {
  ingest: async (state: ProposalReviewStateType): Promise<Partial<ProposalReviewStateType>> => {
    const input: IngestDocumentInput = { documentPath: state.rawProposalContent };
    return { lastToolAction: { toolName: 'ingestDocumentTool', toolInput: input }, status: 'INGESTED' };
  },
  executeIngestTool: executeGenkitTool,
  retrieveContext: async (state: ProposalReviewStateType): Promise<Partial<ProposalReviewStateType>> => {
    const kgInput: KnowledgeGraphRetrieverInput = { query: state.parsedContent || '', concepts: [] };
    const vectorInput: VectorSearchRetrieverInput = { query: state.parsedContent || '', topK: 5 };

    return {
      lastToolAction: { toolName: 'knowledgeGraphRetriever', toolInput: kgInput },
      status: 'RETRIEVING_CONTEXT',
    };
  },
  executeKgTool: executeGenkitTool,
  executeVectorTool: executeGenkitTool,
  validateProposal: async (state: ProposalReviewStateType): Promise<Partial<ProposalReviewStateType>> => {
    const input: GenSpecValidatorInput = {
      proposalContent: state.parsedContent || '',
      kgContext: state.retrievedKgContext,
      vectorContext: state.retrievedVectorContext,
    };
    return { lastToolAction: { toolName: 'genSpecValidator', toolInput: input }, status: 'VALIDATING' };
  },
  executeValidatorTool: executeGenkitTool,
  analyzeImpact: async (state: ProposalReviewStateType): Promise<Partial<ProposalReviewStateType>> => {
    const input: ImpactAnalyzerInput = {
      proposalContent: state.parsedContent || '',
      validationResults: state.validationResults,
      kgContext: state.retrievedKgContext,
    };
    return { lastToolAction: { toolName: 'impactAnalyzer', toolInput: input }, status: 'ANALYZING_IMPACT' };
  },
  executeImpactTool: executeGenkitTool,
  generateDraftReport: async (state: ProposalReviewStateType): Promise<Partial<ProposalReviewStateType>> => {
    const input: ReportDrafterInput = {
      proposalContent: state.parsedContent || '',
      validationResults: state.validationResults,
      impactAnalysisResults: state.impactAnalysisResults,
      humanFeedback: state.humanFeedback,
    };
    return { lastToolAction: { toolName: 'reportDrafter', toolInput: input }, status: 'GENERATING_REPORT' };
  },
  executeReportDrafterTool: executeGenkitTool,
  requestHumanFeedback: async (state: ProposalReviewStateType): Promise<Partial<ProposalReviewStateType>> => {
    const input: HumanFeedbackRequesterInput = {
      proposalSummary: state.parsedContent?.substring(0, 100) || '',
      draftReport: state.draftReport || '',
      identifiedIssues: state.validationResults?.errors || [],
    };
    return { lastToolAction: { toolName: 'humanFeedbackRequester', toolInput: input }, status: 'AWAITING_HUMAN_FEEDBACK' };
  },
  executeHumanFeedbackTool: executeGenkitTool,
  finalizeReport: async (state: ProposalReviewStateType): Promise<Partial<ProposalReviewStateType>> => {
    return { finalReport: state.draftReport, status: 'COMPLETED' };
  },
};

// Define the conditional edges
const conditionalEdges = {
  afterValidate: (state: ProposalReviewStateType) => {
    if (state.validationResults && (!state.validationResults.isValid || (state.validationResults.conflicts && state.validationResults.conflicts.length > 0))) {
      return 'requestHumanFeedback';
    }
    return 'analyzeImpact';
  },
  afterGenerateDraft: (state: ProposalReviewStateType) => {
    if (state.humanFeedback && !state.humanFeedback.approval) {
      return 'requestHumanFeedback';
    }
    return 'finalizeReport';
  },
  shouldExecuteTool: (state: ProposalReviewStateType) => {
    return state.lastToolAction ? 'executeTool' : 'noTool';
  },
};

// Build the graph
export const proposalReviewGraph = new StateGraph(ProposalReviewState) // Changed constructor to use Annotation.Root
  .addNode('ingest', nodes.ingest)
  .addNode('executeIngestTool', nodes.executeIngestTool)
  .addNode('retrieveContext', nodes.retrieveContext)
  .addNode('executeKgTool', nodes.executeKgTool)
  .addNode('executeVectorTool', nodes.executeVectorTool)
  .addNode('validateProposal', nodes.validateProposal)
  .addNode('executeValidatorTool', nodes.executeValidatorTool)
  .addNode('analyzeImpact', nodes.analyzeImpact)
  .addNode('executeImpactTool', nodes.executeImpactTool)
  .addNode('generateDraftReport', nodes.generateDraftReport)
  .addNode('executeReportDrafterTool', nodes.executeReportDrafterTool)
  .addNode('requestHumanFeedback', nodes.requestHumanFeedback)
  .addNode('executeHumanFeedbackTool', nodes.executeHumanFeedbackTool)
  .addNode('finalizeReport', nodes.finalizeReport)
  .addEdge('ingest', 'executeIngestTool')
  .addEdge('executeIngestTool', 'retrieveContext')
  .addEdge('retrieveContext', 'executeKgTool')
  .addEdge('executeKgTool', 'executeVectorTool')
  .addEdge('executeVectorTool', 'validateProposal')
  .addEdge('executeValidatorTool', 'analyzeImpact')
  .addEdge('analyzeImpact', 'generateDraftReport')
  .addEdge('generateDraftReport', 'executeReportDrafterTool')
  .addEdge('executeReportDrafterTool', 'requestHumanFeedback')
  .addEdge('requestHumanFeedback', 'executeHumanFeedbackTool')
  .addEdge('executeHumanFeedbackTool', 'generateDraftReport')
  .addEdge('finalizeReport', END)
  .addConditionalEdges('validateProposal', conditionalEdges.afterValidate)
  .addConditionalEdges('generateDraftReport', conditionalEdges.afterGenerateDraft)
  .setEntryPoint('ingest');

// Example of how to run the graph (for testing/demonstration)
/*
async function runProposalReview(proposalContent: string) {
  const initialInput: ProposalReviewStateType = {
    proposalId: `prop-${Date.now()}`,
    rawProposalContent: proposalContent,
    status: 'INGESTED',
    messages: [], // Initialize messages channel
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