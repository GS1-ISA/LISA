
import type {
  AnswerGs1QuestionsInput,
  AnswerGs1QuestionsOutput,
  AnalyzeStandardsInput,
  AnalyzeStandardsOutput,
  ConductIndependentResearchInput,
  ConductIndependentResearchOutput,
  NaturalLanguageToFormalDescriptionInput,
  NaturalLanguageToFormalDescriptionOutput
} from "@/ai/flows"; // Assuming flows export their types from an index or directly

// Re-exporting for convenience, or define specific app-level types if needed
export type {
  AnswerGs1QuestionsInput,
  AnswerGs1QuestionsOutput,
  AnalyzeStandardsInput,
  AnalyzeStandardsOutput,
  ConductIndependentResearchInput,
  ConductIndependentResearchOutput,
  NaturalLanguageToFormalDescriptionInput,
  NaturalLanguageToFormalDescriptionOutput
};

export interface ExplainableOutput {
  reasoningSteps?: string[];
  confidenceScore?: number | string;
  modelEvaluationMetrics?: Record<string, string | number>;
  // Add other common explainability fields here
}

// Example usage for a combined output type
export type QAResultWithExplainability = AnswerGs1QuestionsOutput & ExplainableOutput;

export type AnalysisResultWithExplainability = AnalyzeStandardsOutput & ExplainableOutput;

export type NLToFormalResultWithExplainability = NaturalLanguageToFormalDescriptionOutput & ExplainableOutput;

export type ResearchResultWithExplainability = ConductIndependentResearchOutput & ExplainableOutput;
