# VettedAI Agent Guide — How to Add Content

This site is a **static Next.js export**. The HTML and the React Server Component (RSC) flight data must stay in sync. If they diverge, reviews will flash on page load then vanish.

---

## Architecture Overview

```
index.html
├── Static HTML (visible immediately on page load)
│   ├── Hero section (review count)
│   ├── Featured review card
│   ├── Category pills
│   └── Review grid (all review cards as <a> tags)
│
└── RSC flight data (<script>self.__next_f.push(...)</script> tags)
    ├── Chunk 0: page metadata
    ├── Chunk 11: review grid children array (references $L1b, $L1c, etc.)
    ├── Chunks 1b-3f+: individual review card RSC data
    └── Chunks 42-43: shared SVG path elements
```

**Key rule**: Every review card in the HTML grid **must** have a matching RSC chunk, otherwise React hydration removes it (~0.5s after page load).

---

## Adding a New Review — Step by Step

### Step 1: Create the review page HTML

Create `reviews/{slug}.html`. You can copy an existing review page, but you **MUST**:

1. Replace **all** content in the `<head>` (title, meta description, canonical URL, og tags)
2. Replace **all** content in the `<body>` HTML (article text, products, images)
3. Replace **all** content in the JSON-LD `<script type="application/ld+json">` schema
4. **Strip all `<script>self.__next_f.push(...)</script>` tags** from the review page — they contain stale template data and the page renders fine without them

### Step 2: Add the cover image

Place the cover image at `images/{slug}-cover.png` (1200×630px recommended).

### Step 3: Add the card to index.html

Insert a new `<a>` card element into the review grid in `index.html`. The grid is inside:
```html
<section id="reviews">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- cards go here -->
  </div>
</section>
```

Card template:
```html
<a class="group block h-full" href="/vettedai/reviews/{SLUG}">
  <article class="bg-card border border-card-border rounded-2xl overflow-hidden hover:border-accent/50 transition-all duration-300 hover:-translate-y-1 h-full flex flex-col">
    <div class="aspect-[1200/630] relative overflow-hidden bg-card-border">
      <img src="/vettedai/images/{SLUG}-cover.png" alt="{TITLE}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"/vettedai/>
      <span class="absolute top-3 right-3 bg-accent/90 text-black text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 z-10 shadow-lg">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-shopping-cart w-2.5 h-2.5" aria-hidden="true"><circle cx="8" cy="21" r="1"></circle><circle cx="19" cy="21" r="1"></circle><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"></path></svg>
        {DEAL_COUNT}<!-- --> deals
      </span>
    </div>
    <div class="p-5 flex flex-col flex-1">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-xs bg-accent/15 text-accent px-2 py-0.5 rounded-full flex items-center gap-1 z-10 relative">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-tag w-3 h-3" aria-hidden="true"><path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"></path><circle cx="7.5" cy="7.5" r=".5" fill="currentColor"></circle></svg>
          {CATEGORY}
        </span>
        <span class="text-xs text-muted flex items-center gap-1">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-star w-3 h-3 text-yellow-500 fill-yellow-500" aria-hidden="true"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path></svg>
          {RATING}
        </span>
      </div>
      <h3 class="font-semibold text-lg leading-snug mb-2 group-hover:text-accent transition-colors">{TITLE}</h3>
      <p class="text-sm text-muted leading-relaxed line-clamp-2 mb-3 flex-1">{DESCRIPTION}</p>
      <div class="flex items-center justify-between pt-2 border-t border-card-border">
        <span class="text-xs text-muted">{DATE}</span>
        <span class="text-xs text-accent flex items-center gap-1 group-hover:gap-2 transition-all font-medium">Read Review <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-arrow-right w-3 h-3" aria-hidden="true"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span>
      </div>
    </div>
  </article>
</a>
```

Categories: `Tech Reviews`, `Home Office`, `Fitness Tech`, `Software`, `AI Tools`

### Step 4: Sync RSC flight data (CRITICAL)

After adding the HTML card, run:

```bash
python tools/sync_rsc.py
```

This script:
- Detects review cards in the HTML grid that are missing from the RSC data
- Generates matching RSC chunks using an existing chunk as a template
- Adds `$L` references to the grid children array in RSC chunk 11
- Updates the review count in both HTML and RSC data
- Is idempotent — safe to run multiple times

### Step 5: Update supporting files

- `sitemap.xml` — add the new review URL
- `deals.html` — add deal cards if applicable
- `category/{cat}.html` — add to the relevant category page

### Step 6: Commit and push

```bash
git add -A
git commit -m "Daily review: {slug} (YYYY-MM-DD)"
git push origin main
```

---

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Skip `sync_rsc.py` | Review card flashes then vanishes | Run `python tools/sync_rsc.py` |
| Copy review HTML without stripping RSC scripts | Wrong content appears on review page | Remove all `<script>self.__next_f.push(...)` from review HTML |
| Copy review HTML without updating JSON-LD schema | Wrong structured data in search engines | Update the `<script type="application/ld+json">` block |
| Wrong review count in hero | Count doesn't match grid | `sync_rsc.py` fixes this automatically |

---

## File Structure

```
/
├── index.html              ← Homepage with review grid (HTML + RSC data)
├── reviews/
│   ├── {slug}.html         ← Individual review pages (HTML only, no RSC)
│   └── {slug}/             ← RSC data dirs (only for original 39 reviews)
├── images/
│   └── {slug}-cover.png    ← Cover images (1200x630)
├── category/
│   └── {cat}.html          ← Category listing pages
├── deals.html              ← Deals page
├── sitemap.xml             ← Sitemap
├── tools/
│   └── sync_rsc.py         ← RSC synchronization script (run after every new review)
└── AGENT_GUIDE.md          ← This file
```
