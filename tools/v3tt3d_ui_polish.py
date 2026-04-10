#!/usr/bin/env python3
"""
v3tt3d_ui_polish.py - Click-driving UX polish for all V3tt3d static pages.

Applies shared CSS improvements plus hero/CTA/orientation patterns to every
review/comparison page and the core site pages (homepage, deals, about).

Run directly:    python tools/v3tt3d_ui_polish.py
Or from build:   python tools/build_homepage.py  (calls polish automatically)

Idempotent — safe to run repeatedly on already-patched pages.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / '_next/static/chunks/e35e1eb681718514.css'
INDEX = ROOT / 'index.html'
DEALS = ROOT / 'deals.html'
ABOUT = ROOT / 'about.html'
REVIEWS_DIR = ROOT / 'reviews'

# ── CSS polish ────────────────────────────────────────────────────────────────

CSS_SENTINEL = 'ux-skip-link'  # presence check

CSS_OLD = (
    ':root{--background:#0a0a0a;--foreground:#ededed;--accent:#f97316;'
    '--accent-light:#fb923c;--card:#141414;--card-border:#262626;--muted:#a3a3a3}'
    'body{background:var(--background);color:var(--foreground);'
    'font-family:var(--font-sans),Arial,Helvetica,sans-serif}'
    '.prose h2{margin-top:2rem;margin-bottom:.75rem;font-size:1.5rem;font-weight:700}'
    '.prose h3{margin-top:1.5rem;margin-bottom:.5rem;font-size:1.25rem;font-weight:600}'
    '.prose p{color:#d4d4d4;margin-bottom:1rem;line-height:1.75}'
    '.prose ul,.prose ol{color:#d4d4d4;margin-bottom:1rem;padding-left:1.5rem}'
    '.prose li{margin-bottom:.25rem}'
    '.prose strong{color:#fff}'
    '.prose table{border-collapse:collapse;width:100%;margin:1.5rem 0}'
    '.prose th,.prose td{text-align:left;border:1px solid #333;padding:.5rem 1rem}'
    '.prose th{background:#1a1a1a;font-weight:600}'
    '.prose blockquote{border-left:3px solid var(--accent);color:#a3a3a3;padding-left:1rem;font-style:italic}'
)

CSS_NEW = (
    ':root{--background:#0a0a0a;--foreground:#ededed;--accent:#f97316;'
    '--accent-light:#fb923c;--card:#141414;--card-border:#262626;--muted:#a3a3a3;'
    '--hero-glow:rgba(249,115,22,.18);--shadow-soft:0 18px 60px rgba(0,0,0,.28);'
    '--shadow-card:0 12px 38px rgba(0,0,0,.22)}'
    'html{scroll-behavior:smooth}'
    'body{background:radial-gradient(circle at top,var(--hero-glow),transparent 32%),var(--background);'
    'color:var(--foreground);font-family:var(--font-sans),Arial,Helvetica,sans-serif;'
    'text-rendering:optimizeLegibility}'
    '::selection{background:rgba(249,115,22,.35);color:#fff}'
    'nav{border-bottom-color:rgba(255,255,255,.06)!important;'
    'background:rgba(10,10,10,.72)!important;backdrop-filter:blur(18px)!important;'
    'box-shadow:0 10px 30px rgba(0,0,0,.18)}'
    'main section{scroll-margin-top:5rem}'
    'main>div>section:first-of-type{padding-bottom:1rem}'
    'article.bg-card,section .bg-card,section .bg-gradient-to-r,section .bg-gradient-to-br,footer .border-t{box-shadow:var(--shadow-card)}'
    '.group article,.group>div,.group.block>div{transition:transform .25s ease,border-color .25s ease,box-shadow .25s ease}'
    '.group:hover article,.group:hover>div,.group.block:hover>div{box-shadow:var(--shadow-soft)}'
    '.text-muted{color:#b3b3b3}'
    '.prose h2{margin-top:2.25rem;margin-bottom:.9rem;font-size:1.6rem;font-weight:700;letter-spacing:-.02em}'
    '.prose h3{margin-top:1.6rem;margin-bottom:.55rem;font-size:1.25rem;font-weight:600}'
    '.prose p{color:#d4d4d4;margin-bottom:1rem;line-height:1.8}'
    '.prose ul,.prose ol{color:#d4d4d4;margin-bottom:1rem;padding-left:1.5rem}'
    '.prose li{margin-bottom:.4rem}'
    '.prose strong{color:#fff}'
    '.prose table{border-collapse:collapse;width:100%;margin:1.5rem 0;border-radius:1rem;overflow:hidden}'
    '.prose th,.prose td{text-align:left;border:1px solid #333;padding:.75rem 1rem}'
    '.prose th{background:#1a1a1a;font-weight:600}'
    '.prose blockquote{border-left:3px solid var(--accent);color:#a3a3a3;padding-left:1rem;font-style:italic}'
    # ── ux helpers ──
    '.ux-skip-link{position:absolute;left:1rem;top:-3rem;z-index:100;background:var(--accent);'
    'color:#111;padding:.7rem 1rem;border-radius:.75rem;font-weight:700;transition:top .2s ease}'
    '.ux-skip-link:focus{top:1rem}'
    '.ux-stat-row{display:flex;flex-wrap:wrap;justify-content:center;gap:.75rem 1rem;margin-top:2rem}'
    '.ux-stat-pill{display:inline-flex;align-items:center;gap:.55rem;padding:.72rem 1rem;'
    'border:1px solid rgba(249,115,22,.18);border-radius:999px;'
    'background:rgba(20,20,20,.78);box-shadow:0 8px 24px rgba(0,0,0,.18)}'
    '.ux-hero-actions{display:flex;flex-wrap:wrap;justify-content:center;gap:1rem;margin-top:2rem}'
    '.ux-btn-primary,.ux-btn-secondary{display:inline-flex;align-items:center;'
    'justify-content:center;gap:.6rem;padding:.9rem 1.25rem;border-radius:.9rem;font-weight:700;transition:all .2s ease}'
    '.ux-btn-primary{background:var(--accent);color:#111;box-shadow:0 12px 28px rgba(249,115,22,.22)}'
    '.ux-btn-primary:hover{transform:translateY(-1px);background:var(--accent-light)}'
    '.ux-btn-secondary{border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03);color:var(--foreground)}'
    '.ux-btn-secondary:hover{border-color:rgba(249,115,22,.35);color:var(--accent)}'
    '.ux-section-heading{display:flex;align-items:end;justify-content:space-between;gap:1rem;flex-wrap:wrap;margin-bottom:1.25rem}'
    '.ux-section-heading h2,.ux-section-heading h3{margin:0}'
    '.ux-kicker{display:inline-flex;align-items:center;gap:.45rem;padding:.35rem .75rem;'
    'border-radius:999px;border:1px solid rgba(249,115,22,.22);background:rgba(249,115,22,.08);'
    'color:var(--accent);font-size:.78rem;font-weight:700;letter-spacing:.03em;text-transform:uppercase}'
    '.ux-info-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem;margin:1.5rem 0 0}'
    '.ux-info-card{padding:1.1rem 1rem;border:1px solid rgba(255,255,255,.06);border-radius:1rem;'
    'background:linear-gradient(180deg,rgba(255,255,255,.03),rgba(255,255,255,.015))}'
    '.ux-info-card strong{display:block;font-size:.95rem;margin-bottom:.35rem}'
    '.ux-page-anchor{display:inline-flex;align-items:center;gap:.5rem;color:var(--accent);font-weight:600}'
    '.ux-review-layout{position:relative}'
    '.ux-review-toc{margin:1.25rem 0 2rem;padding:1rem 1.1rem;'
    'border:1px solid rgba(249,115,22,.15);border-radius:1rem;background:rgba(20,20,20,.82)}'
    '.ux-review-toc h3{margin:0 0 .8rem 0;font-size:1rem}'
    '.ux-review-toc ul{list-style:none;padding:0;margin:0;display:grid;gap:.55rem}'
    '.ux-review-toc a{color:#d9d9d9}.ux-review-toc a:hover{color:var(--accent)}'
    '.ux-meta-strip{display:flex;flex-wrap:wrap;gap:.75rem;margin:1rem 0 1.5rem}'
    '.ux-meta-chip{display:inline-flex;align-items:center;gap:.45rem;padding:.5rem .8rem;'
    'border-radius:999px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.06);'
    'font-size:.82rem;color:#d8d8d8}'
    '.ux-audio-card{margin:1.5rem 0 2rem;padding:1rem 1rem 1.1rem;border-radius:1rem;'
    'border:1px solid rgba(249,115,22,.14);background:linear-gradient(135deg,rgba(249,115,22,.09),rgba(20,20,20,.92))}'
    '.ux-affiliate-card{margin:0 0 1.5rem;padding:1rem;border-radius:1rem;'
    'border:1px solid rgba(255,255,255,.06);background:rgba(255,255,255,.03)}'
    'footer input[type=email]{min-width:0}'
    '@media (max-width:768px){'
    'nav .gap-6{gap:1rem}'
    '.ux-hero-actions{flex-direction:column}'
    '.ux-btn-primary,.ux-btn-secondary{width:100%}'
    '.ux-stat-row{justify-content:stretch}'
    '.ux-stat-pill{width:100%;justify-content:center}'
    '}'
)

# ── Comparison page TOC (no affiliate disclosure block in these pages) ────────

COMPARISON_TOC = (
    '<div class="ux-review-toc" style="margin-bottom:2rem">'
    '<h3>Quick navigation</h3>'
    '<ul>'
    '<li><a href="#comparison-start">Head-to-head breakdown</a></li>'
    '<li><a href="#audio-review">Listen to the review</a></li>'
    '<li><a href="#verdict">Verdict and recommendation</a></li>'
    '<li><a href="#related-reviews">Related reviews</a></li>'
    '</ul>'
    '</div>'
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _body_class_tag(text: str) -> str:
    """Return the first <body ...> tag variant found in text."""
    for variant in [
        '<body class="geist_a71539c9-module__T19VSG__variable geist_mono_8d43a2aa-module__8Li5zG__variable antialiased">',
        '<body>',
    ]:
        if variant in text:
            return variant
    return ''


def _inject_skip_link(text: str, target: str) -> str:
    tag = _body_class_tag(text)
    if not tag:
        return text
    return text.replace(tag, tag + f'\n<a class="ux-skip-link" href="{target}">Skip to main content</a>', 1)


# ── Patch functions ───────────────────────────────────────────────────────────

def patch_css() -> bool:
    text = CSS.read_text(errors='ignore')
    if CSS_SENTINEL in text:
        return False  # already applied
    if CSS_OLD not in text:
        # Try a softer match — patch without removing old block (append)
        text += '\n' + CSS_NEW
        CSS.write_text(text)
        return True
    CSS.write_text(text.replace(CSS_OLD, CSS_NEW, 1))
    return True


def patch_index() -> bool:
    text = INDEX.read_text(errors='ignore')
    changed = False

    if 'ux-skip-link' not in text:
        text = _inject_skip_link(text, '#reviews')
        changed = True

    if 'ux-hero-actions' not in text:
        # Insert CTA row + stat pills before the existing stat row
        old_stats = '<div class="flex items-center justify-center gap-6 text-sm text-muted">'
        if old_stats in text:
            text = text.replace(
                old_stats,
                '<div class="ux-hero-actions">'
                '<a class="ux-btn-primary" href="#reviews">Browse latest reviews</a>'
                '<a class="ux-btn-secondary" href="/deals.html">See live deals</a>'
                '</div>\n<div class="ux-stat-row">',
                1,
            )
            changed = True

    if 'ux-info-grid' not in text:
        # Append info-grid after the closing </div></div></div></section> of hero
        old_hero_end = '</div>\n</div>\n</div>\n</section>'
        if old_hero_end in text:
            text = text.replace(
                old_hero_end,
                '</div>\n'
                '<div class="ux-info-grid">'
                '<div class="ux-info-card"><strong>Quick take</strong>'
                '<span class="text-muted">Fast skimmable cards, deeper comparisons when you want them.</span></div>'
                '<div class="ux-info-card"><strong>What we optimise for</strong>'
                '<span class="text-muted">Clarity, price-awareness, and confidence before you click out.</span></div>'
                '<div class="ux-info-card"><strong>Best starting points</strong>'
                '<span class="text-muted">Browse reviews, explore categories, or go straight to live deals.</span></div>'
                '</div>\n</div>\n</div>\n</section>',
                1,
            )
            changed = True

    if 'ux-kicker' not in text:
        old_grid_header = '<section class="max-w-6xl mx-auto px-4 py-6" id="reviews">\n<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">'
        if old_grid_header in text:
            text = text.replace(
                old_grid_header,
                '<section class="max-w-6xl mx-auto px-4 py-6" id="reviews">\n'
                '<div class="ux-section-heading">'
                '<div><span class="ux-kicker">Latest reviews</span>'
                '<h2 class="text-2xl font-bold mt-3">Fresh AI-vetted picks</h2></div>'
                '<a class="ux-page-anchor" href="/deals.html">Prefer bargains? View deals \u2192</a>'
                '</div>\n'
                '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">',
                1,
            )
            changed = True

    if changed:
        INDEX.write_text(text)
    return changed


def patch_deals() -> bool:
    text = DEALS.read_text(errors='ignore')
    changed = False

    if 'ux-skip-link' not in text:
        text = _inject_skip_link(text, '#top-deals')
        changed = True

    if 'ux-info-grid' not in text:
        needle = 'AI-curated deals from our reviewed products. Real pricing, real affiliate links, updated continuously.</p>'
        if needle in text:
            text = text.replace(
                needle,
                needle + '\n'
                '<div class="ux-hero-actions">'
                '<a class="ux-btn-primary" href="#top-deals">See top deals</a>'
                '<a class="ux-btn-secondary" href="/">Back to reviews</a>'
                '</div>\n'
                '<div class="ux-info-grid">'
                '<div class="ux-info-card"><strong>Why this page exists</strong>'
                '<span class="text-muted">Fast deal discovery without digging through full reviews.</span></div>'
                '<div class="ux-info-card"><strong>What changes most</strong>'
                '<span class="text-muted">Pricing, coupon availability, and retailer callouts.</span></div>'
                '<div class="ux-info-card"><strong>Best use</strong>'
                '<span class="text-muted">Start here if price is the main decision driver.</span></div>'
                '</div>',
                1,
            )
            changed = True

    if 'id="top-deals"' not in text:
        needle2 = '<!-- Highlighted Deal -->\n<section class="max-w-6xl mx-auto px-4 mb-10">'
        if needle2 in text:
            text = text.replace(
                needle2,
                '<!-- Highlighted Deal -->\n'
                '<section class="max-w-6xl mx-auto px-4 mb-10" id="top-deals">'
                '<div class="ux-section-heading">'
                '<div><span class="ux-kicker">Best value now</span>'
                '<h2 class="text-2xl font-bold mt-3">Top deal worth checking first</h2></div>'
                '<a class="ux-page-anchor" href="/">Need more context? Read reviews \u2192</a>'
                '</div>',
                1,
            )
            changed = True

    if changed:
        DEALS.write_text(text)
    return changed


def patch_about() -> bool:
    text = ABOUT.read_text(errors='ignore')
    changed = False

    if 'ux-skip-link' not in text:
        text = _inject_skip_link(text, '#how-v3tt3d-works')
        changed = True

    if 'id="how-v3tt3d-works"' not in text:
        needle = '<div class="text-center mb-16"><h1 class="text-3xl md:text-4xl font-bold mb-4">How V3tt3d Works</h1>'
        if needle in text:
            text = text.replace(
                needle,
                '<div class="text-center mb-16" id="how-v3tt3d-works">'
                '<span class="ux-kicker">Transparency</span>'
                '<h1 class="text-3xl md:text-4xl font-bold mb-4 mt-3">How V3tt3d Works</h1>',
                1,
            )
            changed = True

    if 'ux-info-grid' not in text:
        needle2 = 'We built an autonomous AI engine that researches products, writes honest reviews, and keeps everything updated'
        if needle2 in text:
            # find end of that paragraph
            idx = text.find('</p>', text.find(needle2))
            if idx != -1:
                text = (
                    text[:idx + 4]
                    + '<div class="ux-info-grid">'
                    '<div class="ux-info-card"><strong>For readers</strong>'
                    '<span class="text-muted">Clearer context on how reviews are created and monetised.</span></div>'
                    '<div class="ux-info-card"><strong>For partners</strong>'
                    '<span class="text-muted">A faster way to understand the editorial and revenue model.</span></div>'
                    '<div class="ux-info-card"><strong>For trust</strong>'
                    '<span class="text-muted">More visible signals around methodology and disclosure.</span></div>'
                    '</div>'
                    + text[idx + 4:]
                )
                changed = True

    if changed:
        ABOUT.write_text(text)
    return changed


def _is_comparison_page(text: str) -> bool:
    """Heuristic: comparison pages open with <article class="max-w-4xl ..."."""
    return '<article class="max-w-4xl mx-auto px-4' in text


def patch_review_page(path: Path) -> bool:
    """Patch a single review or comparison page. Idempotent."""
    text = path.read_text(errors='ignore')
    changed = False
    comparison = _is_comparison_page(text)

    # 1. Skip link + layout wrapper
    if 'ux-skip-link' not in text:
        text = _inject_skip_link(text, '#review-content')
        changed = True

    if 'ux-review-layout' not in text:
        if comparison:
            text = text.replace(
                '<article class="max-w-4xl mx-auto px-4 pt-10 pb-16">',
                '<article class="max-w-4xl mx-auto px-4 pt-10 pb-16 ux-review-layout" id="review-content">',
                1,
            )
        else:
            text = text.replace(
                '<div class="max-w-4xl mx-auto px-4 py-12">',
                '<div class="max-w-4xl mx-auto px-4 py-12 ux-review-layout" id="review-content">',
                1,
            )
        changed = True

    # 2. TOC / orientation block
    if 'ux-review-toc' not in text:
        if comparison:
            # Inject after JSON-LD script block, before VS Hero div
            needle = '</script>\n\n<a class="inline-flex items-center'
            if needle in text:
                text = text.replace(needle, '</script>\n\n' + COMPARISON_TOC + '\n<a class="inline-flex items-center', 1)
                changed = True
        elif 'Affiliate Disclosure:' in text:
            text = text.replace(
                '</p></div><article><header class="mb-8">',
                '</p></div>'
                '<div class="ux-review-toc"><h3>Quick navigation</h3><ul>'
                '<li><a href="#top-pick">Top pick and summary</a></li>'
                '<li><a href="#audio-review">Listen to the review</a></li>'
                '<li><a href="#related-reviews">Related reviews</a></li>'
                '</ul></div>'
                '<article><header class="mb-8" id="top-pick">',
                1,
            )
            changed = True

    # 3. Affiliate card styling
    if 'ux-affiliate-card' not in text and 'Affiliate Disclosure:' in text:
        text = text.replace(
            'bg-card border border-card-border rounded-xl p-4 mb-6 flex gap-3 items-start',
            'ux-affiliate-card bg-card border border-card-border rounded-xl p-4 mb-6 flex gap-3 items-start',
            1,
        )
        changed = True

    # 4. Audio review anchor
    if 'id="audio-review"' not in text and '<audio controls' in text:
        text = text.replace(
            '<audio controls class="w-full rounded-lg" style="height:40px;">',
            '<audio controls class="w-full rounded-lg" style="height:40px;" id="audio-review">',
            1,
        )
        changed = True

    # 5. Comparison page: anchor hero block for TOC jump
    if comparison and 'id="comparison-start"' not in text:
        needle = '<!-- VS Hero -->'
        if needle in text:
            text = text.replace(needle, '<!-- VS Hero -->\n<div id="comparison-start"></div>', 1)
            changed = True
        # Also anchor verdict section if present
        for verdict_needle in ['<h2>Verdict</h2>', '<h2>Our Verdict</h2>', '<h2>The Verdict</h2>']:
            if verdict_needle in text and 'id="verdict"' not in text:
                text = text.replace(verdict_needle, f'<h2 id="verdict">Verdict</h2>', 1)
                changed = True
                break

    # 6. Related reviews anchor
    if 'id="related-reviews"' not in text and ('Related Reviews' in text or 'You might also like' in text):
        for old_related in [
            '<section class="mt-16 pt-10 border-t border-card-border"><h2 class="text-xl font-bold mb-6">Related Reviews</h2>',
            '<section class="max-w-4xl mx-auto px-4 pb-16">\n<div class="pt-10 border-t border-card-border">\n<h2 class="text-xl font-bold mb-6">You might also like</h2>',
        ]:
            if old_related in text:
                text = text.replace(old_related, old_related.replace(
                    '<section', '<section id="related-reviews"', 1), 1)
                changed = True
                break

    if changed:
        path.write_text(text)
    return changed


def patch_all_reviews() -> dict:
    results = {'changed': [], 'already_done': [], 'skipped': []}
    for p in sorted(REVIEWS_DIR.glob('*.html')):
        try:
            if patch_review_page(p):
                results['changed'].append(p.stem)
            else:
                results['already_done'].append(p.stem)
        except Exception as e:
            results['skipped'].append(f'{p.stem}: {e}')
    return results


def run(verbose: bool = True) -> dict:
    summary = {}

    css_changed = patch_css()
    summary['css'] = 'patched' if css_changed else 'already_done'

    idx_changed = patch_index()
    summary['index'] = 'patched' if idx_changed else 'already_done'

    deals_changed = patch_deals()
    summary['deals'] = 'patched' if deals_changed else 'already_done'

    about_changed = patch_about()
    summary['about'] = 'patched' if about_changed else 'already_done'

    review_results = patch_all_reviews()
    summary['reviews'] = review_results

    if verbose:
        print(f"CSS:    {summary['css']}")
        print(f"Index:  {summary['index']}")
        print(f"Deals:  {summary['deals']}")
        print(f"About:  {summary['about']}")
        changed = review_results['changed']
        done = review_results['already_done']
        skipped = review_results['skipped']
        print(f"Reviews patched: {len(changed)}  already done: {len(done)}  skipped: {len(skipped)}")
        if changed:
            print('  Patched: ' + ', '.join(changed))
        if skipped:
            print('  Skipped: ' + '; '.join(skipped))

    return summary


if __name__ == '__main__':
    verbose = '--quiet' not in sys.argv
    run(verbose=verbose)
