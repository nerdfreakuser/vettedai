#!/usr/bin/env python3
from pathlib import Path
import re

REVIEWS_DIR = Path('/home/dan/.openclaw/workspace/vettedai-deploy/reviews')

changed = 0
for path in sorted(REVIEWS_DIR.glob('*.html')):
    text = path.read_text(encoding='utf-8')
    original = text

    m_h1 = re.search(r'<h1[^>]*>(.*?)</h1>', text, re.S)
    if m_h1:
        h1 = re.sub(r'<[^>]+>', '', m_h1.group(1)).strip()
        text = re.sub(r'<title>.*?</title>', f'<title>{h1} | V3tt3d</title>', text, count=1, flags=re.S)
        text = text.replace('<!-- -->VettedAI</span>', '<!-- -->V3tt3d</span>')

    if text != original:
        path.write_text(text, encoding='utf-8')
        changed += 1
        print(f'Fixed: {path.name}')

print(f'Updated {changed} review files.')
