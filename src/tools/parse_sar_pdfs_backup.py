import os, json, traceback, time
from pathlib import Path
import fitz  # PyMuPDF
import pdfplumber
PROJECT = Path(__file__).resolve().parent.parent

SOURCE_DIR = Path(r'D:\LSH\合成孔径雷达任务规划')
PARSED_DIR = Path(r'PROJECT / "literature\parsed"')
FAILED_DIR = Path(r'PROJECT / "literature\failed"')
REPORT_PATH = Path(r'PROJECT / "literature\parsing_report.md"')

PARSED_DIR.mkdir(parents=True, exist_ok=True)
FAILED_DIR.mkdir(parents=True, exist_ok=True)

pdf_files = sorted(SOURCE_DIR.glob('*.pdf'))
total = len(pdf_files)
print(f'Found {total} PDF files in {SOURCE_DIR}')

summary = {
    'total': total,
    'parsed': 0,
    'failed': 0,
    'details': [],
    'start_time': time.time(),
}


def extract_with_fitz(path: Path):
    doc = fitz.open(path)
    meta = doc.metadata or {}
    text_parts = []
    for i, page in enumerate(doc):
        txt = page.get_text('text')
        if txt:
            text_parts.append(f'--- Page {i+1} ---\n' + txt)
    doc.close()
    return {
        'parser': 'PyMuPDF',
        'metadata': {
            'title': meta.get('title', ''),
            'author': meta.get('author', ''),
            'subject': meta.get('subject', ''),
            'keywords': meta.get('keywords', ''),
            'creator': meta.get('creator', ''),
            'producer': meta.get('producer', ''),
            'creation_date': meta.get('creationDate', ''),
            'mod_date': meta.get('modDate', ''),
            'page_count': len(fitz.open(path)),
        },
        'text': '\n\n'.join(text_parts),
    }


def extract_with_pdfplumber(path: Path):
    with pdfplumber.open(path) as pdf:
        text_parts = []
        for i, page in enumerate(pdf.pages):
            txt = page.extract_text() or ''
            if txt:
                text_parts.append(f'--- Page {i+1} ---\n' + txt)
        meta = pdf.metadata or {}
    return {
        'parser': 'pdfplumber',
        'metadata': {
            'title': meta.get('Title', ''),
            'author': meta.get('Author', ''),
            'subject': meta.get('Subject', ''),
            'keywords': meta.get('Keywords', ''),
            'creator': meta.get('Creator', ''),
            'producer': meta.get('Producer', ''),
            'creation_date': meta.get('CreationDate', ''),
            'mod_date': meta.get('ModDate', ''),
            'page_count': len(pdf.pages),
        },
        'text': '\n\n'.join(text_parts),
    }


for idx, pdf_path in enumerate(pdf_files, 1):
    stem = pdf_path.stem
    out_json = PARSED_DIR / f'{stem}.json'
    fail_md = FAILED_DIR / f'{stem}.md'
    error_msg = None
    parser_used = None
    result = None

    try:
        try:
            result = extract_with_fitz(pdf_path)
            parser_used = 'PyMuPDF'
        except Exception as e1:
            try:
                result = extract_with_pdfplumber(pdf_path)
                parser_used = 'pdfplumber'
            except Exception as e2:
                raise RuntimeError(f'PyMuPDF failed: {e1}; pdfplumber failed: {e2}')

        if not result or not result.get('text'):
            raise RuntimeError('No text extracted from PDF')

        with open(out_json, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        summary['parsed'] += 1
        summary['details'].append({
            'file': pdf_path.name,
            'status': 'parsed',
            'parser': parser_used,
            'pages': result['metadata'].get('page_count', 0),
            'chars': len(result.get('text', '')),
            'title': result['metadata'].get('title', ''),
        })
    except Exception as e:
        error_msg = traceback.format_exc()
        summary['failed'] += 1
        summary['details'].append({
            'file': pdf_path.name,
            'status': 'failed',
            'error': str(e),
            'parser': parser_used,
        })
        with open(fail_md, 'w', encoding='utf-8') as f:
            f.write(f'# Failed: {pdf_path.name}\n\n')
            f.write(f'**Source:** `{pdf_path}`\n\n')
            f.write(f'**Parser tried:** {parser_used or "none"}\n\n')
            f.write(f'**Error:** {e}\n\n')
            f.write('```\n' + error_msg + '\n```\n')

    if idx % 20 == 0 or idx == total:
        print(f'Progress: {idx}/{total} (parsed={summary["parsed"]}, failed={summary["failed"]})')


summary['end_time'] = time.time()
summary['duration_seconds'] = round(summary['end_time'] - summary['start_time'], 2)

# Write report
report_lines = [
    '# SAR PDF Parsing Report',
    '',
    f'- **Source directory:** `{SOURCE_DIR}`',
    f'- **Parsed output:** `{PARSED_DIR}`',
    f'- **Failed output:** `{FAILED_DIR}`',
    f'- **Total files:** {summary["total"]}',
    f'- **Parsed:** {summary["parsed"]}',
    f'- **Failed:** {summary["failed"]}',
    f'- **Duration:** {summary["duration_seconds"]}s',
    '',
    '## Parsed files',
    '',
    '| # | File | Parser | Pages | Chars | Title |',
    '|---|------|--------|------:|------:|-------|',
]
for i, d in enumerate([d for d in summary['details'] if d['status']=='parsed'], 1):
    report_lines.append(
        f'| {i} | {d["file"]} | {d.get("parser","")} | {d.get("pages",0)} | {d.get("chars",0)} | {d.get("title","")} |'
    )

report_lines += [
    '',
    '## Failed files',
    '',
    '| # | File | Parser | Error |',
    '|---|------|--------|-------|',
]
for i, d in enumerate([d for d in summary['details'] if d['status']=='failed'], 1):
    report_lines.append(
        f'| {i} | {d["file"]} | {d.get("parser","")} | {d.get("error","")} |'
    )

REPORT_PATH.write_text('\n'.join(report_lines), encoding='utf-8')
print(f'Report written to {REPORT_PATH}')
print('Done.')
