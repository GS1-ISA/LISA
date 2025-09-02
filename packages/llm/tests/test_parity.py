from llm_runtime import LlmRuntime


def test_schema_parity_between_backends():
    msgs = [{"role": "user", "content": "hello"}]
    openai = LlmRuntime("openai").chat(msgs, model="gpt-stub")
    bedrock = LlmRuntime("bedrock").chat(msgs, model="bedrock-stub")
    # Both must provide 'choices[0].message.content'
    def extract(d):
        return d["choices"][0]["message"]["content"]

    assert isinstance(extract(openai), str)
    assert isinstance(extract(bedrock), str)

