#!/usr/bin/env python3
import json, re, html, time
from pathlib import Path
from urllib.parse import urlparse, unquote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "archive_raw"
POSTS = ROOT / "_posts"
PAGES = ROOT / "travel"
RAW.mkdir(exist_ok=True)
POSTS.mkdir(exist_ok=True)
PAGES.mkdir(exist_ok=True)

CDX = "https://web.archive.org/cdx?url=zavalny.com/travel*&output=json&fl=timestamp,original,statuscode,mimetype,digest&filter=statuscode:200&collapse=urlkey&limit=1000"
UA = "Mozilla/5.0 (Hermes Agent archive recovery)"

def fetch(url, tries=4):
    last = None
    for i in range(tries):
        try:
            req = Request(url, headers={"User-Agent": UA})
            with urlopen(req, timeout=45) as r:
                return r.read()
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"Failed to fetch {url}")

def text_from_html(s):
    s = re.sub(r"(?is)<(script|style|noscript|svg|iframe)[^>]*>.*?</\1>", "", s)
    s = re.sub(r"(?is)<!--.*?-->", "", s)
    # Preserve structure before stripping tags
    s = re.sub(r"(?i)</(p|div|li|h[1-6]|blockquote|section|article|figure|figcaption|tr)>", "\n\n", s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)<li[^>]*>", "\n- ", s)
    s = re.sub(r"(?is)<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s+", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def title_of(doc):
    for pat in [r"(?is)<h1[^>]*>(.*?)</h1>", r"(?is)<title[^>]*>(.*?)</title>"]:
        m = re.search(pat, doc)
        if m:
            t = text_from_html(m.group(1))
            t = re.sub(r"\s*\|\s*Сайт Александра Завального.*$", "", t).strip()
            if t:
                return t
    return "Путешествие"

PCLOUD_BASE = "https://filedn.com/lVf3Vv8t6I3bfGwgdkdRRD4/zavalny_com"

def pcloud_dir(slug):
    return re.sub(r"-mode-(journal|gallery)$", "", slug)

def markdown_from_journal(doc, slug):
    """Extract old zavalny.com journal photos.

    The archived site used several templates:
    - older pages: many <div class="journal_photo"> blocks with Flickr data-original
    - newer pages: one .container.journal with journal_photo_description + img rows
    - newer pCloud mirror pages: data-src/src already points at filedn.com
    """
    try:
        from bs4 import BeautifulSoup, Tag
    except Exception:
        BeautifulSoup = None
        Tag = None

    def photo_url(raw_url):
        if not raw_url or raw_url.startswith("data:"):
            return None
        raw_url = raw_url.split("?")[0]
        if not re.search(r"\.(?:jpg|jpeg|png)$", raw_url, re.I):
            return None
        if "/covers/" in raw_url:
            return None
        if "filedn.com" in raw_url:
            return raw_url
        filename = raw_url.rsplit("/", 1)[-1]
        return f"{PCLOUD_BASE}/{pcloud_dir(slug)}/{filename}"

    if BeautifulSoup:
        soup = BeautifulSoup(doc, "html.parser")
        jps = soup.select("div.journal_photo")
        containers = jps if len(jps) > 2 else (soup.select(".container.journal") or jps)
        parts, seen, current_desc = [], set(), ""
        for cont in containers:
            children = [c for c in cont.children if isinstance(c, Tag)] if cont.select_one(".journal_photo_description") else [cont]
            for child in children:
                classes = child.get("class") or []
                if "journal_photo_description" in classes:
                    current_desc = text_from_html(str(child))
                    if current_desc:
                        parts.append(current_desc)
                    continue
                for img in child.find_all("img"):
                    for attr in ("data-src", "data-original", "src"):
                        url = photo_url(img.get(attr))
                        if not url or url in seen:
                            continue
                        seen.add(url)
                        alt = current_desc[:80] if current_desc else url.rsplit("/", 1)[-1]
                        parts.append(f"![{alt}]({url})")
        if seen:
            return "\n\n".join(parts).strip()

    blocks = re.findall(r'(?is)<div class="journal_photo"[^>]*>(.*?)(?=<div class="journal_photo"|</body>)', doc)
    parts = []
    for block in blocks:
        dm = re.search(r'(?is)<div class="journal_photo_description"[^>]*>(.*?)</div>', block)
        desc = text_from_html(dm.group(1)) if dm else ""
        urls = []
        for m in re.finditer(r'(?:data-src|data-original|src)="([^"]+?/(?:[^/"?#]+\.(?:jpg|jpeg|png)))"', block, re.I):
            url = photo_url(m.group(1))
            if url and url not in urls:
                urls.append(url)
        if desc:
            parts.append(desc)
        for url in urls:
            alt = desc[:80] if desc else url.rsplit("/", 1)[-1]
            parts.append(f"![{alt}]({url})")
    return "\n\n".join(parts).strip()

def main_content(doc, slug):
    journal = markdown_from_journal(doc, slug)
    if journal:
        return journal
    candidates = []
    for pat in [
        r"(?is)<article[^>]*>(.*?)</article>",
        r"(?is)<main[^>]*>(.*?)</main>",
        r"(?is)<div[^>]+class=[\"'][^\"']*(?:post|content|entry|page)[^\"']*[\"'][^>]*>(.*?)</div>",
        r"(?is)<body[^>]*>(.*?)</body>",
    ]:
        for m in re.finditer(pat, doc):
            txt = text_from_html(m.group(1))
            if len(txt) > 80:
                candidates.append(txt)
    if not candidates:
        return text_from_html(doc)
    # choose not just nav; longest usually contains post body
    return max(candidates, key=len)

def slug_from_original(orig):
    p = urlparse(orig)
    path = p.path.strip("/")
    if path == "travel" or not path:
        return "travel-index"
    slug = path.split("/")[-1] or path.split("/")[-2]
    slug = unquote(slug).lower()
    slug = re.sub(r"[^a-z0-9а-яё-]+", "-", slug, flags=re.I).strip("-")
    if p.query:
        slug += "-" + re.sub(r"[^a-z0-9а-яё-]+", "-", p.query.lower()).strip("-")
    return slug or "travel"

def markdown_escape_yaml(v):
    return json.dumps(v, ensure_ascii=False)

rows = json.loads(fetch(CDX).decode())[1:]
items = []
for ts, orig, code, mt, digest in rows:
    if "html" not in mt:
        continue
    slug = slug_from_original(orig)
    archive_url = f"https://web.archive.org/web/{ts}/{orig}"
    raw_url = f"https://web.archive.org/web/{ts}id_/{orig}"
    try:
        data = fetch(raw_url).decode("utf-8", "ignore")
    except Exception as e:
        print(f"WARN fetch failed {orig}: {e}")
        try:
            data = fetch(archive_url).decode("utf-8", "ignore")
        except Exception as e2:
            print(f"SKIP {orig}: {e2}")
            continue
    (RAW / f"{ts}-{slug}.html").write_text(data, encoding="utf-8")
    title = title_of(data)
    body = main_content(data, slug)
    # remove common site chrome fragments if present
    body = re.sub(r"(?is)<iframe[^>]*>.*?</iframe>", "", body)
    body = re.sub(r"(?is)<iframe[^>]*>|</iframe>", "", body)
    body = re.sub(r"(?im)^\s*(width|height|frameborder|src)=.*$", "", body)
    body = re.sub(r"Ждём карту Гугл!", "", body)
    body = re.sub(r"Сайт Александра Завального - про питание, спорт, путешествия и настольные игры", "", body)
    body = re.sub(r"(?s)×\s*\nEdit\s*\nClose\s*\nSave changes\s*\n×\s*\nПолучить подарочек.*?Смотреть галерею\s*", "", body)
    body = re.sub(r"(?is)^.*?Путешествия\s+", "", body) if slug != "travel-index" and len(body) > 1000 else body
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    body = re.sub(rf"^/?\s*{re.escape(title)}\s*\n", "", body).strip()
    date = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"
    md = f"---\nlayout: post\ntitle: {markdown_escape_yaml(title)}\ndate: {date} 00:00:00 +0000\ncategories: travel\nslug: {markdown_escape_yaml(slug)}\narchive_url: {markdown_escape_yaml(archive_url)}\noriginal_url: {markdown_escape_yaml(orig)}\n---\n\n> Восстановлено из [снимка Web Archive]({archive_url}) от {date}.\n\n{body}\n"
    # Avoid duplicate dates filenames by adding timestamp
    out = POSTS / f"{date}-{ts[8:]}-{slug}.md"
    out.write_text(md, encoding="utf-8")
    items.append({"title": title, "date": date, "slug": slug, "archive_url": archive_url, "original_url": orig})

# Travel landing page with recovered list. Jekyll builds links from site.posts.
index = "---\nlayout: page\ntitle: Путешествия\npermalink: /travel/\n---\n\n# Путешествия\n\nВосстановленные отчёты с прежнего сайта zavalny.com из Web Archive.\n\n<ul class=\"post-list\">\n{% assign travel_posts = site.posts | where_exp: \"post\", \"post.categories contains 'travel'\" %}\n{% for post in travel_posts %}\n  <li><a href=\"{{ post.url | relative_url }}\">{{ post.title }}</a> <span class=\"post-date\">{{ post.date | date: \"%Y-%m-%d\" }}</span></li>\n{% endfor %}\n</ul>\n"
(PAGES / "index.md").write_text(index, encoding="utf-8")
(ROOT / "archive_manifest.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Imported {len(items)} pages")
for it in items:
    print(f"- {it['date']} {it['title']} ({it['slug']})")
