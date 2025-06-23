import vertexai
from vertexai.generative_models import GenerativeModel
import json
import os

def evaluate(model_output, expected_output):
    project_ids_to_try = ["flowing-digit-447320-e2", "gs1-isa", "isa-firebase-5cf2f"]
    locations_to_try = ["us-central1", "us-east4", "europe-west4", "europe-west1"]
    models_to_try = ["gemini-pro", "gemini-flash-2.5"]

    for project_id in project_ids_to_try:
        for location in locations_to_try:
            for model_name in models_to_try:
                try:
                    vertexai.init(project=project_id, location=location)
                    model = GenerativeModel(model_name)
                    prompt = f"Evaluate the similarity between expected:\n{expected_output}\nand actual:\n{model_output}\nReturn a score 0-10 with justification."
                    response = model.generate_content(prompt)
                    return response.text
                except Exception as e:
                    print(f"Error with model '{model_name}' in project '{project_id}' and location '{location}': {e}")
    
    return "Error: Could not access Gemini model with any tried project ID, location, or model. Please ensure Vertex AI Generative Models API is enabled and service account has permissions for the relevant projects."

if __name__ == "__main__":
    golden_dataset_path = "/Users/frisowempe/Desktop/isa_workspace/ISA_Codex_Ready_Workspace 3/evaluation/golden_dataset.json"
    
    if not os.path.exists(golden_dataset_path):
        print(f"Error: Dataset file not found at {golden_dataset_path}")
    else:
        with open(golden_dataset_path) as f:
            dataset = json.load(f)
        for item in dataset:
            result = evaluate(item['actual'], item['expected'])
            print(result)
