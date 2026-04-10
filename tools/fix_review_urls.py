#!/usr/bin/env python3
"""
fix_review_urls.py - Fix all review pages that have wrong URLs in JSON-LD,
duplicate canonical tags, or stale nerdfreakuser.github.io references.

Run: python tools/fix_review_urls.py
"""
import re
import os
import json
from pathlib import Path

DEPLOY_DIR = Path(__file__).parent.parent
REVIEWS_DIR = DEPLOY_DIR / "reviews"

WRONG_BASE = "https://nerdfreakuser.github.io/vettedai"
WRONG_BASE2 = "https://vettedai.netlify.app"
RIGHT_BASE = "https://v3tt3d.com"

def fix_review(html_path: Path) -> bool:
    """Fix a single review file. Returns True if changed."""
    content = html_path.read_text(encoding="utf-8")
    original = content

    # 1. Replace all nerdfreakuser URLs with v3tt3d.com
    content = content.replace(WRONG_BASE, RIGHT_BASE)

    # 2. Replace vettedai.netlify.app URLs with v3tt3d.com
    content = content.replace(WRONG_BASE2, RIGHT_BASE)

    # 3. Remove duplicate <link rel="canonical"> tags — keep only the LAST one
    # (Last one is the correct v3tt3d.com canonical added by the fix above)
    canonicals = re.findall(r'<link rel="canonical"[^>]*/>', content)
    if len(canonicals) > 1:
        # Remove all but the last
        for dup in canonicals[:-1]:
            content = content.replace(dup, "", 1)

    # 4. Remove duplicate twitter:image / twitter:title / twitter:description meta tags
    for meta_name in ["twitter:image", "twitter:title", "twitter:description"]:
        tags = re.findall(rf'<meta name="{meta_name}"[^>]*/>', content)
        if len(tags) > 1:
            for dup in tags[:-1]:
                content = content.replace(dup, "", 1)

    # 5. Remove duplicate og:url, og:image (non-width/height)
    for prop in ["og:url"]:
        tags = re.findall(rf'<meta property="{prop}"[^>]*/>', content)
        if len(tags) > 1:
            for dup in tags[:-1]:
                content = content.replace(dup, "", 1)

    # 6. Fix | VettedAI in page titles — should be | V3tt3d
    content = re.sub(r'(<title>.*?) \| VettedAI(</title>)', r'\1 | V3tt3d\2', content)

    # 7. Fix author name in JSON-LD: "VettedAI" → "V3tt3d"
    # Be careful not to change org names inside string values unintentionally
    # Only fix the name field when it's "VettedAI" specifically
    content = content.replace('"name":"VettedAI"', '"name":"V3tt3d"')
    content = content.replace('"name": "VettedAI"', '"name": "V3tt3d"')

    if content != original:
        html_path.write_text(content, encoding="utf-8")
        return True
    return False


def main():
    review_files = sorted(REVIEWS_DIR.glob("*.html"))
    print(f"Scanning {len(review_files)} review files...")
    fixed = 0
    for p in review_files:
        if fix_review(p):
            print(f"  Fixed: {p.name}")
            fixed += 1
    print(f"\nDone. Fixed {fixed}/{len(review_files)} files.")


if __name__ == "__main__":
    main()
