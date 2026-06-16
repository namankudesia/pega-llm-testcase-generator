"""
Pega LLM Test Case Generator
Converts plain-English business requirements into structured Pega test cases
using chain-of-thought prompting, few-shot examples, and BDD output format.
"""
from __future__ import annotations
import json, os, re
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from openai import OpenAI


@dataclass
class TestCase:
    id: str
    title: str
    test_type: str          # functional | regression | integration | UAT
    preconditions: List[str]
    steps: List[str]
    expected_results: List[str]
    pega_components: List[str]  # Case Type / Flow / Rule / Decision Table
    priority: str           # P1 | P2 | P3
    bdd_scenario: str       # Gherkin Given/When/Then
    tags: List[str] = field(default_factory=list)
    generated_at: str = ""

    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()


SYSTEM_PROMPT = """You are a senior Pega QA engineer and test architect with 10+ years of experience.

Your job is to convert business requirements into comprehensive, structured test cases for Pega BPM applications.

You understand deeply:
- Pega Case Management (case types, stages, processes, sub-cases)
- Business Rules (decision tables, validation rules, when rules)
- UI Rules (harnesses, sections, flow actions)
- SLA timers, assignment routing, work queues
- Healthcare domain: prior authorization, utilization management, claims

For each requirement, generate test cases in this EXACT JSON format:
{
  "test_cases": [
    {
      "id": "TC_001",
      "title": "string",
      "test_type": "functional|regression|integration|UAT",
      "preconditions": ["string"],
      "steps": ["Step 1: ...", "Step 2: ..."],
      "expected_results": ["Expected: ..."],
      "pega_components": ["Case Type: ...", "Rule: ..."],
      "priority": "P1|P2|P3",
      "bdd_scenario": "Given ...\nWhen ...\nThen ...",
      "tags": ["smoke", "regression"]
    }
  ]
}

Return ONLY valid JSON. No markdown, no explanation."""

FEW_SHOT_EXAMPLE = """
Business Requirement: 
"When a prior authorization request is submitted, the system should route it to the Medical Review queue if the requested service cost exceeds $5,000, otherwise route to Auto-Approval queue."

Generated Test Cases:
{
  "test_cases": [
    {
      "id": "TC_001",
      "title": "Verify routing to Medical Review queue when cost > $5000",
      "test_type": "functional",
      "preconditions": ["User logged in with Submitter role", "PA case in Draft stage", "Valid member and provider data"],
      "steps": ["Step 1: Create new Prior Authorization case", "Step 2: Enter service details with cost = $5,001", "Step 3: Click Submit", "Step 4: Verify case stage transitions to Submitted", "Step 5: Navigate to Work Queue"],
      "expected_results": ["Case routed to Medical Review queue", "Assignment visible in Medical Reviewer work queue", "SLA timer started (72 hours)"],
      "pega_components": ["Case Type: PriorAuthorization", "Decision Table: DT_RouteByServiceCost", "SLA: SLA_MedicalReview72hr"],
      "priority": "P1",
      "bdd_scenario": "Given a PA case with service cost of $5,001\nWhen the case is submitted\nThen the case should be routed to Medical Review queue\nAnd SLA timer should start",
      "tags": ["smoke", "routing", "P1"]
    }
  ]
}
"""


class PegaTestCaseGenerator:
    def __init__(self, api_key: str = None, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.generated_count = 0

    def generate(self, requirement: str, context: Optional[str] = None,
                 num_cases: int = 5) -> List[TestCase]:
        prompt = self._build_prompt(requirement, context, num_cases)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": FEW_SHOT_EXAMPLE},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        raw = response.choices[0].message.content
        data = json.loads(raw)
        test_cases = [TestCase(**tc) for tc in data.get("test_cases", [])]
        self.generated_count += len(test_cases)
        return test_cases

    def generate_batch(self, requirements: List[str]) -> Dict[str, List[TestCase]]:
        results = {}
        for i, req in enumerate(requirements, 1):
            print(f"[{i}/{len(requirements)}] Generating for: {req[:60]}...")
            results[f"REQ_{i:03d}"] = self.generate(req)
        return results

    def export_to_json(self, test_cases: List[TestCase], output_path: str):
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump([asdict(tc) for tc in test_cases], f, indent=2)
        print(f"Exported {len(test_cases)} test cases to {output_path}")

    def export_to_csv(self, test_cases: List[TestCase], output_path: str):
        import csv
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id","title","test_type","priority","bdd_scenario","tags"])
            writer.writeheader()
            for tc in test_cases:
                writer.writerow({
                    "id": tc.id, "title": tc.title, "test_type": tc.test_type,
                    "priority": tc.priority,
                    "bdd_scenario": tc.bdd_scenario.replace("\n", " | "),
                    "tags": ", ".join(tc.tags)
                })
        print(f"Exported CSV to {output_path}")

    def _build_prompt(self, requirement: str, context: Optional[str], num_cases: int) -> str:
        ctx = f"\n\nAdditional Context:\n{context}" if context else ""
        return f"""Generate {num_cases} comprehensive Pega test cases for this requirement:{ctx}

Business Requirement:
{requirement}

Include a mix of: positive cases, negative/boundary cases, regression cases.
Tag smoke-test cases as "smoke". Tag P1 cases as priority P1."""
