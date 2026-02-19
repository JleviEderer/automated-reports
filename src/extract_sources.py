import docx
import os
import glob
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# Extract remaining docx files that had encoding errors
problem_files = [
    'Abaxx_Metcalf_Transcript_Summary_August2025.docx',
    'Abaxx_Problem_Solutions_Doc_September2025.docx',
    'Why Stablecoins Can\'t Meet Margin Requirements.docx',
    'Why does Legal Finality beat Ledger Finality.docx',
]

for basename in problem_files:
    f = os.path.join(data_dir, basename)
    print(f'\n===== {basename} =====')
    try:
        doc = docx.Document(f)
        text = '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
        if len(text) > 3000:
            print(text[:3000] + '\n... [truncated]')
        else:
            print(text)
    except Exception as e:
        print(f'ERROR: {e}')

# Extract PDFs using PyPDF2 or pdfplumber
print('\n\n===== PDF FILES =====')
try:
    import PyPDF2
    pdf_lib = 'PyPDF2'
except ImportError:
    try:
        import pdfplumber
        pdf_lib = 'pdfplumber'
    except ImportError:
        pdf_lib = None
        print('No PDF library available, trying pymupdf...')
        try:
            import fitz
            pdf_lib = 'fitz'
        except ImportError:
            print('No PDF library available at all')

for f in sorted(glob.glob(os.path.join(data_dir, '*.pdf'))):
    basename = os.path.basename(f)
    print(f'\n===== {basename} =====')
    try:
        if pdf_lib == 'PyPDF2':
            reader = PyPDF2.PdfReader(f)
            text = ''
            for i, page in enumerate(reader.pages[:10]):
                text += page.extract_text() or ''
            if len(text) > 3000:
                print(text[:3000] + '\n... [truncated]')
            else:
                print(text)
        elif pdf_lib == 'pdfplumber':
            with pdfplumber.open(f) as pdf:
                text = ''
                for page in pdf.pages[:10]:
                    text += (page.extract_text() or '') + '\n'
            if len(text) > 3000:
                print(text[:3000] + '\n... [truncated]')
            else:
                print(text)
        elif pdf_lib == 'fitz':
            doc = fitz.open(f)
            text = ''
            for i, page in enumerate(doc):
                if i >= 10:
                    break
                text += page.get_text()
            if len(text) > 3000:
                print(text[:3000] + '\n... [truncated]')
            else:
                print(text)
        else:
            print('No PDF library available')
    except Exception as e:
        print(f'ERROR: {e}')
