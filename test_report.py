"""
test_report.py
Generate HTML-format test execution reports.
"""

import time
import os
from html import escape


class TestReport:
    """Collect testcase execution results and generate an HTML report."""

    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.start_time = time.time()
        self.results = []  # list of dict: name, status, duration, error, steps_done

    def add_result(self, name, status, duration, error=None, steps_done=0):
        """
        Add one testcase result.
        status: 'PASS' | 'FAIL' | 'SKIP'
        """
        self.results.append({
            'name': name,
            'status': status,
            'duration': duration,
            'error': str(error) if error else None,
            'steps_done': steps_done,
        })

    def summary(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        skipped = sum(1 for r in self.results if r['status'] == 'SKIP')
        return total, passed, failed, skipped

    def generate_html(self, output_path=None):
        """Generate an HTML report file and return its path."""
        if output_path is None:
            output_path = "testreport/report.html"

        total_duration = time.time() - self.start_time
        total, passed, failed, skipped = self.summary()
        pass_rate = f"{passed / total * 100:.1f}" if total > 0 else "0"

        # Build table rows
        rows_html = ""
        for idx, r in enumerate(self.results, 1):
            status_cls = {'PASS': 'pass', 'FAIL': 'fail', 'SKIP': 'skip'}.get(r['status'], '')
            error_html = ""
            if r['error']:
                error_html = f'<div class="error-detail"><b>Failure reason:</b><pre>{escape(r["error"])}</pre></div>'
            rows_html += f"""
            <tr class="{status_cls}">
                <td>{idx}</td>
                <td>{escape(r['name'])}</td>
                <td><span class="badge {status_cls}">{r['status']}</span></td>
                <td>{r['steps_done']}</td>
                <td>{r['duration']:.2f}s</td>
            </tr>"""
            if error_html:
                rows_html += f"""
            <tr class="error-row">
                <td></td>
                <td colspan="4">{error_html}</td>
            </tr>"""

        html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Test Report - {escape(os.path.basename(self.xml_path))}</title>
<style>
  body {{ font-family: 'Segoe UI', Helvetica, Arial, sans-serif; margin: 0; padding: 24px; background: #f8fafc; color: #1f2937; }}
  h1 {{ margin-bottom: 4px; }}
  .sub {{ color: #6b7280; margin-bottom: 20px; }}
  .summary {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
  .card {{ border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px 24px; background: #fff; min-width: 120px; }}
  .card .num {{ font-size: 28px; font-weight: 700; }}
  .card .label {{ color: #6b7280; font-size: 13px; }}
  .card.total .num {{ color: #1e40af; }}
  .card.pass-card .num {{ color: #16a34a; }}
  .card.fail-card .num {{ color: #dc2626; }}
  .card.skip-card .num {{ color: #ca8a04; }}
  .card.rate .num {{ color: #7c3aed; }}
  .card.time .num {{ color: #0891b2; font-size: 20px; }}
  table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
  th {{ background: #f1f5f9; text-align: left; padding: 10px 14px; font-size: 13px; color: #475569; border-bottom: 2px solid #e2e8f0; }}
  td {{ padding: 10px 14px; border-bottom: 1px solid #f1f5f9; font-size: 14px; }}
  tr.fail td {{ background: #fef2f2; }}
  tr.error-row td {{ background: #fef2f2; padding-top: 0; }}
  .badge {{ padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
  .badge.pass {{ background: #dcfce7; color: #16a34a; }}
  .badge.fail {{ background: #fee2e2; color: #dc2626; }}
  .badge.skip {{ background: #fef9c3; color: #ca8a04; }}
  .error-detail {{ margin: 4px 0 8px; }}
  .error-detail pre {{ background: #fff5f5; border: 1px solid #fecaca; border-radius: 6px; padding: 10px; font-size: 12px; white-space: pre-wrap; word-break: break-all; max-height: 200px; overflow-y: auto; }}
  .footer {{ margin-top: 24px; color: #9ca3af; font-size: 12px; }}
</style>
</head>
<body>
<h1>Test Execution Report</h1>
<p class="sub">{escape(self.xml_path)} &nbsp;|&nbsp; {time.strftime('%Y-%m-%d %H:%M:%S')}</p>

<div class="summary">
    <div class="card total"><div class="num">{total}</div><div class="label">Total Cases</div></div>
    <div class="card pass-card"><div class="num">{passed}</div><div class="label">Passed</div></div>
    <div class="card fail-card"><div class="num">{failed}</div><div class="label">Failed</div></div>
    <div class="card skip-card"><div class="num">{skipped}</div><div class="label">Skipped</div></div>
    <div class="card rate"><div class="num">{pass_rate}%</div><div class="label">Pass Rate</div></div>
    <div class="card time"><div class="num">{total_duration:.1f}s</div><div class="label">Total Duration</div></div>
</div>

<table>
<thead>
    <tr><th>#</th><th>Testcase Name</th><th>Status</th><th>Steps</th><th>Duration</th></tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>

<div class="footer">Generated by AutoControlPC · test_report.py</div>
</body>
</html>"""

        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return output_path
