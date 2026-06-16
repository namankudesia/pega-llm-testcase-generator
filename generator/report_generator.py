"""Generates HTML test summary report from generated test cases."""
from __future__ import annotations
from typing import List
from generator.pega_testcase_generator import TestCase
from datetime import datetime


def generate_html_report(test_cases: List[TestCase], output_path: str = "output/report.html"):
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    p1 = sum(1 for tc in test_cases if tc.priority == "P1")
    functional = sum(1 for tc in test_cases if tc.test_type == "functional")
    smoke = sum(1 for tc in test_cases if "smoke" in tc.tags)

    rows = ""
    for tc in test_cases:
        badge = {"P1":"#dc3545","P2":"#fd7e14","P3":"#198754"}.get(tc.priority,"#6c757d")
        rows += f"""
        <tr>
          <td><code>{tc.id}</code></td>
          <td>{tc.title}</td>
          <td><span class="badge" style="background:{badge}">{tc.priority}</span></td>
          <td>{tc.test_type}</td>
          <td><pre style="font-size:11px;white-space:pre-wrap">{tc.bdd_scenario}</pre></td>
          <td>{", ".join(tc.pega_components[:2])}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html><head><title>Pega Test Cases</title>
<style>
  body{{font-family:Calibri,sans-serif;margin:2rem;color:#222}}
  h1{{color:#1B4F8A}} table{{width:100%;border-collapse:collapse;margin-top:1rem}}
  th{{background:#1B4F8A;color:#fff;padding:8px;text-align:left}}
  td{{padding:7px;border-bottom:1px solid #ddd;vertical-align:top}}
  tr:hover{{background:#f5f8ff}} .badge{{color:#fff;padding:2px 8px;border-radius:4px;font-size:12px}}
  .stat{{display:inline-block;background:#E6F1FB;border-radius:8px;padding:12px 24px;margin:0 8px;text-align:center}}
  .stat-num{{font-size:32px;font-weight:bold;color:#1B4F8A}} .stat-label{{font-size:13px;color:#555}}
</style></head>
<body>
<h1>Pega Test Case Report</h1>
<p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Total: {len(test_cases)} test cases</p>
<div style="margin:1rem 0">
  <div class="stat"><div class="stat-num">{len(test_cases)}</div><div class="stat-label">Total Cases</div></div>
  <div class="stat"><div class="stat-num">{p1}</div><div class="stat-label">P1 Critical</div></div>
  <div class="stat"><div class="stat-num">{smoke}</div><div class="stat-label">Smoke Tests</div></div>
  <div class="stat"><div class="stat-num">{functional}</div><div class="stat-label">Functional</div></div>
</div>
<table>
  <tr><th>ID</th><th>Title</th><th>Priority</th><th>Type</th><th>BDD Scenario</th><th>Pega Components</th></tr>
  {rows}
</table></body></html>"""

    with open(output_path, "w") as f:
        f.write(html)
    print(f"HTML report saved to {output_path}")
