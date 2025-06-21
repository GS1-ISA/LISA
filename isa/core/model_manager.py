import json
import os
from typing import Optional

class ModelManager:
    def __init__(self, config_path='isa/config/roo_mode_map.json'):
        self.config_path = config_path
        self.mode_config = self._load_mode_config()

    def _load_mode_config(self):
        """Loads the mode configuration from the JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {self.config_path}")
            return {"modes": [], "mcpServers": []}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {self.config_path}")
            return {"modes": [], "mcpServers": []}

    def get_model_params(self, mode_slug: str, prompt_context: Optional[dict] = None):
        """
        Retrieves the appropriate model and thinking budget for a given mode,
        with dynamic switching based on prompt context.
        """
        default_model = "gemini-2.5-flash"
        default_thinking_budget = 5000

        mode_info = next((m for m in self.mode_config.get("modes", []) if m["slug"] == mode_slug), None)

        if mode_info:
            model = mode_info.get("model", default_model)
            thinking_budget = mode_info.get("thinkingBudget", default_thinking_budget)
        else:
            model = default_model
            thinking_budget = default_thinking_budget
            print(f"Warning: Mode '{mode_slug}' not found in config. Using defaults.")

        # Dynamic switching logic based on prompt context
        if prompt_context:
            input_token_count = prompt_context.get("input_token_count", 0)
            task_intent = prompt_context.get("task_intent", "").lower()
            complexity_flags = prompt_context.get("complexity_flags", [])

            # Define thresholds and complexity keywords
            high_complexity_threshold = 20000
            pro_keywords = ["architect", "indexer", "refactor", "complex", "deep analysis", "strategic design"]
            flash_lite_keywords = ["simple", "quick", "low latency", "high volume", "rate-limit fallback"]

            # Prioritize Pro for high complexity or specific flags
            if input_token_count > high_complexity_threshold or any(flag in task_intent for flag in pro_keywords) or any(flag in complexity_flags for flag in pro_keywords):
                model = "gemini-2.5-pro"
                thinking_budget = -1 # Dynamic budget for Pro

            # Prioritize Flash-Lite for simple/latency-sensitive tasks
            elif any(flag in task_intent for flag in flash_lite_keywords) or any(flag in complexity_flags for flag in flash_lite_keywords):
                model = "gemini-2.5-flash-lite-preview-06-17"
                # If thinkingBudget is 0, it means minimize internal reasoning
                if thinking_budget == -1: # If default was Pro's dynamic, set a small budget for Flash-Lite
                    thinking_budget = 100
                elif thinking_budget == 0:
                    pass # Keep 0 for no thinking
                elif thinking_budget > 0 and thinking_budget > 1000: # Cap large budgets for Flash-Lite
                    thinking_budget = 1000
            
            # Default to Flash for standard tasks if not overridden
            elif model not in ["gemini-2.5-pro", "gemini-2.5-flash-lite-preview-06-17"]:
                model = "gemini-2.5-flash"
                if thinking_budget == -1: # If default was Pro's dynamic, set a standard budget for Flash
                    thinking_budget = 5000

        self._log_model_usage(mode_slug, model, thinking_budget, prompt_context)
        return {"model": model, "thinkingBudget": thinking_budget}

    def _log_model_usage(self, mode_slug: str, model: str, thinking_budget: int, prompt_context: dict):
        """Logs the model usage to a file."""
        log_dir = 'isa/logs'
        log_file = os.path.join(log_dir, 'model_usage.log')
        os.makedirs(log_dir, exist_ok=True)

        log_entry = {
            "timestamp": self._get_current_timestamp(),
            "mode_slug": mode_slug,
            "model_used": model,
            "thinking_budget_applied": thinking_budget,
            "prompt_context": prompt_context
        }
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")

    def _get_current_timestamp(self):
        """Returns the current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

import sys

if __name__ == "__main__":
    manager = ModelManager()
    mode_slug = sys.argv[1] if len(sys.argv) > 1 else "code" # Default to 'code' if no slug provided
    prompt_context = {}
    if len(sys.argv) > 2:
        try:
            prompt_context = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            print("Error: Invalid JSON for prompt_context. Using empty context.", file=sys.stderr)

    result = manager.get_model_params(mode_slug, prompt_context)
    print(json.dumps(result))