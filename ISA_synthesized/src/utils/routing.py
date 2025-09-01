DEFAULT_MODEL = "openrouter/auto"
TASK_MODEL_MAP = {
    "qa": "openrouter/auto:floor",
    "summarize": "openrouter/auto:floor",
    "reason": "openrouter/auto",
}


def choose_model(task: str) -> str:
    return TASK_MODEL_MAP.get(task, DEFAULT_MODEL)
