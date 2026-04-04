#!/usr/bin/env python3
"""Extract Meridian module content from index.html into structured JSON files."""

import json
import os
import re
import sys
from copy import copy
from datetime import datetime, timezone

from bs4 import BeautifulSoup, NavigableString


def parse_modules_js(html_text):
    """Extract the JS `var modules = {...}` object and return as Python dict."""
    match = re.search(
        r'var modules\s*=\s*(\{.+?\});\s*\n',
        html_text,
        re.DOTALL,
    )
    if not match:
        sys.exit("ERROR: Could not find `var modules = {...}` in HTML")
    js_obj = match.group(1)
    # Convert JS object notation to JSON
    js_obj = js_obj.replace("'", '"')
    js_obj = re.sub(r',\s*([}\]])', r'\1', js_obj)
    # Add quotes around unquoted keys
    js_obj = re.sub(r'(\s)(\w+)\s*:', r'\1"\2":', js_obj)
    return json.loads(js_obj)


def inner_html(tag):
    """Get the inner HTML of a BeautifulSoup tag, trimmed."""
    return ''.join(str(child) for child in tag.children).strip()


def extract_goFAQ_key(element):
    """Extract the FAQ key from an onclick="goFAQ('key')" attribute."""
    onclick = element.get('onclick', '')
    m = re.search(r"goFAQ\('([^']+)'\)", onclick)
    return m.group(1) if m else None


def extract_home_page(soup, home_page_id):
    """Extract all structured content from a module's home page."""
    page = soup.find('div', id=home_page_id)
    if not page:
        sys.exit(f"ERROR: Could not find home page #{home_page_id}")

    result = {}

    # Landing intro
    intro = page.find('div', class_='landing-intro')
    if intro:
        p = intro.find('p')
        result['landing_intro'] = p.get_text() if p else ''
    else:
        result['landing_intro'] = ''

    # Section labels (collect all)
    section_labels = page.find_all('div', class_='section-label')
    result['checklist_section_label'] = section_labels[0].get_text() if len(section_labels) > 0 else ''
    result['escalation_section_label'] = section_labels[1].get_text() if len(section_labels) > 1 else ''

    # Checklist items
    checklist = []
    checklist_div = page.find('div', class_='checklist')
    if checklist_div:
        for i, item in enumerate(checklist_div.find_all('div', class_='check-item'), 1):
            checkbox = item.find('div', class_='check-box')
            text_div = item.find('div', class_='check-item-text')
            checklist.append({
                'item_id': checkbox.get('data-key', '') if checkbox else '',
                'position': i,
                'statement': text_div.get_text() if text_div else '',
                'faq_ref': extract_goFAQ_key(item),
            })
    result['checklist'] = checklist

    # Green zone
    green = page.find('div', class_='zone-block green')
    if green:
        zone_label = green.find('div', class_='zone-label')
        sp_tag = green.find('div', class_='smartphrase-tag')
        # Narrative is the <p> tag(s)
        narrative_parts = []
        for p in green.find_all('p'):
            narrative_parts.append(inner_html(p))
        # Extract smartphrase code from "SmartPhrase: .CODE"
        sp_text = sp_tag.get_text() if sp_tag else ''
        sp_match = re.search(r'SmartPhrase:\s*(\.\S+)', sp_text)
        result['green_zone'] = {
            'zone_label': zone_label.get_text() if zone_label else '',
            'narrative_html': '\n'.join(narrative_parts),
            'smartphrase': sp_match.group(1) if sp_match else sp_text,
        }
    else:
        result['green_zone'] = None

    # Escalation items
    escalation = []
    red = page.find('div', class_='zone-block red')
    if red:
        for i, item in enumerate(red.find_all('div', class_='zone-item'), 1):
            text_div = item.find('div', class_='zone-item-text')
            faq_key = extract_goFAQ_key(item)
            escalation.append({
                'item_id': faq_key or f'escalation-{i}',
                'position': i,
                'statement': text_div.get_text() if text_div else '',
                'faq_ref': faq_key,
            })
    result['escalation'] = escalation

    # Context strip (optional — only ADHD has one)
    cs = page.find('div', class_='context-strip')
    if cs:
        cs_label = cs.find('div', class_='cs-label')
        cs_p = cs.find('p')
        result['context_strip'] = {
            'label': cs_label.get_text() if cs_label else '',
            'text': cs_p.get_text() if cs_p else '',
        }
    else:
        result['context_strip'] = None

    # Footer note
    footer = page.find('div', class_='footer-note')
    result['footer_note'] = footer.get_text().strip() if footer else ''

    return result


def extract_faq_page(soup, page_id):
    """Extract FAQ content from a single FAQ page div."""
    page = soup.find('div', id=page_id)
    if not page:
        return None

    header = page.find('div', class_='faq-header')
    topic_div = header.find('div', class_='faq-topic') if header else None
    title_div = header.find('div', class_='faq-title') if header else None

    items = []
    for faq_item in page.find_all('div', class_='faq-item'):
        faq_q = faq_item.find('div', class_='faq-q')
        faq_a = faq_item.find('div', class_='faq-a')

        # Extract question text, stripping the chevron span
        if faq_q:
            # Work on a copy so we don't mutate the soup
            q_copy = copy(faq_q)
            chevron = q_copy.find('span', class_='faq-chevron')
            if chevron:
                chevron.decompose()
            question = q_copy.get_text().strip()
        else:
            question = ''

        answer_html = inner_html(faq_a).strip() if faq_a else ''

        items.append({
            'question': question,
            'answer_html': answer_html,
        })

    return {
        'topic': topic_div.get_text().strip() if topic_div else '',
        'title': title_div.get_text().strip() if title_div else '',
        'items': items,
    }


def build_module_json(module_key, module_meta, soup):
    """Assemble the complete JSON for a single module."""
    home_data = extract_home_page(soup, module_meta['homeId'])

    # Collect all faq_refs from checklist and escalation
    ref_to_origins = {}
    for item in home_data['checklist']:
        ref = item.get('faq_ref')
        if ref:
            ref_to_origins.setdefault(ref, []).append(item['item_id'])
    for item in home_data['escalation']:
        ref = item.get('faq_ref')
        if ref:
            ref_to_origins.setdefault(ref, []).append(item['item_id'])

    # Extract all FAQ pages
    faqs = []
    for faq_key, page_id in module_meta['pages'].items():
        faq_data = extract_faq_page(soup, page_id)
        if faq_data is None:
            print(f"  WARNING: FAQ page #{page_id} not found for key '{faq_key}'")
            continue
        faqs.append({
            'faq_id': faq_key,
            'topic': faq_data['topic'],
            'title': faq_data['title'],
            'referenced_by': ref_to_origins.get(faq_key, []),
            'items': faq_data['items'],
        })

    return {
        'schema_version': '1.0.0',
        'module_id': module_key,
        'default_title': module_meta['defaultTitle'],
        'landing_intro': home_data['landing_intro'],
        'checklist_section_label': home_data['checklist_section_label'],
        'checklist': home_data['checklist'],
        'green_zone': home_data['green_zone'],
        'escalation_section_label': home_data['escalation_section_label'],
        'escalation': home_data['escalation'],
        'context_strip': home_data['context_strip'],
        'footer_note': home_data['footer_note'],
        'faqs': faqs,
    }


def build_index_json(modules_meta):
    """Generate the module registry index."""
    entries = []
    for key, meta in modules_meta.items():
        title = meta['defaultTitle']
        parts = title.split(' \u2014 ', 1)  # split on em dash
        entries.append({
            'module_id': key,
            'title': parts[0] if len(parts) == 2 else title,
            'subtitle': parts[1] if len(parts) == 2 else '',
            'default_title': title,
            'status': 'published',
            'file': f'{key}.json',
        })
    return {
        'schema_version': '1.0.0',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'modules': entries,
    }


def validate(module_json):
    """Run validation checks on a module JSON and return issues."""
    issues = []
    faq_ids = {f['faq_id'] for f in module_json['faqs']}

    for item in module_json['checklist'] + module_json['escalation']:
        ref = item.get('faq_ref')
        if ref and ref not in faq_ids:
            issues.append(f"  MISSING FAQ: item '{item['item_id']}' references faq '{ref}' which was not extracted")

    return issues


def main():
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules')
    os.makedirs(out_dir, exist_ok=True)

    print(f"Reading {src}...")
    with open(src, 'r', encoding='utf-8') as f:
        html_text = f.read()

    print("Parsing HTML...")
    soup = BeautifulSoup(html_text, 'html.parser')

    print("Extracting JS modules object...")
    modules_meta = parse_modules_js(html_text)
    print(f"  Found {len(modules_meta)} modules: {', '.join(modules_meta.keys())}")

    # Extract each module
    all_ok = True
    for key, meta in modules_meta.items():
        print(f"\nExtracting module: {key}")
        module_json = build_module_json(key, meta, soup)

        # Validate
        issues = validate(module_json)
        if issues:
            all_ok = False
            for issue in issues:
                print(issue)

        # Summary
        n_check = len(module_json['checklist'])
        n_esc = len(module_json['escalation'])
        n_faq = len(module_json['faqs'])
        n_qa = sum(len(f['items']) for f in module_json['faqs'])
        print(f"  {n_check} checklist, {n_esc} escalation, {n_faq} FAQs ({n_qa} Q&A pairs)")
        print(f"  context_strip: {'yes' if module_json['context_strip'] else 'no'}")
        print(f"  smartphrase: {module_json['green_zone']['smartphrase'] if module_json['green_zone'] else 'none'}")

        # Write
        out_path = os.path.join(out_dir, f'{key}.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(module_json, f, indent=2, ensure_ascii=False)
        print(f"  -> {out_path}")

    # Write index
    index_json = build_index_json(modules_meta)
    index_path = os.path.join(out_dir, 'index.json')
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_json, f, indent=2, ensure_ascii=False)
    print(f"\n-> {index_path}")

    if all_ok:
        print("\nAll modules extracted and validated successfully.")
    else:
        print("\nExtraction complete with warnings (see above).")


if __name__ == '__main__':
    main()
