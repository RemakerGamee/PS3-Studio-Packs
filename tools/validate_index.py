# RetroRemakes PS3 Studio - community patch pack list check
# Copyright (c) 2026 RetroRemakes. All rights reserved.
"""Check index.json: entry fields, unique ids, and (with --download) each pack ZIP.

    python tools/validate_index.py [--download]
"""
import hashlib
import io
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import PurePosixPath

ID = re.compile(r"[a-z0-9][a-z0-9-]{1,63}\Z")
TITLE = re.compile(r"[A-Z]{4}\d{5}\Z")
BLOCKED = (".elf", ".self", ".sprx", ".prx", ".pup", ".pkg", ".rap", ".edat", ".sdat", ".iso", ".bin")
MAX_PACK = 256 * 1024 * 1024


def check(download):
    data = json.load(open("index.json", encoding="utf-8"))
    problems, seen = [], set()
    if data.get("schema") != 1 or not isinstance(data.get("packs"), list):
        return ["index.json must be {\"schema\": 1, \"packs\": [...]}"]
    for n, e in enumerate(data["packs"], 1):
        where = f"entry {n} ({e.get('id', '?')})"
        for key in ("id", "name", "version", "author", "license", "url", "sha256"):
            if not str(e.get(key, "")).strip():
                problems.append(f"{where}: missing {key}")
        if not ID.match(str(e.get("id", ""))):
            problems.append(f"{where}: id must be lowercase letters, digits and '-'")
        if e.get("id") in seen:
            problems.append(f"{where}: duplicate id")
        seen.add(e.get("id"))
        if not str(e.get("url", "")).startswith("https://"):
            problems.append(f"{where}: url must be https://")
        if not re.fullmatch(r"[0-9a-fA-F]{64}", str(e.get("sha256", ""))):
            problems.append(f"{where}: sha256 must be 64 hex characters")
        titles = e.get("title_ids", [])
        if not titles or any(not TITLE.match(str(t)) for t in titles):
            problems.append(f"{where}: title_ids must list PS3 title IDs like BCUS98234")
        if download and not any(p.startswith(where) for p in problems):
            problems += check_zip(e, where)
    return problems


def check_zip(e, where):
    try:
        req = urllib.request.Request(e["url"], headers={"User-Agent": "PS3-Studio-Packs-check"})
        blob = urllib.request.urlopen(req, timeout=120).read(MAX_PACK + 1)
    except Exception as error:
        return [f"{where}: download failed: {error}"]
    if len(blob) > MAX_PACK:
        return [f"{where}: ZIP larger than 256 MB"]
    if hashlib.sha256(blob).hexdigest().lower() != e["sha256"].lower():
        return [f"{where}: sha256 does not match the file at url"]
    problems = []
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names = z.namelist()
        packs = [n for n in names if PurePosixPath(n).name == "pack.json"]
        for n in names:
            parts = PurePosixPath(n).parts
            if n.startswith("/") or ".." in parts or "\\" in n:
                problems.append(f"{where}: unsafe path in ZIP: {n}")
            if n.lower().endswith(BLOCKED):
                problems.append(f"{where}: game/system file type not allowed: {n}")
        if not packs:
            return problems + [f"{where}: no pack.json in ZIP"]
        pack = json.loads(z.read(min(packs, key=len)))
        if pack.get("id") != e["id"]:
            problems.append(f"{where}: pack.json id is {pack.get('id')!r}, list says {e['id']!r}")
        if str(pack.get("version")) != str(e["version"]):
            problems.append(f"{where}: pack.json version is {pack.get('version')!r}, list says {e['version']!r}")
    return problems


if __name__ == "__main__":
    found = check("--download" in sys.argv)
    for p in found:
        print("PROBLEM:", p)
    print("index.json OK" if not found else f"{len(found)} problem(s)")
    sys.exit(1 if found else 0)
