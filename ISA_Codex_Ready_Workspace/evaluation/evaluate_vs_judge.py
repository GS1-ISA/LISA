import vertexai
from vertexai.language_models import TextGenerationModel
import json

def evaluate(model_output, expected_output):
    model = TextGenerationModel.from_pretrained("text-bison@002")
    prompt = f"Evaluate the similarity between expected:\n{expected_output}\nand actual:\n{model_output}\nReturn a score 0-10 with justification."
    response = model.predict(prompt)
    return response.text

if __name__ == "__main__":
    with open("evaluation/golden_dataset.json") as f:
        dataset = json.load(f)
    for item in dataset:
        result = evaluate(item['actual'], item['expected'])
        print(result)
