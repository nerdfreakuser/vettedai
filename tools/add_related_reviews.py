#!/usr/bin/env python3
"""
add_related_reviews.py - Add 'You might also like' sections to review pages.

Reads reviews_data.json, finds 2-3 related reviews (same category), and injects
a related reviews section before the footer on pages that don't already have one.

Usage:
    python tools/add_related_reviews.py
"""

import json
import os
import sys
import re
import random

SVG_ARROW = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-arrow-right w-3 h-3"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>'


def build_related_section(related):
    cards = ""
    for r in related:
        cards += f'''<a class="group block h-full" href="/reviews/{r["slug"]}">
<div class="bg-card border border-card-border rounded-xl overflow-hidden hover:border-accent/50 transition-all">
<div class="aspect-[16/9] overflow-hidden bg-card"><img src="{r["img"]}" alt="{r["alt"]}" class="w-full h-full object-cover group-hover:scale-105 transition-transform" loading="lazy"/></div>
<div class="p-4"><h3 class="font-bold text-sm mb-1 group-hover:text-accent transition-colors line-clamp-2">{r["title"]}</h3><p class="text-xs text-muted line-clamp-2">{r["desc"]}</p>
<span class="text-xs text-accent flex items-center gap-1 mt-2">Read review {SVG_ARROW}</span></div>
</div>
</a>'''

    return f'''
<!-- Related Reviews (auto-generated) -->
<section class="max-w-4xl mx-auto px-4 pb-16">
<div class="pt-10 border-t border-card-border">
<h2 class="text-xl font-bold mb-6">You might also like</h2>
<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
{cards}
</div>
</div>
</section>
'''


def get_related(current_slug, current_cat, all_reviews, count=3):
    """Find related reviews from the same category, excluding current."""
    same_cat = [r for r in all_reviews if r["cat"] == current_cat and r["slug"] != current_slug]
    if len(same_cat) < count:
        # Fill with random other reviews
        others = [r for r in all_reviews if r["slug"] != current_slug and r not in same_cat]
        same_cat.extend(others[:count - len(same_cat)])
    random.seed(current_slug)  # Deterministic per page
    random.shuffle(same_cat)
    return same_cat[:count]


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)

    data_path = os.path.join(repo_root, 'reviews_data.json')
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found")
        sys.exit(1)

    with open(data_path, 'r', encoding='utf-8-sig') as f:
        all_reviews = json.load(f)

    reviews_dir = os.path.join(repo_root, 'reviews')
    added = 0
    skipped = 0
    already = 0

    # Build slug->cat mapping from data
    slug_to_cat = {r["slug"]: r.get("cat", "") for r in all_reviews}

    for fname in sorted(os.listdir(reviews_dir)):
        if not fname.endswith('.html'):
            continue

        fpath = os.path.join(reviews_dir, fname)
        slug = fname.replace('.html', '')

        with open(fpath, 'r', encoding='utf-8') as f:
            html = f.read()

        # Check if already has related section
        if 'You might also like' in html or 'Related Reviews' in html:
            already += 1
            continue

        cat = slug_to_cat.get(slug, "")
        if not cat:
            skipped += 1
            continue

        related = get_related(slug, cat, all_reviews, 3)
        if not related:
            skipped += 1
            continue

        section = build_related_section(related)

        # Insert before footer or before </main> or before </body>
        if '<footer' in html:
            html = html.replace('<footer', section + '<footer', 1)
        elif '</main>' in html:
            html = html.replace('</main>', section + '</main>', 1)
        elif '</body>' in html:
            html = html.replace('</body>', section + '</body>', 1)
        else:
            skipped += 1
            continue

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(html)
        added += 1
        print(f"  + {fname} ({len(related)} related)")

    print(f"\nDone! Added: {added}, Already had: {already}, Skipped: {skipped}")
