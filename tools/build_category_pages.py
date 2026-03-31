#!/usr/bin/env python3
"""
build_category_pages.py - Rebuild category landing pages from reviews_data.json.

Usage:
    python tools/build_category_pages.py
"""

import json
import os
import sys

CATEGORIES = {
    "ai-tools": {
        "name": "AI Tools",
        "emoji": "🤖",
        "intro": "Cutting-edge AI platforms, writing assistants, image generators, and productivity tools — tested and ranked by data.",
        "match": ["AI Tools"],
    },
    "software": {
        "name": "Software",
        "emoji": "💻",
        "intro": "VPNs, antivirus, hosting, streaming services, and more. Every software product independently tested for performance and value.",
        "match": ["Software"],
    },
    "tech-reviews": {
        "name": "Tech Reviews",
        "emoji": "⚡",
        "intro": "Cameras, drones, monitors, speakers, and the latest gadgets. Hands-on testing with real-world benchmarks.",
        "match": ["Tech Reviews"],
    },
    "home-office": {
        "name": "Home Office",
        "emoji": "🏠",
        "intro": "Ergonomic chairs, standing desks, keyboards, webcams, and everything you need for a productive workspace.",
        "match": ["Home Office"],
    },
    "fitness-tech": {
        "name": "Fitness Tech",
        "emoji": "🏋️",
        "intro": "Smartwatches, fitness trackers, rowing machines, massage guns, and under-desk treadmills — tested for accuracy and durability.",
        "match": ["Fitness Tech"],
    },
}

SVG_CART = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-shopping-cart w-2.5 h-2.5" aria-hidden="true"><circle cx="8" cy="21" r="1"></circle><circle cx="19" cy="21" r="1"></circle><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"></path></svg>'
SVG_TAG = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-tag w-3 h-3" aria-hidden="true"><path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"></path><circle cx="7.5" cy="7.5" r=".5" fill="currentColor"></circle></svg>'
SVG_STAR = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-star w-3 h-3 text-yellow-500 fill-yellow-500" aria-hidden="true"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path></svg>'
SVG_ARROW = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-arrow-right w-3 h-3" aria-hidden="true"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>'


def build_review_card(r):
    return f'''<a class="group block h-full" href="/reviews/{r["slug"]}">
<article class="bg-card border border-card-border rounded-2xl overflow-hidden hover:border-accent/50 transition-all duration-300 hover:-translate-y-1 h-full flex flex-col">
<div class="aspect-[1200/630] relative overflow-hidden bg-card-border">
<img src="{r["img"]}" alt="{r["alt"]}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy"/>
<span class="absolute top-3 right-3 bg-accent/90 text-black text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 z-10 shadow-lg">{SVG_CART}{r["deals"]} deals</span>
</div>
<div class="p-5 flex flex-col flex-1">
<div class="flex items-center gap-2 mb-2">
<span class="text-xs bg-accent/15 text-accent px-2 py-0.5 rounded-full flex items-center gap-1">{SVG_TAG}{r["cat"]}</span>
<span class="flex items-center gap-0.5 text-xs text-muted">{SVG_STAR}{r["rating"]}</span>
</div>
<h3 class="font-bold text-sm mb-2 group-hover:text-accent transition-colors line-clamp-2">{r["title"]}</h3>
<p class="text-xs text-muted line-clamp-2 flex-1">{r["desc"]}</p>
<div class="flex items-center justify-between mt-4 pt-3 border-t border-card-border">
<span class="text-xs text-muted">{r["date"]}</span>
<span class="text-xs text-accent flex items-center gap-1 group-hover:gap-2 transition-all">Read review {SVG_ARROW}</span>
</div>
</div>
</article>
</a>'''


def build_category_page(slug, cat_info, reviews):
    count = len(reviews)
    cards = "\n".join(build_review_card(r) for r in reviews)

    # Preload first 4 images
    preloads = ""
    for r in reviews[:4]:
        preloads += f'<link rel="preload" href="{r["img"]}" as="image"/>'

    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{cat_info["name"]} Reviews &amp; Comparisons — V3tt3d</title>
<meta name="description" content="Browse {count} AI-vetted, data-driven reviews in {cat_info["name"]}. {cat_info["intro"]}"/>
<meta name="robots" content="index, follow"/>
<meta property="og:title" content="{cat_info["name"]} Reviews — V3tt3d"/>
<meta property="og:description" content="{cat_info["intro"]}"/>
<meta property="og:url" content="https://v3tt3d.com/category/{slug}"/>
<meta property="og:site_name" content="V3tt3d"/>
<meta property="og:type" content="website"/>
<meta property="og:image" content="https://v3tt3d.com/images/og-image.svg"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{cat_info["name"]} Reviews — V3tt3d"/>
<meta name="twitter:description" content="{cat_info["intro"]}"/>
<link rel="icon" href="/images/favicon.svg" type="image/svg+xml"/>
<link rel="preload" href="/_next/static/media/797e433ab948586e-s.p.dbea232f.woff2" as="font" crossorigin="" type="font/woff2"/>
<link rel="preload" href="/_next/static/media/caa3a2e1cccd8315-s.p.853070df.woff2" as="font" crossorigin="" type="font/woff2"/>
{preloads}
<link rel="stylesheet" href="/_next/static/chunks/e35e1eb681718514.css"/>
<link rel="canonical" href="https://v3tt3d.com/category/{slug}"/>
</head>
<body>

<nav class="border-b border-card-border bg-card/80 backdrop-blur-md sticky top-0 z-50"><div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between"><a class="flex items-center gap-3 group" href="/"><div class="w-8 h-8 bg-accent rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform"><svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5"><path d="M8 16l5 5 10-12" stroke="#0a0a0a" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/></svg></div><span class="font-bold text-lg tracking-tight">V<span class="text-accent">3</span>tt<span class="text-accent">3</span>d</span></a><div class="flex items-center gap-6 text-sm"><a class="text-muted hover:text-foreground transition-colors" href="/">Reviews</a><a class="text-muted hover:text-foreground transition-colors" href="/deals.html">Deals</a><a class="text-muted hover:text-foreground transition-colors" href="/about.html">About</a></div></div></nav>

<main class="min-h-screen">
<div class="max-w-6xl mx-auto px-4 py-12">

<a class="inline-flex items-center gap-1 text-sm text-muted hover:text-accent transition-colors mb-8" href="/"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg> Back Home</a>

<!-- Hero -->
<section class="relative bg-gradient-to-br from-accent/10 via-card to-transparent border border-card-border rounded-2xl p-8 mb-10 overflow-hidden">
<div class="absolute top-0 right-0 w-48 h-48 bg-accent/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
<div class="relative">
<span class="text-4xl mb-3 block">{cat_info["emoji"]}</span>
<h1 class="text-3xl md:text-4xl font-bold tracking-tight mb-3">{cat_info["name"]}</h1>
<p class="text-muted max-w-2xl mb-4">{cat_info["intro"]}</p>
<div class="flex items-center gap-4 text-sm text-muted">
<span class="flex items-center gap-1.5 bg-card border border-card-border rounded-full px-3 py-1"><strong class="text-foreground">{count}</strong> reviews</span>
<span class="flex items-center gap-1.5 bg-card border border-card-border rounded-full px-3 py-1">Updated daily</span>
</div>
</div>
</section>

<!-- Review Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
{cards}
</div>

</div>
</main>

<!-- Footer -->
<footer class="max-w-6xl mx-auto px-4 py-8 mt-4 border-t border-card-border">
<div class="flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-muted">
<div class="flex items-center gap-2"><svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4"><rect width="32" height="32" rx="8" fill="#f97316"/><path d="M8 16l5 5 10-12" stroke="#0a0a0a" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/></svg><span class="font-bold text-foreground">V<span class="text-accent">3</span>tt<span class="text-accent">3</span>d</span><span>— AI-powered product intelligence</span></div>
<div class="flex items-center gap-4">
<a href="/about.html" class="hover:text-accent transition-colors">About</a>
<a href="/deals.html" class="hover:text-accent transition-colors">Deals</a>
<a href="mailto:hello@v3tt3d.com" class="hover:text-accent transition-colors">Contact</a>
</div>
</div>
</footer>

</body>
</html>'''


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)

    data_path = os.path.join(repo_root, 'reviews_data.json')
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found")
        sys.exit(1)

    with open(data_path, 'r', encoding='utf-8-sig') as f:
        reviews = json.load(f)

    cat_dir = os.path.join(repo_root, 'category')
    os.makedirs(cat_dir, exist_ok=True)

    for slug, cat_info in CATEGORIES.items():
        cat_reviews = [r for r in reviews if r.get("cat", "") in cat_info["match"]]
        html = build_category_page(slug, cat_info, cat_reviews)
        out_path = os.path.join(cat_dir, f"{slug}.html")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  {slug}.html — {len(cat_reviews)} reviews ({len(html):,} bytes)")

    print(f"\nDone! Built {len(CATEGORIES)} category pages.")
