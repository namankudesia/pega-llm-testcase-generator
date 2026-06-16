# Pega LLM Test Case Generator

> Converts plain-English business requirements into structured Pega test cases using **OpenAI GPT-4 + Chain-of-Thought Prompting + BDD output**

---

## How It Was Built

### The Problem
Writing Pega test cases manually is time-consuming and requires deep knowledge of case types, decision tables, SLAs, and UI rules. A single complex requirement can take 30–60 minutes to properly document.

### The Solution
This tool uses GPT-4 with:
- **Few-shot prompting** — provides a Pega-specific example to prime the model
- **Chain-of-thought reasoning** — the model reasons through Pega components before generating
- **Structured JSON output** — `response_format: json_object` ensures parseable output every time
- **BDD format** — generates Gherkin Given/When/Then scenarios ready for Cucumber integration

### What gets generated per requirement:
- Test case ID, title, priority (P1/P2/P3)
- Preconditions, step-by-step actions, expected results
- Pega component references (Case Type, Decision Table, SLA, Rule name)
- BDD Gherkin scenario
- Tags (smoke, regression, P1, etc.)

---

## How to Run

```bash
git clone https://github.com/namankudesia/pega-llm-testcase-generator.git
cd pega-llm-testcase-generator
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && echo 'OPENAI_API_KEY=sk-your-key' >> .env

# Single requirement
python main.py -r "When PA is submitted with cost > $5000, route to Medical Review queue" --html-report

# Batch from file
python main.py -f requirements.txt -n 5 --html-report

# Output: output/test_cases.json + output/test_cases.csv + output/report.html
```

---

## Output Formats
- **JSON** — full structured test case data
- **CSV** — importable to JIRA, ALM, Excel
- **HTML report** — visual dashboard with priority breakdown

## Run Tests
```bash
pytest tests/ -v
```

> Built by [Naman Kudesia](https://github.com/namankudesia)
