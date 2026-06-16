import pytest
from unittest.mock import MagicMock, patch
from generator.pega_testcase_generator import PegaTestCaseGenerator, TestCase
import json

MOCK_RESPONSE = json.dumps({"test_cases": [{
    "id": "TC_001", "title": "Test routing", "test_type": "functional",
    "preconditions": ["User logged in"], "steps": ["Step 1: Submit case"],
    "expected_results": ["Case routed correctly"],
    "pega_components": ["Case Type: PA"], "priority": "P1",
    "bdd_scenario": "Given a case\nWhen submitted\nThen routed", "tags": ["smoke"]
}]})

@patch("generator.pega_testcase_generator.OpenAI")
def test_generate_returns_test_cases(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.return_value.choices[0].message.content = MOCK_RESPONSE
    gen = PegaTestCaseGenerator(api_key="test-key")
    cases = gen.generate("Test requirement")
    assert len(cases) == 1
    assert isinstance(cases[0], TestCase)
    assert cases[0].priority == "P1"

def test_testcase_dataclass():
    tc = TestCase(id="TC_001", title="Test", test_type="functional",
                  preconditions=[], steps=[], expected_results=[],
                  pega_components=[], priority="P1", bdd_scenario="Given\nWhen\nThen")
    assert tc.generated_at != ""
    assert tc.tags == []
