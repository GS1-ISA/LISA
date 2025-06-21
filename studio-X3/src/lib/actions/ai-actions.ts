
"use server";

import {
  AnswerGs1QuestionsInputSchema,
  AnalyzeStandardsInputSchema,
  ConductIndependentResearchInputSchema,
  NaturalLanguageToFormalDescriptionInputSchema,
} from "@/ai/schemas"; // Import Zod schema objects from the new central file

import {
  answerGs1Questions,
  type AnswerGs1QuestionsInput,
  type AnswerGs1QuestionsOutput,
  analyzeStandards,
  type AnalyzeStandardsInput,
  type AnalyzeStandardsOutput,
  conductIndependentResearch,
  type ConductIndependentResearchInput,
  type ConductIndependentResearchOutput,
  naturalLanguageToFormalDescription,
  type NaturalLanguageToFormalDescriptionInput,
  type NaturalLanguageToFormalDescriptionOutput,
} from "@/ai/flows"; // Import async functions and types from flows index
import { z } from "zod";

interface ActionResult<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export async function handleAnswerGs1Questions(
  input: AnswerGs1QuestionsInput
): Promise<ActionResult<AnswerGs1QuestionsOutput>> {
  try {
    const validatedInput = AnswerGs1QuestionsInputSchema.parse(input);
    const result = await answerGs1Questions(validatedInput);
    return { success: true, data: result };
  } catch (e: any) {
    if (e instanceof z.ZodError) {
      return { success: false, error: "Invalid input: " + e.errors.map(err => err.message).join(', ') };
    }
    return { success: false, error: e.message || "An unexpected error occurred" };
  }
}

export async function handleAnalyzeStandards(
  input: AnalyzeStandardsInput
): Promise<ActionResult<AnalyzeStandardsOutput>> {
  try {
    const validatedInput = AnalyzeStandardsInputSchema.parse(input);
    const result = await analyzeStandards(validatedInput);
    return { success: true, data: result };
  } catch (e: any) {
    if (e instanceof z.ZodError) {
      return { success: false, error: "Invalid input: " + e.errors.map(err => err.message).join(', ') };
    }
    return { success: false, error: e.message || "An unexpected error occurred" };
  }
}

export async function handleConductIndependentResearch(
  input: ConductIndependentResearchInput
): Promise<ActionResult<ConductIndependentResearchOutput>> {
  try {
    const validatedInput = ConductIndependentResearchInputSchema.parse(input);
    const result = await conductIndependentResearch(validatedInput);
    return { success: true, data: result };
  } catch (e: any) {
    if (e instanceof z.ZodError) {
      return { success: false, error: "Invalid input: " + e.errors.map(err => err.message).join(', ') };
    }
    return { success: false, error: e.message || "An unexpected error occurred" };
  }
}

export async function handleNaturalLanguageToFormalDescription(
  input: NaturalLanguageToFormalDescriptionInput
): Promise<ActionResult<NaturalLanguageToFormalDescriptionOutput>> {
  try {
    const validatedInput = NaturalLanguageToFormalDescriptionInputSchema.parse(input);
    const result = await naturalLanguageToFormalDescription(validatedInput);
    return { success: true, data: result };
  } catch (e: any) {
    if (e instanceof z.ZodError) {
      return { success: false, error: "Invalid input: " + e.errors.map(err => err.message).join(', ') };
    }
    return { success: false, error: e.message || "An unexpected error occurred" };
  }
}
