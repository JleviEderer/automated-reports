"""
PDF Report Generator

Generates HTML reports from source data and converts to PDF
using Playwright for high-fidelity CSS rendering.

Usage:
    python src/generate.py --data data/ --template report --output output/report.pdf
    python src/generate.py --data data/ --template report --preview
    python src/generate.py --data data/ --template report --output output/report.pdf --iterate
    python src/generate.py --data data/ --template report --output output/report.pdf --preset marketing-report
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_preset(preset_name: str) -> dict:
    """Load a report type preset from the presets/ directory."""
    preset_path = PROJECT_ROOT / "presets" / f"{preset_name}.yaml"
    if not preset_path.exists():
        print(f"Error: Preset not found: {preset_path}", file=sys.stderr)
        available = [p.stem for p in (PROJECT_ROOT / "presets").glob("*.yaml")]
        print(f"Available presets: {', '.join(available)}", file=sys.stderr)
        sys.exit(1)

    if yaml is None:
        # Fallback: read raw text if PyYAML not installed
        print("Warning: PyYAML not installed. Preset loaded as raw text.", file=sys.stderr)
        return {"_raw": preset_path.read_text(encoding="utf-8")}

    with open(preset_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_data(data_path: str) -> dict:
    """Load and validate the data directory or JSON file."""
    path = PROJECT_ROOT / data_path
    if not path.exists():
        print(f"Error: Data path not found: {path}", file=sys.stderr)
        sys.exit(1)

    # If it's a directory, list its contents and return metadata
    if path.is_dir():
        files = [f.name for f in path.iterdir() if f.is_file()]
        return {"_data_dir": str(path), "_files": files}

    # If it's a JSON file, load it (no hardcoded required keys)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def generate_html(data_path: str, template_name: str) -> Path:
    """
    Generate the HTML report.

    Uses the pre-rendered HTML from the Design Agent output.
    A future version could use Jinja2 templates with dynamic data injection.
    """
    html_path = PROJECT_ROOT / "output" / "report.html"
    if not html_path.exists():
        print(f"Error: HTML report not found at {html_path}", file=sys.stderr)
        print("Run the Design Agent first to generate the HTML.", file=sys.stderr)
        sys.exit(1)

    print(f"HTML report ready: {html_path}")
    return html_path


def render_pdf_playwright(html_path: Path, output_path: Path) -> bool:
    """
    Render HTML to PDF using Playwright.

    Starts a local HTTP server to serve the HTML (Playwright requires http://),
    then uses Playwright's Chromium to render a print-quality PDF.
    """
    import http.server
    import threading

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Serve from project root so image paths resolve
    serve_dir = PROJECT_ROOT

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(serve_dir), **kwargs)

        def log_message(self, format, *args):
            pass  # suppress logs

    server = http.server.HTTPServer(("127.0.0.1", 0), QuietHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    url = f"http://127.0.0.1:{port}/output/report.html"
    pdf_posix = output_path.as_posix()

    script = f"""
const {{ chromium }} = require('playwright');

(async () => {{
    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.goto('{url}', {{ waitUntil: 'networkidle', timeout: 30000 }});

    // Wait for Google Fonts to load
    await page.waitForTimeout(3000);

    await page.pdf({{
        path: '{pdf_posix}',
        format: 'Letter',
        printBackground: true,
        preferCSSPageSize: true,
        margin: {{ top: '0', right: '0', bottom: '0', left: '0' }}
    }});

    await browser.close();
    console.log('PDF generated successfully');
}})();
"""

    script_path = PROJECT_ROOT / "src" / "_render.js"
    try:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)

        result = subprocess.run(
            ["node", str(script_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            print(f"PDF rendered: {output_path}")
            return True
        else:
            print(f"PDF render failed: {result.stderr}", file=sys.stderr)
            return False
    except FileNotFoundError:
        print("Error: Node.js not found. Install Node.js for Playwright rendering.", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("Error: PDF render timed out after 60s.", file=sys.stderr)
        return False
    finally:
        script_path.unlink(missing_ok=True)
        server.shutdown()


def run_qa(pdf_path: Path) -> dict:
    """
    Run QA validation. Delegates to validate.py.
    Returns dict with 'status' (PASS/FAIL) and 'issues' list.
    """
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "src" / "validate.py"), str(pdf_path)],
        capture_output=True,
        text=True,
    )

    try:
        return json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError):
        return {
            "status": "FAIL",
            "issues": [f"QA script error: {result.stderr or result.stdout}"],
        }


def main():
    parser = argparse.ArgumentParser(description="Generate PDF report from structured data")
    parser.add_argument("--data", required=True, help="Path to JSON data file (relative to project root)")
    parser.add_argument("--template", required=True, help="Template name (e.g., 'report')")
    parser.add_argument("--output", help="Output PDF path (relative to project root)")
    parser.add_argument("--preview", action="store_true", help="Generate HTML preview only, skip PDF")
    parser.add_argument("--iterate", action="store_true", help="Run full QA loop (max 3 iterations)")
    parser.add_argument("--preset", default="consultant-report", help="Report type preset (default: consultant-report)")

    args = parser.parse_args()

    # Load preset
    preset = load_preset(args.preset)
    print(f"Preset loaded: {preset.get('name', args.preset)}")

    # Load and validate data
    data = load_data(args.data)
    file_count = len(data.get("_files", [])) if "_files" in data else len(data)
    print(f"Data loaded: {file_count} items")

    # Generate HTML
    html_path = generate_html(args.data, args.template)

    if args.preview:
        print(f"\nPreview ready: {html_path}")
        print("Open in a browser to review before PDF rendering.")
        return

    if not args.output:
        print("Error: --output is required for PDF generation (or use --preview)", file=sys.stderr)
        sys.exit(1)

    output_path = PROJECT_ROOT / args.output

    # Render PDF
    success = render_pdf_playwright(html_path, output_path)
    if not success:
        sys.exit(1)

    if args.iterate:
        max_iterations = 3
        for i in range(max_iterations):
            print(f"\n--- QA Iteration {i + 1}/{max_iterations} ---")
            qa_result = run_qa(output_path)

            if qa_result["status"] == "PASS":
                print("QA PASSED. Report is ready.")
                return
            elif qa_result["status"] == "PASS WITH NOTES":
                print("QA PASSED WITH NOTES:")
                for note in qa_result.get("notes", []):
                    print(f"  - {note}")
                return
            else:
                print(f"QA FAILED ({len(qa_result.get('issues', []))} issues):")
                for issue in qa_result.get("issues", []):
                    print(f"  - {issue}")

                if i < max_iterations - 1:
                    print("\nIterating...")
                else:
                    print(f"\nMax iterations ({max_iterations}) reached.")
                    print("Shipping best version with QA notes attached.")

    print(f"\nDone. Output: {output_path}")


if __name__ == "__main__":
    main()
