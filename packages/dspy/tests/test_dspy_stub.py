from dspy_modules import ClassifierStub


def test_classifier_stub_predicts():
    m = ClassifierStub()
    m.compile()
    assert m.predict("this is OK") == "OK"
    assert m.predict("nope") == "OTHER"

