#!/usr/bin/env python3
"""
build_homepage.py - Build a clean index.html from review data.

No Next.js RSC flight data needed. Pure static HTML + existing Tailwind CSS.

Usage:
    python tools/build_homepage.py
"""

import json
import os
import sys
import re

# SVG icons used throughout the page
SVG_ZAP = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-zap w-5 h-5" aria-hidden="true"><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"></path></svg>'
SVG_BAR_CHART = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-bar-chart-3 w-4 h-4" aria-hidden="true"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M7 16h8"></path><path d="M7 11h12"></path><path d="M7 6h3"></path></svg>'
SVG_CLOCK = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-clock w-4 h-4" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'
SVG_SHIELD = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-shield-check w-4 h-4" aria-hidden="true"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path><path d="m9 12 2 2 4-4"></path></svg>'
SVG_CART = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-shopping-cart w-2.5 h-2.5" aria-hidden="true"><circle cx="8" cy="21" r="1"></circle><circle cx="19" cy="21" r="1"></circle><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"></path></svg>'
SVG_TAG = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-tag w-3 h-3" aria-hidden="true"><path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"></path><circle cx="7.5" cy="7.5" r=".5" fill="currentColor"></circle></svg>'
SVG_STAR = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-star w-3 h-3 text-yellow-500 fill-yellow-500" aria-hidden="true"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path></svg>'
SVG_ARROW = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-arrow-right w-3 h-3" aria-hidden="true"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>'
SVG_ARROW_LG = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-arrow-right w-4 h-4" aria-hidden="true"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>'
SVG_EXTERNAL = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-external-link w-3 h-3 text-accent shrink-0" aria-hidden="true"><path d="M15 3h6v6"></path><path d="M10 14 21 3"></path><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path></svg>'
SVG_TREND = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-trending-up w-5 h-5" aria-hidden="true"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline><polyline points="16 7 22 7 22 13"></polyline></svg>'
SVG_SHIELD_LG = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-shield w-5 h-5" aria-hidden="true"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path></svg>'
SVG_ZAP_SM = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-zap w-4 h-4" aria-hidden="true"><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"></path></svg>'
SVG_STAR_FEATURED = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-star w-3.5 h-3.5 text-yellow-500 fill-yellow-500" aria-hidden="true"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path></svg>'

CATEGORIES = [
    ("tech-reviews", "🎧", "Tech Reviews"),
    ("home-office", "🏠", "Home Office"),
    ("fitness-tech", "💪", "Fitness Tech"),
    ("software", "💻", "Software"),
    ("ai-tools", "🤖", "AI Tools"),
]

MONEY_PAGE_SLUGS = [
    "nordvpn-vs-expressvpn-2026",
    "best-vpn-services-2026",
    "best-password-managers-2026",
]

MONEY_PAGE_BADGES = {
    "nordvpn-vs-expressvpn-2026": "VPN showdown",
    "best-vpn-services-2026": "Best VPNs",
    "best-password-managers-2026": "Security picks",
}

MONEY_PAGE_REASONS = {
    "nordvpn-vs-expressvpn-2026": "Compare price, speed, and privacy before you buy.",
    "best-vpn-services-2026": "The definitive 2026 VPN ranking — with deals and discount links.",
    "best-password-managers-2026": "1Password, NordPass, Bitwarden and more — tested and ranked for 2026.",
}


NORDVPN_AFFILIATE = "https://go.nordvpn.net/aff_c?offer_id=15&aff_id=144442&url_id=902"


def build_deal_strip():
    """Build a high-visibility NordVPN deal strip above the fold."""
    return f'''<section class="max-w-6xl mx-auto px-4 pt-4 pb-2">
<a href="{NORDVPN_AFFILIATE}" target="_blank" rel="noopener sponsored" class="group block">
<div class="relative bg-gradient-to-r from-[#1a1a2e] via-[#16213e] to-[#0f3460] border border-accent/30 rounded-2xl px-6 py-4 hover:border-accent/60 transition-all duration-300 overflow-hidden">
<div class="absolute inset-0 bg-gradient-to-r from-accent/5 to-transparent"></div>
<div class="relative flex flex-col sm:flex-row items-center justify-between gap-4">
<div class="flex items-center gap-4">
<div class="flex-shrink-0 w-10 h-10 bg-accent/10 rounded-xl flex items-center justify-center border border-accent/20">
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-accent"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path><path d="m9 12 2 2 4-4"></path></svg>
</div>
<div>
<div class="flex items-center gap-2 mb-0.5">
<span class="text-[10px] uppercase tracking-[0.2em] text-accent font-bold">Today\'s Best Deal</span>
<span class="text-[10px] bg-accent/20 text-accent px-2 py-0.5 rounded-full font-semibold">Limited time</span>
</div>
<p class="text-sm font-bold text-white leading-tight">NordVPN — Up to 72% off + 3 months free <span class="text-accent">on 2-year plans</span></p>
<p class="text-xs text-slate-400 mt-0.5">Rated #1 VPN for speed &amp; privacy. 30-day money-back guarantee.</p>
</div>
</div>
<div class="flex-shrink-0">
<span class="inline-flex items-center gap-2 bg-accent text-black text-sm font-bold px-5 py-2.5 rounded-xl group-hover:bg-accent/90 transition-colors">
Get Deal
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
</span>
</div>
</div>
</div>
</a>
</section>'''


def build_review_card(r):
    """Build a single review card HTML."""
    return f'''<a class="group block h-full" href="/reviews/{r["slug"]}"><article class="bg-card border border-card-border rounded-2xl overflow-hidden hover:border-accent/50 transition-all duration-300 hover:-translate-y-1 h-full flex flex-col"><div class="aspect-[1200/630] relative overflow-hidden bg-card-border"><img src="{r["img"]}" alt="{r["alt"]}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"/><span class="absolute top-3 right-3 bg-accent/90 text-black text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 z-10 shadow-lg">{SVG_CART}{r["deals"]} deals</span></div><div class="p-5 flex flex-col flex-1"><div class="flex items-center gap-2 mb-2"><span class="text-xs bg-accent/15 text-accent px-2 py-0.5 rounded-full flex items-center gap-1 z-10 relative">{SVG_TAG}{r["cat"] or "Tech Reviews"}</span><span class="text-xs text-muted flex items-center gap-1">{SVG_STAR}{r["rating"]}</span></div><h3 class="font-semibold text-lg leading-snug mb-2 group-hover:text-accent transition-colors">{r["title"]}</h3><p class="text-sm text-muted leading-relaxed line-clamp-2 mb-3 flex-1">{r["desc"]}</p><div class="flex items-center justify-between pt-2 border-t border-card-border"><span class="text-xs text-muted">{r["date"]}</span><span class="text-xs text-accent flex items-center gap-1 group-hover:gap-2 transition-all font-medium">Read Review {SVG_ARROW}</span></div></div></article></a>'''


def build_featured_card(r):
    """Build the featured review section."""
    # Build top picks rows if available
    top_picks = r.get("top_picks", [])
    if top_picks:
        picks_html = "".join(
            f'<div class="flex items-center gap-2 text-sm truncate">{SVG_EXTERNAL}<span class="truncate">{pick}</span></div>'
            for pick in top_picks[:3]
        )
        picks_section = f'<div class="mt-4 pt-4 border-t border-card-border"><p class="text-xs text-muted mb-2 font-medium">Top Picks</p><div class="space-y-1.5">{picks_html}</div></div>'
    else:
        picks_section = ""
    return f'''<section class="max-w-6xl mx-auto px-4 pt-6 pb-2"><a class="group block" href="/reviews/{r["slug"]}"><div class="relative bg-card border border-card-border rounded-2xl overflow-hidden hover:border-accent/50 transition-all duration-300"><div class="md:flex"><div class="md:w-1/2 aspect-[1200/630] md:aspect-auto relative overflow-hidden bg-card-border"><img src="{r["img"]}" alt="{r["alt"]}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"/><span class="absolute top-4 left-4 bg-accent/90 text-black text-xs font-bold px-3 py-1 rounded-full">Featured Review</span></div><div class="md:w-1/2 p-6 md:p-8 flex flex-col justify-center"><div class="flex items-center gap-3 mb-3"><span class="text-xs bg-accent/15 text-accent px-3 py-1 rounded-full">{r["cat"] or "Tech Reviews"}</span><span class="text-xs text-muted flex items-center gap-1">{SVG_STAR_FEATURED}{r["rating"]}/5</span></div><h2 class="text-2xl md:text-3xl font-bold mb-3 group-hover:text-accent transition-colors leading-tight">{r["title"]}</h2><p class="text-muted leading-relaxed mb-4 line-clamp-2">{r["desc"]}</p><span class="inline-flex items-center gap-2 text-accent font-medium group-hover:gap-3 transition-all">Read Full Review {SVG_ARROW_LG}</span>{picks_section}</div></div></div></a></section>'''


def build_money_funnel(reviews):
    """Build a high-intent money page section near the top of the homepage."""
    review_map = {r.get("slug"): r for r in reviews}
    selected = [review_map[slug] for slug in MONEY_PAGE_SLUGS if slug in review_map]
    if not selected:
        return ""

    cards = []
    for r in selected:
        badge = MONEY_PAGE_BADGES.get(r["slug"], "Top pick")
        reason = MONEY_PAGE_REASONS.get(r["slug"], r["desc"])
        cards.append(
            f'''<a class="group block" href="/reviews/{r["slug"]}"><article class="h-full bg-card border border-card-border rounded-2xl p-5 hover:border-accent/50 transition-all duration-300 hover:-translate-y-1"><div class="flex items-center justify-between gap-3 mb-3"><span class="text-[11px] uppercase tracking-[0.18em] text-accent font-semibold">{badge}</span><span class="text-xs text-muted flex items-center gap-1">{SVG_STAR}{r["rating"]}</span></div><h3 class="text-lg font-bold leading-snug mb-2 group-hover:text-accent transition-colors">{r["title"]}</h3><p class="text-sm text-muted leading-relaxed mb-4">{reason}</p><div class="flex items-center justify-between pt-4 border-t border-card-border text-sm"><span class="text-muted">Read review</span><span class="text-accent font-medium flex items-center gap-2 group-hover:gap-3 transition-all">Open review {SVG_ARROW_LG}</span></div></article></a>'''
        )

    return f'''<section class="max-w-6xl mx-auto px-4 py-4"><div class="bg-card border border-card-border rounded-2xl p-6"><div class="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-5"><div><p class="text-xs uppercase tracking-[0.22em] text-accent font-semibold mb-2">Editor’s shortlist</p><h2 class="text-2xl font-bold leading-tight">Popular guides worth starting with</h2><p class="text-sm text-muted mt-2 max-w-2xl">Our most-read reviews in software, security, and online tools.</p></div><a href="/deals.html" class="inline-flex items-center gap-2 text-sm text-accent font-medium hover:gap-3 transition-all">See all deals {SVG_ARROW_LG}</a></div><div class="grid grid-cols-1 md:grid-cols-3 gap-4">{"".join(cards)}</div></div></section>'''


def build_page(reviews):
    """Build the complete index.html page."""
    count = len(reviews)
    # Prefer reviews with featured=True; fall back to most recent
    featured_list = [r for r in reviews if r.get('featured')]
    featured = featured_list[0] if featured_list else reviews[0]
    
    # Preload first 8 cover images
    preloads = ""
    for r in reviews[:8]:
        preloads += f'<link rel="preload" href="{r["img"]}" as="image"/>'

    cards = "\n".join(build_review_card(r) for r in reviews)
    
    cat_pills = ""
    for slug, emoji, name in CATEGORIES:
        cat_pills += f'<a class="text-xs bg-card border border-card-border rounded-full px-4 py-2 text-muted hover:text-accent hover:border-accent/30 transition-colors" href="/category/{slug}">{emoji} {name}</a>'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-8V3818FTLF"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-8V3818FTLF');</script>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>V3tt3d — AI-Powered Product Reviews &amp; Deals</title>
<meta name="description" content="Honest, AI-vetted product reviews and deals. Every product researched, compared, and rated by AI. No sponsored placements — just data-driven picks."/>
<meta name="robots" content="index, follow"/>
<meta property="og:title" content="V3tt3d — AI-Powered Product Reviews &amp; Deals"/>
<meta property="og:description" content="Every product researched, compared, and rated by AI. No sponsored placements — just data-driven picks that save you money."/>
<meta property="og:url" content="https://v3tt3d.com"/>
<meta property="og:site_name" content="V3tt3d"/>
<meta property="og:type" content="website"/>
<meta property="og:image" content="https://v3tt3d.com/images/og-image.svg"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="V3tt3d — AI-Powered Product Reviews"/>
<meta name="twitter:description" content="Every product researched, compared, and rated by AI. No sponsored placements — just data-driven picks."/>
<meta name="twitter:image" content="https://v3tt3d.com/images/og-image.svg"/>
<link rel="icon" href="/images/favicon.svg" type="image/svg+xml"/>
<link rel="preload" href="/_next/static/media/797e433ab948586e-s.p.dbea232f.woff2" as="font" crossorigin="" type="font/woff2"/>
<link rel="preload" href="/_next/static/media/caa3a2e1cccd8315-s.p.853070df.woff2" as="font" crossorigin="" type="font/woff2"/>
{preloads}
<link rel="stylesheet" href="/_next/static/chunks/e35e1eb681718514.css"/>
<link rel="canonical" href="https://v3tt3d.com"/>
</head>
<body>

<!-- Nav -->
<nav class="border-b border-card-border bg-card/80 backdrop-blur-md sticky top-0 z-50"><div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between"><a class="flex items-center gap-3 group" href="/"><div class="w-8 h-8 bg-accent rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform"><svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5"><path d="M8 16l5 5 10-12" stroke="#0a0a0a" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/></svg></div><span class="font-bold text-lg tracking-tight">V<span class="text-accent" style="display:inline-block;transform:scaleY(-1)">3</span>tt<span class="text-accent">3</span>d</span></a><div class="flex items-center gap-6 text-sm"><a class="text-muted hover:text-foreground transition-colors" href="/">Reviews</a><a class="text-muted hover:text-foreground transition-colors" href="/deals.html">Deals</a><a class="text-muted hover:text-foreground transition-colors" href="/about.html">About</a></div></div></nav>

<main class="min-h-screen">
<div>

<!-- Hero -->
<section class="relative overflow-hidden">
<div class="absolute inset-0 bg-gradient-to-b from-accent/5 via-transparent to-transparent"></div>
<div class="max-w-6xl mx-auto px-4 pt-16 pb-10 relative">
<div class="text-center max-w-3xl mx-auto">
<div class="inline-flex items-center gap-2 bg-accent/10 border border-accent/20 rounded-full px-4 py-1.5 text-sm text-accent mb-6">
<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5"><rect width="32" height="32" rx="8" fill="#f97316"/><path d="M8 16l5 5 10-12" stroke="#0a0a0a" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/></svg>AI-Powered Product Intelligence
</div>
<h1 class="text-4xl md:text-5xl font-bold tracking-tight mb-4 leading-tight">Buy smarter with AI-vetted reviews</h1>
<p class="text-lg text-muted max-w-2xl mx-auto mb-8">Every product researched, compared, and rated by AI. No sponsored placements. No BS. Just data-driven picks that save you money.</p>
<div class="flex items-center justify-center gap-6 text-sm text-muted">
<span class="flex items-center gap-1.5">{SVG_BAR_CHART}<strong>{count}</strong> reviews</span>
<span class="flex items-center gap-1.5">{SVG_CLOCK}Updated daily</span>
<span class="flex items-center gap-1.5">{SVG_SHIELD}No paid placements</span>
</div>
</div>
</div>
</section>

<!-- NordVPN Deal Strip -->
{build_deal_strip()}

<!-- Featured Review -->
{build_featured_card(featured)}

<!-- Money Funnel -->
{build_money_funnel(reviews)}

<!-- Category Pills -->
<section class="max-w-6xl mx-auto px-4 py-4">
<div class="flex flex-wrap gap-2">
{cat_pills}
</div>
</section>

<!-- Review Grid -->
<section class="max-w-6xl mx-auto px-4 py-6" id="reviews">
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
{cards}
</div>
</section>

<!-- Features -->
<section class="max-w-6xl mx-auto px-4 py-6">
<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
<div class="flex items-start gap-3 bg-card border border-card-border rounded-xl p-4">
<div class="text-accent mt-0.5">{SVG_TREND}</div>
<div><h3 class="font-bold text-sm mb-1">Data-Driven</h3><p class="text-xs text-muted">Every review backed by real research, specs, and price comparisons</p></div>
</div>
<div class="flex items-start gap-3 bg-card border border-card-border rounded-xl p-4">
<div class="text-accent mt-0.5">{SVG_SHIELD_LG}</div>
<div><h3 class="font-bold text-sm mb-1">Honest Reviews</h3><p class="text-xs text-muted">Real pros and cons — we never accept paid product placements</p></div>
</div>
<div class="flex items-start gap-3 bg-card border border-card-border rounded-xl p-4">
<div class="text-accent mt-0.5">{SVG_ZAP_SM}</div>
<div><h3 class="font-bold text-sm mb-1">Fresh Daily</h3><p class="text-xs text-muted">New reviews published every day, prices checked continuously</p></div>
</div>
</div>
</section>

<!-- Footer -->
<footer class="max-w-6xl mx-auto px-4 py-8 mt-4 border-t border-card-border">
<div class="flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-muted">
<div class="flex items-center gap-2"><svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4"><rect width="32" height="32" rx="8" fill="#f97316"/><path d="M8 16l5 5 10-12" stroke="#0a0a0a" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/></svg><span class="font-bold text-foreground">V<span class="text-accent" style="display:inline-block;transform:scaleY(-1)">3</span>tt<span class="text-accent">3</span>d</span><span>— AI-powered product intelligence</span></div>
<div class="flex items-center gap-4">
<a href="/about.html" class="hover:text-accent transition-colors">About</a>
<a href="/deals.html" class="hover:text-accent transition-colors">Deals</a>
<a href="mailto:hello@v3tt3d.com" class="hover:text-accent transition-colors">Contact</a>
</div>
</div>
</footer>

</div>
</main>

</body>
</html>'''


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    
    data_path = os.path.join(repo_root, 'reviews_data.json')
    if not os.path.exists(data_path):
        print(f"ERROR: {data_path} not found. Extract review data first.")
        sys.exit(1)
    
    with open(data_path, 'r', encoding='utf-8-sig') as f:
        reviews = json.load(f)
    
    print(f"Building homepage with {len(reviews)} reviews...")
    html = build_page(reviews)
    
    out_path = os.path.join(repo_root, 'index.html')
    with open(out_path, 'w', encoding='utf-8', newline='') as f:
        f.write(html)
    
    print(f"Done! Saved {out_path} ({len(html):,} bytes)")
