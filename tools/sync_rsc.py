#!/usr/bin/env python3
"""
sync_rsc.py - Synchronize RSC flight data with HTML content in index.html

This script detects review cards present in the HTML grid but missing from
the Next.js RSC (React Server Component) flight data, and adds the missing
RSC chunks so reviews don't flash-then-vanish on page hydration.

Run after adding any new review card to index.html:
    python tools/sync_rsc.py

How it works:
- The static HTML has review cards visible immediately on page load
- Next.js hydration replaces the HTML with what the RSC flight data says
- If a review card exists in HTML but NOT in RSC data, it vanishes after ~0.5s
- This script generates matching RSC chunks for any missing reviews
"""

import re
import sys
import os


def extract_card_data(card_html):
    """Extract review card data from an HTML card element."""
    data = {}

    m = re.search(r'href="/vettedai/reviews/([^"]+)"', card_html)
    data['slug'] = m.group(1) if m else None

    m = re.search(r'src="([^"]+)"', card_html)
    data['img'] = m.group(1) if m else ''

    m = re.search(r'alt="([^"]+)"', card_html)
    data['alt'] = m.group(1) if m else ''

    m = re.search(r'font-semibold text-lg[^>]*>([^<]+)<', card_html)
    data['title'] = m.group(1) if m else data['alt']

    m = re.search(r'line-clamp-2[^>]*>([^<]+)<', card_html)
    data['desc'] = m.group(1) if m else ''

    m = re.search(r'(\w{3} \d+, \d{4})', card_html)
    data['date'] = m.group(1) if m else 'Mar 28, 2026'

    m = re.search(r'>(\d+)<!-- --> deal', card_html)
    data['deals'] = int(m.group(1)) if m else 4

    m = re.search(r'</svg>([A-Za-z ]+)</span><span class="text-xs text-muted', card_html)
    data['cat'] = m.group(1).strip() if m else 'Tech Reviews'

    m = re.search(r'fill-yellow-500.*?</svg>(\d+\.?\d*)', card_html, re.DOTALL)
    data['rating'] = float(m.group(1)) if m else 4.8

    return data


def get_rsc_template(content):
    """Extract an existing RSC chunk to use as a template.
    
    Reads chunk 1b (or the first available review chunk) and returns
    the raw RSC string with placeholders for variable parts.
    """
    # Find an existing review card RSC chunk (e.g., chunk 1b)
    # Pattern: self.__next_f.push([1,"1b:[...]\n"])
    m = re.search(
        r'self\.__next_f\.push\(\[1,"([0-9a-f]+):(\[.*?/vettedai/reviews/.*?)\n"\]\)',
        content,
        re.DOTALL
    )
    if not m:
        return None, None, None

    ref_id = m.group(1)
    template_raw = m.group(2)

    # Extract the variable parts from this template
    slug_m = re.search(r'/vettedai/reviews/([^\\]+)\\', template_raw)
    if not slug_m:
        return None, None, None

    ref_slug = slug_m.group(1)
    return ref_id, template_raw, ref_slug


def build_chunk_from_template(template_raw, ref_slug, data):
    """Build a new RSC chunk by replacing variable parts in the template."""
    chunk = template_raw

    # Replace slug (appears multiple times)
    chunk = chunk.replace(ref_slug, data['slug'])

    return chunk


def build_chunk_from_scratch(data):
    """Build an RSC chunk from scratch using string template (no f-strings with braces)."""
    slug = data['slug']
    img = data['img']
    alt = data['alt']
    title = data['title']
    desc = data['desc']
    date = data['date']
    deals = data['deals']
    cat = data['cat']
    rating = data['rating']
    rating_str = str(int(rating)) if rating == int(rating) else str(rating)

    # Use a plain string template with .replace() to avoid f-string brace issues
    # This is the exact structure from existing RSC chunks (e.g., chunk 1b)
    T = '[\\"$\\",\\"$L2\\",\\"__SLUG__\\"'
    T += ',{\\"href\\":\\"/vettedai/reviews/__SLUG__\\"'
    T += ',\\"className\\":\\"group block h-full\\"'
    T += ',\\"children\\":[\\"$\\",\\"article\\",null'
    T += ',{\\"className\\":\\"bg-card border border-card-border rounded-2xl overflow-hidden hover:border-accent/50 transition-all duration-300 hover:-translate-y-1 h-full flex flex-col\\"'
    T += ',\\"children\\":'
    T += '[[\\"$\\",\\"div\\",null'
    T += ',{\\"className\\":\\"aspect-[1200/630] relative overflow-hidden bg-card-border\\"'
    T += ',\\"children\\":'
    T += '[[\\"$\\",\\"img\\",null'
    T += ',{\\"src\\":\\"__IMG__\\"'
    T += ',\\"alt\\":\\"__ALT__\\"'
    T += ',\\"className\\":\\"w-full h-full object-cover group-hover:scale-105 transition-transform duration-500\\"}]'
    T += ',[\\"$\\",\\"span\\",null'
    T += ',{\\"className\\":\\"absolute top-3 right-3 bg-accent/90 text-black text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 z-10 shadow-lg\\"'
    T += ',\\"children\\":'
    T += '[[\\"$\\",\\"svg\\",null'
    T += ',{\\"ref\\":\\"$undefined\\"'
    T += ',\\"xmlns\\":\\"http://www.w3.org/2000/svg\\"'
    T += ',\\"width\\":24,\\"height\\":24'
    T += ',\\"viewBox\\":\\"0 0 24 24\\"'
    T += ',\\"fill\\":\\"none\\"'
    T += ',\\"stroke\\":\\"currentColor\\"'
    T += ',\\"strokeWidth\\":2'
    T += ',\\"strokeLinecap\\":\\"round\\"'
    T += ',\\"strokeLinejoin\\":\\"round\\"'
    T += ',\\"className\\":\\"lucide lucide-shopping-cart w-2.5 h-2.5\\"'
    T += ',\\"aria-hidden\\":\\"true\\"'
    T += ',\\"children\\":'
    T += '[[\\"$\\",\\"circle\\",\\"jimo8o\\",{\\"cx\\":\\"8\\",\\"cy\\":\\"21\\",\\"r\\":\\"1\\"}]'
    T += ',[\\"$\\",\\"circle\\",\\"13723u\\",{\\"cx\\":\\"19\\",\\"cy\\":\\"21\\",\\"r\\":\\"1\\"}]'
    T += ',[\\"$\\",\\"path\\",\\"9zh506\\",{\\"d\\":\\"M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12\\"}]'
    T += ',\\"$undefined\\"]}]'
    T += ',__DEALS__'
    T += ',\\" deals\\"]}' 
    T += ']]}'
    T += ']'
    T += ',[\\"$\\",\\"div\\",null'
    T += ',{\\"className\\":\\"p-5 flex flex-col flex-1\\"'
    T += ',\\"children\\":'
    T += '[[\\"$\\",\\"div\\",null'
    T += ',{\\"className\\":\\"flex items-center gap-2 mb-2\\"'
    T += ',\\"children\\":'
    T += '[[\\"$\\",\\"span\\",null'
    T += ',{\\"className\\":\\"text-xs bg-accent/15 text-accent px-2 py-0.5 rounded-full flex items-center gap-1 z-10 relative\\"'
    T += ',\\"children\\":'
    T += '[[\\"$\\",\\"svg\\",null'
    T += ',{\\"ref\\":\\"$undefined\\"'
    T += ',\\"xmlns\\":\\"http://www.w3.org/2000/svg\\"'
    T += ',\\"width\\":24,\\"height\\":24'
    T += ',\\"viewBox\\":\\"0 0 24 24\\"'
    T += ',\\"fill\\":\\"none\\"'
    T += ',\\"stroke\\":\\"currentColor\\"'
    T += ',\\"strokeWidth\\":2'
    T += ',\\"strokeLinecap\\":\\"round\\"'
    T += ',\\"strokeLinejoin\\":\\"round\\"'
    T += ',\\"className\\":\\"lucide lucide-tag w-3 h-3\\"'
    T += ',\\"aria-hidden\\":\\"true\\"'
    T += ',\\"children\\":'
    T += '[[\\"$\\",\\"path\\",\\"vktsd0\\",{\\"d\\":\\"M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z\\"}]'
    T += ',[\\"$\\",\\"circle\\",\\"kqv944\\",{\\"cx\\":\\"7.5\\",\\"cy\\":\\"7.5\\",\\"r\\":\\".5\\",\\"fill\\":\\"currentColor\\"}]'
    T += ',\\"$undefined\\"]}]'
    T += ',\\"__CAT__\\"}]'
    T += ',[\\"$\\",\\"span\\",null'
    T += ',{\\"className\\":\\"text-xs text-muted flex items-center gap-1\\"'
    T += ',\\"children\\":'
    T += '[[\\"$\\",\\"svg\\",null'
    T += ',{\\"ref\\":\\"$undefined\\"'
    T += ',\\"xmlns\\":\\"http://www.w3.org/2000/svg\\"'
    T += ',\\"width\\":24,\\"height\\":24'
    T += ',\\"viewBox\\":\\"0 0 24 24\\"'
    T += ',\\"fill\\":\\"none\\"'
    T += ',\\"stroke\\":\\"currentColor\\"'
    T += ',\\"strokeWidth\\":2'
    T += ',\\"strokeLinecap\\":\\"round\\"'
    T += ',\\"strokeLinejoin\\":\\"round\\"'
    T += ',\\"className\\":\\"lucide lucide-star w-3 h-3 text-yellow-500 fill-yellow-500\\"'
    T += ',\\"aria-hidden\\":\\"true\\"'
    T += ',\\"children\\":'
    T += '[[\\"$\\",\\"path\\",\\"r04s7s\\",{\\"d\\":\\"M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z\\"}]'
    T += ',\\"$undefined\\"]}]'
    T += ',__RATING__]}]]}]'
    T += ',[\\"$\\",\\"h3\\",null'
    T += ',{\\"className\\":\\"font-semibold text-lg leading-snug mb-2 group-hover:text-accent transition-colors\\"'
    T += ',\\"children\\":\\"__TITLE__\\"}]'
    T += ',[\\"$\\",\\"p\\",null'
    T += ',{\\"className\\":\\"text-sm text-muted leading-relaxed line-clamp-2 mb-3 flex-1\\"'
    T += ',\\"children\\":\\"__DESC__\\"}]'
    T += ',[\\"$\\",\\"div\\",null'
    T += ',{\\"className\\":\\"flex items-center justify-between pt-2 border-t border-card-border\\"'
    T += ',\\"children\\":'
    T += '[[\\"$\\",\\"span\\",null'
    T += ',{\\"className\\":\\"text-xs text-muted\\"'
    T += ',\\"children\\":\\"__DATE__\\"}]'
    T += ',[\\"$\\",\\"span\\",null'
    T += ',{\\"className\\":\\"text-xs text-accent flex items-center gap-1 group-hover:gap-2 transition-all font-medium\\"'
    T += ',\\"children\\":'
    T += '[\\"Read Review \\"'
    T += ',[\\"$\\",\\"svg\\",null'
    T += ',{\\"ref\\":\\"$undefined\\"'
    T += ',\\"xmlns\\":\\"http://www.w3.org/2000/svg\\"'
    T += ',\\"width\\":24,\\"height\\":24'
    T += ',\\"viewBox\\":\\"0 0 24 24\\"'
    T += ',\\"fill\\":\\"none\\"'
    T += ',\\"stroke\\":\\"currentColor\\"'
    T += ',\\"strokeWidth\\":2'
    T += ',\\"strokeLinecap\\":\\"round\\"'
    T += ',\\"strokeLinejoin\\":\\"round\\"'
    T += ',\\"className\\":\\"lucide lucide-arrow-right w-3 h-3\\"'
    T += ',\\"aria-hidden\\":\\"true\\"'
    T += ',\\"children\\":[\\"$L42\\",\\"$L43\\",\\"$undefined\\"]}]]}]]}]]}]]}]}]'

    T = T.replace('__SLUG__', slug)
    T = T.replace('__IMG__', img)
    T = T.replace('__ALT__', alt)
    T = T.replace('__TITLE__', title)
    T = T.replace('__DESC__', desc)
    T = T.replace('__DATE__', date)
    T = T.replace('__DEALS__', str(deals))
    T = T.replace('__CAT__', cat)
    T = T.replace('__RATING__', rating_str)

    return T


def sync_rsc(html_path):
    """Main function to sync RSC data with HTML content."""
    print(f"Reading {html_path}...")
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find review grid section in HTML
    grid_start = content.find('id="reviews"')
    if grid_start < 0:
        print("ERROR: Could not find reviews grid section")
        return False

    grid_end = content.find('</section>', grid_start)
    grid_html = content[grid_start:grid_end]

    # Extract all review slugs from HTML grid
    html_slugs = list(dict.fromkeys(
        m.group(1) for m in re.finditer(r'href="/vettedai/reviews/([^"]+)"', grid_html)
    ))

    # Extract all review slugs from RSC flight data (individual chunks)
    rsc_slugs = list(dict.fromkeys(
        m.group(1) for m in re.finditer(
            r'self\.__next_f\.push\(\[1,"[0-9a-f]+:\[.*?/vettedai/reviews/([^\\]+)\\',
            content
        )
    ))

    # Also count the inline review in chunk 11 (first card in grid RSC data)
    inline_match = re.search(r'"11:\[.*?/vettedai/reviews/([^\\]+)\\', content)
    if inline_match and inline_match.group(1) not in rsc_slugs:
        rsc_slugs.append(inline_match.group(1))

    missing = [s for s in html_slugs if s not in rsc_slugs]

    print(f"HTML grid cards: {len(html_slugs)}")
    print(f"RSC data cards:  {len(rsc_slugs)}")
    print(f"Missing from RSC: {len(missing)}")

    if not missing:
        print("All reviews have RSC data. Nothing to fix!")
        return True

    for slug in missing:
        print(f"  - {slug}")

    # Try to use an existing RSC chunk as template (most reliable)
    template_result = get_rsc_template(content)
    use_template = template_result is not None and template_result[0] is not None
    if use_template:
        ref_id, template_raw, ref_slug = template_result
        print(f"\nUsing chunk {ref_id} ({ref_slug}) as template")

    # Find existing chunk IDs to avoid conflicts
    existing_ids = set(
        m.group(1) for m in re.finditer(
            r'self\.__next_f\.push\(\[1,"([0-9a-f]+):', content
        )
    )

    # Assign new chunk IDs
    next_id = 0x46
    chunk_map = {}
    for slug in missing:
        while format(next_id, 'x') in existing_ids:
            next_id += 1
        chunk_map[slug] = format(next_id, 'x')
        existing_ids.add(format(next_id, 'x'))
        next_id += 1

    # Generate RSC chunks for missing reviews
    new_scripts = []
    new_refs = []

    for slug in missing:
        chunk_id = chunk_map[slug]

        # Find the card HTML in the grid
        card_idx = content.find(f'/vettedai/reviews/{slug}', grid_start)
        a_start = content.rfind('<a ', 0, card_idx)
        a_end = content.find('</a>', card_idx)
        card_html = content[a_start:a_end + 4]

        data = extract_card_data(card_html)
        if not data['slug']:
            print(f"  WARNING: Could not extract data for {slug}, skipping")
            continue

        if use_template:
            rsc_content = build_chunk_from_template(template_raw, ref_slug, data)
            # Also need to replace title, desc, img, alt, cat, date, rating, deals
            # Extract those from the template chunk first
            ref_card_idx = content.find(f'/vettedai/reviews/{ref_slug}', grid_start)
            ref_a_start = content.rfind('<a ', 0, ref_card_idx)
            ref_a_end = content.find('</a>', ref_card_idx)
            ref_card = content[ref_a_start:ref_a_end + 4]
            ref_data = extract_card_data(ref_card)
            
            # Replace all variable fields in the template
            if ref_data['title'] and data['title']:
                rsc_content = rsc_content.replace(ref_data['title'], data['title'])
            if ref_data['desc'] and data['desc']:
                rsc_content = rsc_content.replace(ref_data['desc'], data['desc'])
            if ref_data['img'] and data['img']:
                rsc_content = rsc_content.replace(ref_data['img'], data['img'])
            if ref_data['alt'] and data['alt']:
                rsc_content = rsc_content.replace(ref_data['alt'], data['alt'])
            if ref_data['cat'] and data['cat']:
                old_cat = ',\\"' + ref_data['cat'] + '\\"'
                new_cat = ',\\"' + data['cat'] + '\\"'
                rsc_content = rsc_content.replace(old_cat, new_cat)
            if ref_data['date'] and data['date']:
                rsc_content = rsc_content.replace(ref_data['date'], data['date'])
            # deals (numeric)
            old_deals = '],' + str(ref_data['deals']) + ',\\" deals\\"'
            new_deals = '],' + str(data['deals']) + ',\\" deals\\"'
            rsc_content = rsc_content.replace(old_deals, new_deals)
            # rating (numeric)
            ref_r = str(ref_data['rating'])
            if ref_data['rating'] == int(ref_data['rating']):
                ref_r = str(int(ref_data['rating']))
            new_r = str(data['rating'])
            if data['rating'] == int(data['rating']):
                new_r = str(int(data['rating']))
            # Rating appears after the star SVG path, before ]}]]}]
            old_rating_str = '],' + ref_r + ']}'
            new_rating_str = '],' + new_r + ']}'
            rsc_content = rsc_content.replace(old_rating_str, new_rating_str, 1)
        else:
            rsc_content = build_chunk_from_scratch(data)

        script_tag = '<script>self.__next_f.push([1,"' + chunk_id + ':' + rsc_content + '\\n"])</script>'
        new_scripts.append(script_tag)
        new_refs.append(',\\"$L' + chunk_id + '\\"')

        print(f"  Generated RSC chunk {chunk_id} for {slug} (cat={data['cat']}, deals={data['deals']})")

    if not new_scripts:
        print("No chunks generated.")
        return False

    # 1. Add new references to the grid children array in chunk 11
    chunk11_start = content.find('"11:[')
    chunk11_end = content.find('</script>', chunk11_start)
    chunk11_text = content[chunk11_start:chunk11_end]
    
    # Find the last $L reference in chunk 11
    last_refs = re.findall(r',\\"\$L([0-9a-f]+)\\"', chunk11_text)
    if last_refs:
        last_id = last_refs[-1]
        old_pattern = f',\\"$L{last_id}\\"'
        # Find the specific occurrence at the end of the children array
        last_occurrence = chunk11_text.rfind(old_pattern)
        if last_occurrence >= 0:
            refs_str = ''.join(new_refs)
            new_chunk11 = (
                chunk11_text[:last_occurrence + len(old_pattern)] + 
                refs_str + 
                chunk11_text[last_occurrence + len(old_pattern):]
            )
            content = content[:chunk11_start] + new_chunk11 + content[chunk11_end:]
            print(f"\nUpdated chunk 11 grid children (added {len(new_refs)} refs after $L{last_id})")
    else:
        print("\nWARNING: Could not find grid children refs in chunk 11")

    # 2. Insert new script tags after the last existing RSC push
    last_push_idx = content.rfind('self.__next_f.push')
    insert_idx = content.find('</script>', last_push_idx) + len('</script>')
    scripts_str = ''.join(new_scripts)
    content = content[:insert_idx] + scripts_str + content[insert_idx:]
    print(f"Inserted {len(new_scripts)} new RSC script tags")

    # 3. Update review count in RSC data
    total_reviews = len(html_slugs)
    old_count_match = re.search(r'\]}\],(\d+),\\" reviews\\"', content)
    if old_count_match:
        old_count = int(old_count_match.group(1))
        if old_count != total_reviews:
            content = content.replace(
                f']}}],{old_count},\\" reviews\\"',
                f']}}],{total_reviews},\\" reviews\\"'
            )
            print(f"Updated RSC review count: {old_count} -> {total_reviews}")

    # Also update HTML review count
    old_html_count = re.search(r'>(\d+)<!-- --> reviews<', content)
    if old_html_count:
        old_c = old_html_count.group(1)
        if int(old_c) != total_reviews:
            content = content.replace(
                f'>{old_c}<!-- --> reviews<',
                f'>{total_reviews}<!-- --> reviews<'
            )
            print(f"Updated HTML review count: {old_c} -> {total_reviews}")

    # Save
    with open(html_path, 'w', encoding='utf-8', newline='') as f:
        f.write(content)

    print(f"\nDone! Saved {html_path}")
    return True


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    html_path = os.path.join(repo_root, 'index.html')

    if not os.path.exists(html_path):
        print(f"ERROR: {html_path} not found")
        sys.exit(1)

    success = sync_rsc(html_path)
    sys.exit(0 if success else 1)
