"""
Pega LLM Test Case Generator — CLI entry point.

Usage:
  python main.py --requirement "When PA is submitted, route to Medical Review if cost > $5000"
  python main.py --file requirements.txt --output output/test_cases.json
"""
import argparse, os
from generator.pega_testcase_generator import PegaTestCaseGenerator
from generator.report_generator import generate_html_report

def main():
    parser = argparse.ArgumentParser(description="Pega LLM Test Case Generator")
    parser.add_argument("--requirement", "-r", help="Single requirement string")
    parser.add_argument("--file", "-f", help="Text file with one requirement per line")
    parser.add_argument("--output", "-o", default="output/test_cases.json")
    parser.add_argument("--num-cases", "-n", type=int, default=5)
    parser.add_argument("--html-report", action="store_true")
    args = parser.parse_args()

    generator = PegaTestCaseGenerator()
    all_cases = []

    if args.requirement:
        cases = generator.generate(args.requirement, num_cases=args.num_cases)
        all_cases.extend(cases)
        for tc in cases:
            print(f"\n{'='*60}")
            print(f"ID: {tc.id} | {tc.title} | {tc.priority}")
            print(f"BDD:\n{tc.bdd_scenario}")
    elif args.file:
        with open(args.file) as f:
            reqs = [l.strip() for l in f if l.strip()]
        batch = generator.generate_batch(reqs)
        for cases in batch.values():
            all_cases.extend(cases)
    else:
        parser.print_help()
        return

    generator.export_to_json(all_cases, args.output)
    generator.export_to_csv(all_cases, args.output.replace(".json", ".csv"))

    if args.html_report:
        generate_html_report(all_cases)

    print(f"\nDone! Generated {len(all_cases)} test cases.")

if __name__ == "__main__":
    main()
