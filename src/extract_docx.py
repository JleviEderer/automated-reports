import docx
import os
import glob

data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

for f in sorted(glob.glob(os.path.join(data_dir, '*.docx'))):
    basename = os.path.basename(f)
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
