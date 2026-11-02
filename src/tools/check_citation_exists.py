#!/usr/bin/env python3
"""check_citation_exists.py — .bib citation existence + metadata gate.

Motivation: AI-assisted drafting has produced fabricated / mis-attributed
references in this project before (RDR-007, RDR-065: wrong venue, wrong scope,
title paraphrased into a claim the source never made).  Manual subagent
spot-checks caught them; this script makes the check repeatable.

For every bib entry it queries open bibliographic sources and asserts:
  * EXISTENCE  — the DOI resolves, or the arXiv id resolves, or the title is
                 found in Crossref.  Missing => hard failure (exit 1).
  * METADATA   — title / journal / year / volume / issue / pages / first-author
                 compared against the source of record.  Divergence => warning
                 only (exit unaffected); non-international venues and
                 forthcoming items legitimately differ.

Exit codes:
  0  all entries exist (metadata warnings allowed)
  1  at least one entry does not exist
  2  no entry found missing, but some lookups errored (network/quota) — retry

Stdlib only (urllib) — no venv, no third-party deps.

Usage:
  python src/tools/check_citation_exists.py                       # all papers
  python src/tools/check_citation_exists.py --bib <path.bib>
  python src/tools/check_citation_exists.py --only Ferrari2025 Wei2025MONP
  python src/tools/check_citation_exists.py --recheck             # ignore cache
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

UA = "planning-paper-citation-check/0.1 (mailto:noreply@example.org)"
CACHE_PATH = Path(tempfile.gettempdir()) / "planning-paper-citation-cache.json"

# token-set thresholds
TITLE_MATCH_MIN = 0.90   # containment ratio required for a title-only match
TITLE_JACCARD_MIN = 0.65  # ... and jaccard, so a short title cannot ride along
TITLE_WARN_MIN = 0.75    # below this => metadata warning

STOPWORDS = {
    "a", "an", "the", "of", "for", "on", "in", "to", "and", "or", "with",
    "from", "by", "at", "as", "is", "are", "using", "based", "via",
}


# ── bib parsing ─────────────────────────────────────────────────────────────

def strip_latex(value: str) -> str:
    """Braces/accents/escapes -> plain text suitable for comparison."""
    v = value
    # accent wrappers: {\^i} {\'e} {\"o} {\c{c}} {\v{s}} {\`a}
    v = re.sub(r"\\[a-zA-Z]?\s*\{([a-zA-Z])\}", r"\1", v)
    v = re.sub(r"\\([`'\"^~=.])\s*\{?([a-zA-Z])\}?", r"\2", v)
    v = re.sub(r"\\([`'\"^~=.])\s*([a-zA-Z])", r"\2", v)
    v = v.replace("~", " ")
    for cmd, rep in (
        ("\\&", "&"), ("\\%", "%"), ("\\_", "_"), ("\\$", "$"),
        ("\\aa", "a"), ("\\AA", "A"), ("\\ss", "ss"),
        ("\\o", "o"), ("\\O", "O"), ("\\l", "l"), ("\\L", "L"),
    ):
        v = v.replace(cmd, rep)
    v = re.sub(r"\\[a-zA-Z]+\s*", " ", v)   # drop remaining commands
    v = v.replace("{", "").replace("}", "")
    v = re.sub(r"\s+", " ", v)
    return v.strip()


from strip_tex_comments import strip_comments  # single implementation: the
# local copy treated "\\\\%" (escaped backslash then percent) as a literal
# percent, where an even backslash run means a real comment starts.


def _split_top_level(chunk: str, sep: str = ",") -> list[str]:
    parts, depth, quote, cur = [], 0, False, []
    for ch in chunk:
        if ch == '"':
            quote = not quote
        if not quote:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            elif ch == sep and depth == 0:
                parts.append("".join(cur))
                cur = []
                continue
        cur.append(ch)
    parts.append("".join(cur))
    return parts


def parse_bib(text: str) -> list[dict]:
    """Minimal brace-aware .bib parser. Returns [{type,key,fields}, ...]."""
    text = strip_comments(text)
    entries = []
    pos = 0
    header = re.compile(r"@(\w+)\s*\{")
    while True:
        m = header.search(text, pos)
        if not m:
            break
        etype = m.group(1).lower()
        start = m.end()
        depth = 1
        i = start
        while i < len(text) and depth > 0:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        body = text[start:i - 1]
        pos = i
        if etype in {"comment", "preamble", "string"}:
            continue
        fields_parts = _split_top_level(body)
        if not fields_parts:
            continue
        key = fields_parts[0].strip()
        fields = {}
        for chunk in fields_parts[1:]:
            if "=" not in chunk:
                continue
            name, _, val = chunk.partition("=")
            val = val.strip()
            if len(val) >= 2 and val[0] == "{" and val[-1] == "}":
                val = val[1:-1]
            elif len(val) >= 2 and val[0] == '"' and val[-1] == '"':
                val = val[1:-1]
            fields[name.strip().lower()] = val.strip()
        entries.append({"type": etype, "key": key, "fields": fields})
    return entries


def normalize_doi(raw: str) -> str:
    d = strip_latex(raw).strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    d = re.sub(r"^doi:\s*", "", d)
    return d.strip()


def normalize_arxiv(raw: str) -> str:
    a = strip_latex(raw).strip()
    a = re.sub(r"^arxiv:\s*", "", a, flags=re.I)
    a = re.sub(r"v\d+$", "", a)
    return a.strip()


_LATIN_FOLD = str.maketrans({
    "ı": "i", "ł": "l", "ø": "o", "đ": "d", "ß": "ss",
    "æ": "ae", "œ": "oe", "þ": "th", "ð": "d",
})


def tokens(s: str) -> set[str]:
    s = unicodedata.normalize("NFKD", strip_latex(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.translate(_LATIN_FOLD)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return {t for t in s.split() if t and t not in STOPWORDS}


def first_page(value) -> str:
    """'183--219' / '183-219' / '106875' -> leading page or article number."""
    if value is None:
        return ""
    s = str(value).replace("\u2013", "-").replace("--", "-")
    return re.sub(r"[^0-9]", "", s.split("-")[0])


def title_similarity(a: str, b: str) -> tuple[float, float]:
    """(containment, jaccard) over normalized token sets."""
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0, 0.0
    inter = len(ta & tb)
    return inter / min(len(ta), len(tb)), inter / len(ta | tb)


# ── network ─────────────────────────────────────────────────────────────────

class Net:
    def __init__(self, delay: float, timeout: float, use_cache: bool):
        self.delay = delay
        self.timeout = timeout
        self.use_cache = use_cache
        self.hits = 0
        self.cache = {}
        if use_cache and CACHE_PATH.exists():
            try:
                self.cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self.cache = {}

    def get_json(self, url: str) -> tuple[str, object]:
        """-> (status, payload). status in {ok, notfound, error}."""
        if self.use_cache and url in self.cache:
            self.hits += 1
            cached = self.cache[url]
            return cached["status"], cached.get("payload")
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                payload = json.loads(r.read().decode("utf-8", "replace"))
            status = "ok"
        except urllib.error.HTTPError as e:
            payload = None
            status = "notfound" if e.code in (404, 400) else "error"
            if status == "error":
                payload = f"HTTP {e.code}"
        except Exception as e:  # noqa: BLE001 — URLError, timeout, DNS, JSON
            status, payload = "error", f"{type(e).__name__}: {e}"
        self.cache[url] = {"status": status, "payload": payload}
        time.sleep(self.delay)
        return status, payload

    def get_text(self, url: str) -> tuple[str, object]:
        if self.use_cache and url in self.cache:
            self.hits += 1
            cached = self.cache[url]
            return cached["status"], cached.get("payload")
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                payload = r.read().decode("utf-8", "replace")
            status = "ok"
        except urllib.error.HTTPError as e:
            status, payload = ("notfound" if e.code == 404 else "error"), f"HTTP {e.code}"
        except Exception as e:  # noqa: BLE001
            status, payload = "error", f"{type(e).__name__}: {e}"
        self.cache[url] = {"status": status, "payload": payload}
        time.sleep(self.delay)
        return status, payload

    def flush(self):
        try:
            CACHE_PATH.write_text(json.dumps(self.cache), encoding="utf-8")
        except OSError:
            pass


# ── source lookups ──────────────────────────────────────────────────────────

def crossref_by_doi(net: Net, doi: str) -> dict | None:
    status, msg = net.get_json(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}")
    if status == "ok" and isinstance(msg, dict):
        return crossref_message(msg)
    return None


def crossref_message(msg: dict) -> dict:
    m = msg.get("message", msg)
    issued = m.get("issued", {}).get("date-parts", [[None]])[0]
    authors = m.get("author") or []
    return {
        "source": "crossref",
        "title": (m.get("title") or [""])[0],
        "container": (m.get("container-title") or [""])[0],
        "year": issued[0] if issued else None,
        "volume": m.get("volume"),
        "issue": m.get("issue"),
        "page": m.get("page"),
        "articleno": m.get("article-number"),
        "type": m.get("type"),
        "first_author": (authors[0].get("family") if authors else "") or "",
        "doi": m.get("DOI"),
    }


def crossref_search_title(net: Net, title: str) -> list[dict]:
    q = urllib.parse.urlencode({
        "query.bibliographic": strip_latex(title)[:300],
        "rows": 3,
    })
    status, msg = net.get_json(f"https://api.crossref.org/works?{q}")
    if status != "ok" or not isinstance(msg, dict):
        return []
    return [crossref_message({"message": it}) for it in msg.get("message", {}).get("items", [])]


def doi_handle_registered(net: Net, doi: str) -> bool:
    """Last-resort existence probe: DOI handle exists but Crossref/OpenAlex do
    not index it (small journals, society proceedings)."""
    url = f"https://doi.org/api/handles/{urllib.parse.quote(doi)}"
    status, msg = net.get_json(url)
    return status == "ok" and isinstance(msg, dict) and int(msg.get("responseCode", 200)) == 1


def openalex_by_doi(net: Net, doi: str) -> dict | None:
    url = f"https://api.openalex.org/works/https://doi.org/{urllib.parse.quote(doi)}"
    status, msg = net.get_json(url)
    if status != "ok" or not isinstance(msg, dict):
        return None
    biblio = msg.get("biblio") or {}
    loc = msg.get("primary_location") or {}
    src = loc.get("source") or {}
    authors = msg.get("authorships") or []
    first = ""
    if authors:
        first = (authors[0].get("author") or {}).get("display_name", "") or ""
    return {
        "source": "openalex",
        "title": msg.get("title") or msg.get("display_name") or "",
        "container": src.get("display_name") or "",
        "year": msg.get("publication_year"),
        "volume": biblio.get("volume"),
        "issue": biblio.get("issue"),
        "page": biblio.get("first_page"),
        "articleno": None,
        "type": msg.get("type"),
        "first_author": first.split()[-1] if first else "",
        "doi": (msg.get("doi") or "").replace("https://doi.org/", ""),
    }


def arxiv_by_id(net: Net, arxiv_id: str) -> dict | None:
    url = f"http://export.arxiv.org/api/query?id_list={urllib.parse.quote(arxiv_id)}"
    status, text = net.get_text(url)
    if status != "ok" or not isinstance(text, str):
        return None
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return None
    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    entry = root.find("a:entry", ns)
    if entry is None:
        return None
    title_el = entry.find("a:title", ns)
    title = (title_el.text or "").strip() if title_el is not None else ""
    if not title or title.lower().startswith("error"):
        return None
    pub_el = entry.find("a:published", ns)
    year = int((pub_el.text or "")[:4]) if pub_el is not None and pub_el.text else None
    jref_el = entry.find("arxiv:journal_ref", ns)
    return {
        "source": "arxiv",
        "title": title,
        "container": (jref_el.text or "").strip() if jref_el is not None else "",
        "year": year,
        "volume": None, "issue": None, "page": None, "articleno": None,
        "type": "preprint",
        "first_author": "",
        "doi": None,
    }


# ── comparison ──────────────────────────────────────────────────────────────

def _digits(s) -> str:
    return re.sub(r"[^0-9]", "", str(s or ""))


def compare(entry: dict, found: dict) -> list[str]:
    """Human-readable metadata divergences (warnings only)."""
    f = entry["fields"]
    warns = []

    sim_c, sim_j = title_similarity(f.get("title", ""), found.get("title", ""))
    if sim_c < TITLE_WARN_MIN:
        warns.append(
            f"title differs (containment {sim_c:.2f}, jaccard {sim_j:.2f}): "
            f"bib={strip_latex(f.get('title',''))[:90]!r} vs "
            f"source={strip_latex(found.get('title',''))[:90]!r}"
        )

    by, sy = f.get("year"), found.get("year")
    if by and sy and _digits(by) != _digits(sy):
        warns.append(f"year bib={by} vs source={sy}")

    bj = f.get("journal") or f.get("booktitle") or ""
    sj = found.get("container") or ""
    if bj and sj:
        jc, _ = title_similarity(bj, sj)
        if jc < 0.5:
            warns.append(f"venue bib={strip_latex(bj)!r} vs source={strip_latex(sj)!r}")

    for field, label in (("volume", "volume"), ("issue", "issue")):
        bv, sv = f.get(field), found.get(field)
        if bv and sv and _digits(bv) != _digits(sv):
            warns.append(f"{label} bib={bv} vs source={sv}")

    bp = f.get("pages") or f.get("articleno")
    sp = found.get("page") or found.get("articleno")
    b_first, s_first = first_page(bp), first_page(sp)
    if b_first and s_first and b_first != s_first:
        warns.append(f"first page/article-no bib={bp} vs source={sp}")

    ba, sa = f.get("author", ""), found.get("first_author", "")
    if ba and sa:
        bt = tokens(ba.split(" and ")[0])
        st = tokens(sa)
        if bt and st and not (bt & st):
            warns.append(f"first author bib={strip_latex(ba.split(' and ')[0])!r} vs source={sa!r}")

    return warns


# ── main check ──────────────────────────────────────────────────────────────

def check_entry(net: Net, entry: dict, allowlist: dict) -> dict:
    f = entry["fields"]
    key = entry["key"]
    rec = {"key": key, "type": entry["type"], "status": "missing",
           "found_via": None, "source": None, "warnings": [], "note": ""}

    if key in allowlist:
        rec.update(status="allowlisted", note=allowlist[key])
        return rec

    doi = normalize_doi(f.get("doi", ""))
    arxiv_id = normalize_arxiv(f.get("eprint", "")) or (
        normalize_arxiv(f["doi"]) if "arxiv" in f.get("doi", "").lower() else ""
    )

    if doi:
        found = crossref_by_doi(net, doi)
        via = "crossref:doi"
        if found is None:
            found = openalex_by_doi(net, doi)
            via = "openalex:doi"
        if found:
            rec.update(status="found", found_via=via, source=found["source"])
            rec["warnings"] = compare(entry, found)
            return rec
        if doi_handle_registered(net, doi):
            rec.update(status="found", found_via="doi.org:handle", source="doi.org")
            rec["warnings"] = ["DOI handle resolves but Crossref/OpenAlex do not index "
                              "this work — metadata NOT verified against a source of record"]
            return rec
        rec["note"] = (f"DOI {doi} not registered (doi.org handle 404) and absent from "
                       f"Crossref/OpenAlex")

    if arxiv_id:
        found = arxiv_by_id(net, arxiv_id)
        if found:
            rec.update(status="found", found_via="arxiv:id", source="arxiv")
            rec["warnings"] = compare(entry, found)
            return rec
        rec["note"] = (rec["note"] + "; " if rec["note"] else "") + f"arXiv {arxiv_id} unresolvable"

    # no usable identifier (books, unregistered preprints) -> title search
    title = strip_latex(f.get("title", ""))
    if title:
        best, best_c, best_j = None, 0.0, 0.0
        seen_ids = set()
        for cand in crossref_search_title(net, title):
            tid = (cand.get("doi") or cand.get("title") or "").lower()
            if tid in seen_ids:
                continue
            seen_ids.add(tid)
            sim_c, sim_j = title_similarity(title, cand.get("title", ""))
            if sim_c > best_c:
                best, best_c, best_j = cand, sim_c, sim_j
        # contain-only matches are unsafe: a short title is "contained" in any
        # longer one. Require token overlap in both directions.
        if best is not None and best_c >= TITLE_MATCH_MIN and best_j >= TITLE_JACCARD_MIN:
            rec.update(status="found",
                       found_via=f"crossref:title(c={best_c:.2f},j={best_j:.2f})",
                       source="crossref")
            rec["warnings"] = compare(entry, best)
            return rec
        if best is not None:
            rec["note"] = (rec["note"] + "; " if rec["note"] else "") + (
                f"best title hit only c={best_c:.2f}/j={best_j:.2f} "
                f"({strip_latex(best.get('title',''))[:70]!r})"
            )
    else:
        rec["note"] = (rec["note"] + "; " if rec["note"] else "") + "no title field"

    return rec


def find_bibs(explicit: list[str] | None) -> list[Path]:
    if explicit:
        # resolve() so an explicitly-passed relative path still satisfies the
        # bib.relative_to(REPO) call in check_bib — Path(p) alone leaves it
        # relative and raises ValueError there.
        return [Path(p).resolve() for p in explicit]
    return sorted(p for p in (REPO / "papers").glob("*/*.bib"))


def load_allowlist(bib: Path) -> dict:
    p = bib.parent / "citation-allowlist.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"  ! {p} is not valid JSON — ignored", file=sys.stderr)
    return {}


def check_bib(net: Net, bib: Path, only: set[str] | None, verbose: bool) -> dict:
    entries = parse_bib(bib.read_text(encoding="utf-8"))
    if only:
        entries = [e for e in entries if e["key"] in only]
    allowlist = load_allowlist(bib)

    print(f"\n=== {bib.relative_to(REPO)} — {len(entries)} entries ===")
    print(f"{'key':<26} {'status':<10} {'via':<22} warnings")
    print("-" * 96)

    records = []
    for e in entries:
        rec = check_entry(net, e, allowlist)
        records.append(rec)
        mark = {"found": "ok", "missing": "MISSING",
                "allowlisted": "allow", "error": "ERROR"}[rec["status"]]
        w = len(rec["warnings"])
        tail = (f"{w} warn" if w else "") + (f"  {rec['note']}" if rec["note"] and verbose else "")
        print(f"{rec['key']:<26} {mark:<10} {(rec['found_via'] or '-'):<22} {tail}")
        for warn in rec["warnings"]:
            print(f"{'':<26} {'':<10} {'':<22}   - {warn}")

    missing = [r["key"] for r in records if r["status"] == "missing"]
    warned = [r["key"] for r in records if r["warnings"]]
    errors = [r["key"] for r in records if r["status"] == "error"]
    allow = [r["key"] for r in records if r["status"] == "allowlisted"]

    print("-" * 96)
    print(f"found={sum(1 for r in records if r['status']=='found')} "
          f"missing={len(missing)} warnings={len(warned)} "
          f"allowlisted={len(allow)} errors={len(errors)}")
    if missing:
        print(f"MISSING: {', '.join(missing)}")

    # header-comment staleness (RDR-065 B6: bib claimed "25 cited entries")
    m = re.search(r"%\s*(\d+)\s+cited entries", bib.read_text(encoding="utf-8"))
    if m and int(m.group(1)) != len(entries):
        print(f"NOTE: header says '{m.group(1)} cited entries', file has {len(entries)} "
              f"— update the comment")

    return {
        "bib": str(bib.relative_to(REPO)),
        "entries_total": len(entries),
        "missing": missing, "warned": warned, "errors": errors, "allowlisted": allow,
        "records": records,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bib", action="append", help="bib file(s); default: papers/*/*.bib")
    ap.add_argument("--only", nargs="+", help="restrict to these citation keys")
    ap.add_argument("--report", help="JSON report path (default papers/<theme>/review/citation-report.json)")
    ap.add_argument("--allowlist", help="override allowlist JSON path")
    ap.add_argument("--delay", type=float, default=0.4, help="seconds between HTTP calls")
    ap.add_argument("--timeout", type=float, default=25.0)
    ap.add_argument("--recheck", action="store_true", help="bypass the response cache")
    ap.add_argument("-v", "--verbose", action="store_true", help="print failure notes inline")
    args = ap.parse_args()

    bibs = find_bibs(args.bib)
    if not bibs:
        print("no .bib files found", file=sys.stderr)
        return 2

    net = Net(delay=args.delay, timeout=args.timeout, use_cache=not args.recheck)
    only = set(args.only) if args.only else None

    results = [check_bib(net, b, only, args.verbose) for b in bibs]
    net.flush()

    report = {
        "tool": "check_citation_exists.py",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": {"existence": "hard fail", "metadata": "warn only"},
        "cache": {"path": str(CACHE_PATH), "hits": net.hits},
        "bibfiles": results,
        "summary": {
            "missing": sum(len(r["missing"]) for r in results),
            "warnings": sum(len(r["warned"]) for r in results),
            "errors": sum(len(r["errors"]) for r in results),
        },
    }

    targets = [Path(p) for p in args.bib] if args.bib else bibs
    report_path = Path(args.report) if args.report else (targets[0].parent / "review" / "citation-report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nreport -> {report_path}")

    s = report["summary"]
    if s["missing"]:
        print("EXIT 1 — existence failures present")
        return 1
    if s["errors"]:
        print("EXIT 2 — lookups errored (network/quota); rerun without --recheck or later")
        return 2
    print("EXIT 0 — all entries exist")
    return 0


if __name__ == "__main__":
    sys.exit(main())
