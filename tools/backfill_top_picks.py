#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path('/home/dan/.openclaw/workspace/vettedai-deploy')
DATA = ROOT / 'reviews_data.json'
REVIEWS = ROOT / 'reviews'

items = json.loads(DATA.read_text(encoding='utf-8-sig'))
updated = 0
for item in items:
    slug = item.get('slug')
    review_path = REVIEWS / f'{slug}.html'
    if not review_path.exists():
        continue
    html = review_path.read_text(encoding='utf-8')
    picks = re.findall(r'<span class="font-medium text-sm flex items-center gap-2">(.*?)</span>', html)
    picks = [re.sub(r'<[^>]+>', '', p).strip() for p in picks[:3]]
    if picks and item.get('top_picks') != picks:
        item['top_picks'] = picks
        updated += 1

DATA.write_text(json.dumps(items, indent=4) + '\n', encoding='utf-8')
print(f'Updated top_picks for {updated} entries.')
