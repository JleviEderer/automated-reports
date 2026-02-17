"""
QA Validator — Report Quality Checklist

Validates rendered reports against the QA Agent's quality checklist.
Can validate HTML files directly or be used as part of the iterative loop.

Usage:
    python src/validate.py output/report.html
    python src/validate.py output/report.pdf
"""

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# AI filler phrases that should never appear in the report
AI_FILLER_PHRASES = [
    "it's worth noting",
    "it is worth noting",
    "interestingly",
    "furthermore",
    "additionally",
    "in conclusion",
    "in this section",
    "we will discuss",
    "it can be observed",
    "it should be noted",
    "needless to say",
    "as we can see",
    "it goes without saying",
    "in today's world",
    "at the end of the day",
    "moving forward",
    "paradigm shift",
    "leverage synergies",
    "deep dive",
    "unpack",
    "holistic approach",
    "game-changer",
    "cutting-edge",
    "it's important to note",
    "as mentioned earlier",
    "in summary",
]


def validate_html(html_path: Path) -> dict:
    """
    Validate an HTML report against the QA checklist.
    Returns dict with status and issues.
    """
    if not html_path.exists():
        return {"status": "FAIL", "issues": [f"File not found: {html_path}"]}

    content = html_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    issues: list[str] = []
    notes: list[str] = []

    # === TYPOGRAPHY CHECKS ===
    # Check for serif body font
    serif_fonts = ["garamond", "georgia", "baskerville", "crimson", "times"]
    has_serif_body = any(f in content_lower for f in serif_fonts)
    if not has_serif_body:
        issues.append("TYPOGRAPHY: No serif body font detected. Body must use serif (Georgia, Garamond, Libre Baskerville, etc.)")

    # Check for banned fonts
    banned_fonts = ["inter", "roboto", "arial", "helvetica", "calibri", "system-ui"]
    for font in banned_fonts:
        if f"font-family.*{font}" in content_lower or f"'{font}'" in content_lower:
            issues.append(f"TYPOGRAPHY: Banned font detected: {font}")

    # Check for Google Fonts link (ensures fonts load)
    if "fonts.googleapis.com" not in content:
        notes.append("TYPOGRAPHY: No Google Fonts link found. Ensure fonts are available locally or embedded.")

    # === LAYOUT CHECKS ===
    # Check for @page rules
    if "@page" not in content:
        issues.append("LAYOUT: Missing @page CSS rules for print formatting")

    # Check for page-break controls
    if "page-break" not in content and "break-" not in content:
        issues.append("LAYOUT: Missing page-break controls")

    # Check for orphans/widows
    if "orphans" not in content or "widows" not in content:
        issues.append("LAYOUT: Missing orphans/widows control on paragraphs")

    # Check for print-color-adjust
    if "print-color-adjust" not in content:
        notes.append("LAYOUT: Missing print-color-adjust: exact (backgrounds may not print)")

    # === COLOR & STYLE CHECKS ===
    # Count distinct colors (simplified check)
    hex_colors = set(re.findall(r'#[0-9a-fA-F]{6}', content))
    # Filter to significant colors (not near-white or near-black variants)
    significant = [c for c in hex_colors if c.lower() not in ('#ffffff', '#000000', '#fff', '#000')]
    if len(significant) > 15:
        notes.append(f"COLOR: {len(significant)} distinct hex colors found. Verify palette stays within 3-color limit.")

    # Check for neon/SaaS colors
    neon_patterns = [r'#[0-9a-f]{2}[0-9a-f]{2}ff', r'#ff[0-9a-f]{2}[0-9a-f]{2}']
    for pattern in neon_patterns:
        if re.search(pattern, content_lower):
            notes.append("COLOR: Potentially bright/neon color detected. Verify it's intentional.")

    # === CONTENT CHECKS ===
    # Check for AI filler phrases
    for phrase in AI_FILLER_PHRASES:
        if phrase in content_lower:
            issues.append(f"CONTENT: AI filler phrase detected: \"{phrase}\"")

    # Check for excessive bullet lists
    list_items = content.count("<li")
    list_groups = content.count("<ul") + content.count("<ol")
    if list_groups > 0 and list_items / max(list_groups, 1) > 7:
        notes.append(f"CONTENT: Average {list_items / list_groups:.1f} items per list. Max recommended is 5.")

    # Check for repetitive section structure
    h2_count = content.count("<h2")
    h3_count = content.count("<h3")
    if h2_count > 0 and h3_count > 0:
        notes.append(f"CONTENT: {h2_count} H2 sections, {h3_count} H3 subsections. Verify structural variety.")

    # === STRUCTURAL CHECKS ===
    # Check for cover page
    if "cover" not in content_lower:
        issues.append("STRUCTURE: No cover page detected")

    # Check for images (billboard variants)
    img_count = content.count("<img")
    if img_count < 5:
        issues.append(f"STRUCTURE: Only {img_count} images found. Expected 5+ (billboard variants + logo)")

    # Check for figure captions
    figcaption_count = content.count("<figcaption")
    if figcaption_count < 5:
        notes.append(f"STRUCTURE: {figcaption_count} figure captions found. Expected 5 (one per variant).")

    # Check for table
    if "<table" not in content:
        notes.append("STRUCTURE: No comparison table found. Expected comparative matrix.")

    # === THE SCREENSHOT TEST ===
    # Heuristic: check for variety in CSS classes (indicates design effort)
    classes = set(re.findall(r'class="([^"]+)"', content))
    if len(classes) < 15:
        notes.append("DESIGN: Limited CSS class variety. May look generic.")

    # === DETERMINE STATUS ===
    if issues:
        status = "FAIL"
    elif notes:
        status = "PASS WITH NOTES"
    else:
        status = "PASS"

    return {
        "status": status,
        "issues": issues,
        "notes": notes,
        "stats": {
            "images": img_count,
            "figure_captions": figcaption_count,
            "list_groups": list_groups,
            "list_items": list_items,
            "h2_sections": h2_count,
            "h3_subsections": h3_count,
            "css_classes": len(classes),
        },
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python src/validate.py <report_path>", file=sys.stderr)
        sys.exit(1)

    report_path = Path(sys.argv[1])

    # For PDF files, we can only do basic checks
    # For HTML files, we do full validation
    if report_path.suffix == ".html":
        result = validate_html(report_path)
    elif report_path.suffix == ".pdf":
        # Check if corresponding HTML exists
        html_path = report_path.with_suffix(".html")
        if html_path.exists():
            result = validate_html(html_path)
            result["notes"] = result.get("notes", []) + [
                "PDF validated via HTML source. Visual inspection recommended for final sign-off."
            ]
        else:
            result = {
                "status": "PASS WITH NOTES",
                "notes": ["PDF-only validation: manual visual inspection required."],
                "issues": [],
            }
    else:
        result = {
            "status": "FAIL",
            "issues": [f"Unsupported file type: {report_path.suffix}"],
        }

    # Output as JSON for programmatic consumption
    print(json.dumps(result, indent=2))

    # Also print human-readable summary to stderr
    print(f"\n{'=' * 50}", file=sys.stderr)
    print(f"QA Result: {result['status']}", file=sys.stderr)
    print(f"{'=' * 50}", file=sys.stderr)

    if result.get("issues"):
        print("\nISSUES:", file=sys.stderr)
        for issue in result["issues"]:
            print(f"  FAIL  {issue}", file=sys.stderr)

    if result.get("notes"):
        print("\nNOTES:", file=sys.stderr)
        for note in result["notes"]:
            print(f"  NOTE  {note}", file=sys.stderr)

    if result.get("stats"):
        print(f"\nStats: {json.dumps(result['stats'])}", file=sys.stderr)


if __name__ == "__main__":
    main()
