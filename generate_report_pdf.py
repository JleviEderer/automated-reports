"""
Generate a professional PDF of the Strategic Complementarity Report.
Uses fpdf2's multi_cell with markdown support for reliable text rendering.
"""

import re
from fpdf import FPDF

MD_PATH = "Strategic_Complementarity_Report_Erebor_Abaxx.md"
PDF_PATH = "Strategic_Complementarity_Report_Erebor_Abaxx.pdf"

# Colours
NAVY = (13, 33, 55)
DARK_BLUE = (26, 82, 118)
DARK_TEXT = (26, 26, 26)
GREY_TEXT = (90, 106, 122)
WHITE = (255, 255, 255)
RULE_GREY = (213, 220, 228)
TABLE_HEADER_BG = (13, 33, 55)
TABLE_ALT_BG = (245, 247, 250)
QUOTE_BORDER = (26, 82, 118)
CODE_BG = (244, 246, 249)
CODE_BORDER = (220, 225, 232)

# Unicode -> Latin-1 safe
UNICODE_MAP = {
    "\u2014": " -- ", "\u2013": " - ", "\u2018": "'", "\u2019": "'",
    "\u201c": '"', "\u201d": '"', "\u2026": "...", "\u00a0": " ",
}

def sanitize(text):
    for char, repl in UNICODE_MAP.items():
        text = text.replace(char, repl)
    return text


def md_to_fpdf_markdown(text):
    """Convert standard markdown bold/italic to fpdf2 markdown syntax.
    fpdf2 uses **bold** (same), --italic-- (different from *italic*).
    """
    text = sanitize(text)
    # Convert *single asterisk italic* to --fpdf italic--
    # But avoid converting **bold** markers
    # First protect **bold**
    text = text.replace("**", "\x00BOLD\x00")
    # Convert *italic* to --italic--
    text = re.sub(r'\*([^*]+?)\*', r'--\1--', text)
    # Restore bold
    text = text.replace("\x00BOLD\x00", "**")
    return text


class ReportPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_y(8)
            self.set_font("Helvetica", "I", 7.5)
            self.set_text_color(*GREY_TEXT)
            self.cell(0, 5,
                      "Strategic Complementarity Report: Erebor Bank & Abaxx Technologies",
                      align="R")
            self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GREY_TEXT)
        self.cell(0, 10, str(self.page_no()), align="C")

    def hr(self):
        self.ln(4)
        y = self.get_y()
        self.set_draw_color(*RULE_GREY)
        self.set_line_width(0.3)
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(6)

    def heading(self, text, level):
        text = sanitize(text)
        if level == 1:
            self.ln(12)
            self.set_font("Helvetica", "B", 22)
            self.set_text_color(*NAVY)
            self.multi_cell(0, 9, text)
            self.ln(2)
        elif level == 2:
            self.ln(6)
            self.set_font("Helvetica", "B", 14)
            self.set_text_color(*NAVY)
            self.multi_cell(0, 7, text)
            y = self.get_y() + 1
            self.set_draw_color(*DARK_BLUE)
            self.set_line_width(0.5)
            self.line(self.l_margin, y, self.w - self.r_margin, y)
            self.ln(5)
        elif level == 3:
            self.ln(4)
            self.set_font("Helvetica", "B", 11.5)
            self.set_text_color(*DARK_BLUE)
            self.multi_cell(0, 6, text)
            self.ln(2)
        elif level == 4:
            self.ln(3)
            self.set_font("Helvetica", "B", 10.5)
            self.set_text_color(44, 62, 80)
            self.multi_cell(0, 5.5, text)
            self.ln(1.5)

    def body(self, text):
        text = md_to_fpdf_markdown(text)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*DARK_TEXT)
        self.multi_cell(0, 5, text, markdown=True)
        self.ln(2.5)

    def bullet(self, text):
        text = md_to_fpdf_markdown(text)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*DARK_TEXT)
        x0 = self.get_x()
        self.set_x(self.l_margin + 6)
        self.cell(4, 5, "-")
        self.multi_cell(self.w - self.l_margin - self.r_margin - 10, 5,
                        text, markdown=True)
        self.ln(1)

    def numbered(self, num, text):
        text = md_to_fpdf_markdown(text)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*DARK_TEXT)
        self.set_x(self.l_margin + 6)
        self.set_font("Helvetica", "B", 9.5)
        self.cell(6, 5, f"{num}.")
        self.set_font("Helvetica", "", 9.5)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 12, 5,
                        text, markdown=True)
        self.ln(1)

    def blockquote(self, text):
        text = md_to_fpdf_markdown(text)
        self.ln(3)
        y_start = self.get_y()
        self.set_x(self.l_margin + 8)
        self.set_font("Helvetica", "BI", 9.5)
        self.set_text_color(44, 62, 80)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 12, 5.5,
                        text, markdown=True)
        y_end = self.get_y() + 2
        self.set_draw_color(*QUOTE_BORDER)
        self.set_line_width(1.0)
        self.line(self.l_margin + 3, y_start, self.l_margin + 3, y_end)
        self.set_y(y_end)
        self.ln(3)

    def codeblock(self, text):
        text = sanitize(text)
        self.ln(2)
        lines = text.split("\n")
        line_h = 3.8
        block_h = len(lines) * line_h + 6
        y0 = self.get_y()
        w = self.w - self.l_margin - self.r_margin
        if y0 + block_h > self.h - self.b_margin:
            self.add_page()
            y0 = self.get_y()
        self.set_fill_color(*CODE_BG)
        self.set_draw_color(*CODE_BORDER)
        self.set_line_width(0.2)
        self.rect(self.l_margin, y0, w, block_h, style="DF")
        self.set_y(y0 + 3)
        self.set_font("Courier", "", 7.5)
        self.set_text_color(*DARK_TEXT)
        for line in lines:
            self.set_x(self.l_margin + 4)
            self.cell(w - 8, line_h, line)
            self.ln(line_h)
        self.ln(3)

    def render_table(self, headers, rows):
        self.ln(3)
        headers = [sanitize(h) for h in headers]
        rows = [[sanitize(c) for c in r] for r in rows]
        w = self.w - self.l_margin - self.r_margin
        n = len(headers)

        # Column widths
        if n == 2:
            cw = [w * 0.26, w * 0.74]
        elif n == 3:
            cw = [w * 0.20, w * 0.40, w * 0.40]
        else:
            cw = [w / n] * n

        line_h = 4.5

        # --- Header row ---
        self.set_fill_color(*TABLE_HEADER_BG)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 7.5)
        y_top = self.get_y()
        # Measure header height
        max_lines = 1
        for i, h in enumerate(headers):
            nb = self.multi_cell(cw[i] - 3, line_h, h.upper(),
                                 dry_run=True, output="LINES")
            max_lines = max(max_lines, len(nb))
        row_h = max_lines * line_h + 4
        self.rect(self.l_margin, y_top, w, row_h, style="F")
        self.set_text_color(*WHITE)
        for i, h in enumerate(headers):
            self.set_xy(self.l_margin + sum(cw[:i]) + 2, y_top + 2)
            self.multi_cell(cw[i] - 3, line_h, h.upper())
        self.set_y(y_top + row_h)

        # --- Data rows ---
        for ri, row in enumerate(rows):
            self.set_font("Helvetica", "", 8)
            # Measure row height
            max_lines = 1
            for i, cell in enumerate(row):
                nb = self.multi_cell(cw[i] - 4, line_h,
                                     md_to_fpdf_markdown(cell),
                                     dry_run=True, output="LINES",
                                     markdown=True)
                max_lines = max(max_lines, len(nb))
            row_h = max_lines * line_h + 3

            y_row = self.get_y()
            if y_row + row_h > self.h - self.b_margin:
                self.add_page()
                y_row = self.get_y()

            # Alternating background
            if ri % 2 == 1:
                self.set_fill_color(*TABLE_ALT_BG)
                self.rect(self.l_margin, y_row, w, row_h, style="F")

            # Bottom border
            self.set_draw_color(*RULE_GREY)
            self.set_line_width(0.15)
            self.line(self.l_margin, y_row + row_h,
                      self.l_margin + w, y_row + row_h)

            # Cell text
            for i, cell in enumerate(row):
                self.set_xy(self.l_margin + sum(cw[:i]) + 2, y_row + 1.5)
                if i == 0 and n > 1:
                    self.set_font("Helvetica", "B", 8)
                else:
                    self.set_font("Helvetica", "", 8)
                self.set_text_color(*DARK_TEXT)
                self.multi_cell(cw[i] - 4, line_h,
                                md_to_fpdf_markdown(cell), markdown=True)

            self.set_y(y_row + row_h)
        self.ln(3)

    def source_text(self, text):
        self.ln(4)
        self.set_draw_color(*RULE_GREY)
        self.set_line_width(0.3)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(4)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*GREY_TEXT)
        self.multi_cell(0, 3.5, sanitize(text))


# --- Markdown Parser ---

def parse_markdown(filepath):
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            blocks.append(("hr",))
            i += 1
            continue

        m = re.match(r'^(#{1,4})\s+(.*)', line)
        if m:
            blocks.append(("heading", len(m.group(1)), m.group(2).strip()))
            i += 1
            continue

        if stripped.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i].rstrip("\n"))
                i += 1
            i += 1
            blocks.append(("code", "\n".join(code_lines)))
            continue

        if "|" in stripped and i + 1 < len(lines) and \
                re.match(r'^\|[\s\-|]+\|', lines[i + 1].strip()):
            headers = [c.strip() for c in stripped.strip("|").split("|")]
            headers = [re.sub(r'\s*h$', '', h) for h in headers]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in
                          lines[i].strip().strip("|").split("|")]
                rows.append(cells)
                i += 1
            blocks.append(("table", headers, rows))
            continue

        if stripped.startswith(">"):
            q = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q.append(re.sub(r'^>\s*', '', lines[i].strip()))
                i += 1
            blocks.append(("blockquote", " ".join(q)))
            continue

        if re.match(r'^[-*]\s', stripped):
            items = []
            while i < len(lines):
                l = lines[i].strip()
                if re.match(r'^[-*]\s', l):
                    items.append(re.sub(r'^[-*]\s+', '', l))
                elif l and (l.startswith("  ") or l.startswith("\t")):
                    if items:
                        items[-1] += " " + l.strip()
                elif not l:
                    if i + 1 < len(lines) and re.match(r'^[-*]\s',
                                                        lines[i+1].strip()):
                        i += 1
                        continue
                    else:
                        break
                else:
                    break
                i += 1
            blocks.append(("bullets", items))
            continue

        if re.match(r'^\d+\.\s', stripped):
            items = []
            while i < len(lines):
                l = lines[i].strip()
                m2 = re.match(r'^\d+\.\s+(.*)', l)
                if m2:
                    items.append(m2.group(1))
                elif l and (l.startswith("  ") or l.startswith("\t")):
                    if items:
                        items[-1] += " " + l.strip()
                elif not l:
                    if i+1 < len(lines) and re.match(r'^\d+\.\s',
                                                      lines[i+1].strip()):
                        i += 1
                        continue
                    else:
                        break
                else:
                    break
                i += 1
            blocks.append(("numbered", items))
            continue

        para = []
        while i < len(lines):
            l = lines[i].strip()
            if (not l or l == "---" or l.startswith("#") or
                    l.startswith("|") or l.startswith(">") or
                    l.startswith("```") or re.match(r'^[-*]\s', l) or
                    re.match(r'^\d+\.\s', l)):
                break
            para.append(l)
            i += 1
        text = " ".join(para)
        if text.startswith("*Sources:") or text.startswith("*Sources"):
            blocks.append(("sources", text.strip("*")))
        else:
            blocks.append(("paragraph", text))

    return blocks


# --- Build PDF ---

def build_pdf(blocks, output_path):
    pdf = ReportPDF(orientation="P", unit="mm", format="Letter")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(left=22, top=18, right=22)
    pdf.add_page()

    is_first = True

    for block in blocks:
        kind = block[0]

        if kind == "heading":
            lvl, text = block[1], block[2]
            if is_first and lvl == 1:
                pdf.heading(text, 1)
                is_first = False
            else:
                pdf.heading(text, lvl)

        elif kind == "paragraph":
            text = block[1]
            if is_first:
                clean = text.replace("**", "")
                pdf.set_font("Helvetica", "", 9.5)
                pdf.set_text_color(*GREY_TEXT)
                pdf.cell(0, 6, sanitize(clean))
                pdf.ln(6)
                is_first = False
            else:
                pdf.body(text)

        elif kind == "hr":
            pdf.hr()

        elif kind == "table":
            pdf.render_table(block[1], block[2])

        elif kind == "bullets":
            for item in block[1]:
                pdf.bullet(item)
            pdf.ln(1.5)

        elif kind == "numbered":
            for idx, item in enumerate(block[1], 1):
                pdf.numbered(idx, item)
            pdf.ln(1.5)

        elif kind == "blockquote":
            pdf.blockquote(block[1])

        elif kind == "code":
            pdf.codeblock(block[1])

        elif kind == "sources":
            pdf.source_text(block[1])

    pdf.output(output_path)
    print(f"PDF written to {output_path}")


if __name__ == "__main__":
    blocks = parse_markdown(MD_PATH)
    build_pdf(blocks, PDF_PATH)
