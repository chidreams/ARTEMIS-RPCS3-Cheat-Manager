#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2026 ChiDreams. All rights reserved.
"""
ARTEMIS - RPCS3 Cheat Manager
=============================
A zero-dependency (pure Tkinter + stdlib) PS3/XMB-themed GUI for managing an
RPCS3 patch.yml (import_patch.yml) file.

Features
--------
* Left panel groups cheats by GAME, showing  Game  [SERIAL]  vVERSION  pulled
  straight from each patch's Games: block, with the cheats listed underneath.
* Add new cheats with LIVE validation (invalid patch lines turn RED).
* New cheats are written in exact RPCS3 v1.2 format and APPENDED without
  disturbing existing formatting.
* "Patch Library" tab downloads the latest patches from your GitHub repo
  (Artemis-Patch-Collection-RPCS3) and lets you open or merge any of them.
* "About" tab with all your socials (YouTube, Discord, X, Reddit, GBAtemp,
  GitHub).
* Hidden easter egg: type the secret word anywhere...

Run the GUI:      python cheat_manager.py
Run self-tests:   python cheat_manager.py --selftest
"""

import os
import re
import io
import sys
import json
import math
import shutil
import zipfile
import datetime
import threading
import webbrowser
import urllib.request

# ----------------------------------------------------------------------------
# >>> EDIT THESE <<<  put your real links here
# ----------------------------------------------------------------------------
SOCIALS = [
    # (label,        url,                                              dot color)
    ("YouTube",  "https://www.youtube.com/@ChidreamsEmulationGamePlay","#ff0000"),
    ("Discord",  "https://discord.gg/CUUva5FPzu",                      "#5865f2"),
    ("X.com",    "https://x.com/ChidreamsG",                           "#1d9bf0"),
    ("Reddit",   "https://www.reddit.com/r/darkchidreams/",             "#ff4500"),
    ("GBAtemp",  "https://gbatemp.net/forums/retro-video-games-and-emulation-talk.499/","#3aa76d"),
    ("GitHub",   "https://github.com/chidreams/Artemis-Patch-Collection-RPCS3", "#e6eefc"),
]
YOUTUBE_URL = SOCIALS[0][1]          # used by the easter egg banner
SECRET_WORD = "dron3"                # type this anywhere to trigger the egg

GITHUB_OWNER = "chidreams"
GITHUB_REPO = "Artemis-Patch-Collection-RPCS3"
GITHUB_BRANCH = "main"
ZIP_URL = ("https://codeload.github.com/%s/%s/zip/refs/heads/%s"
           % (GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH))
# ----------------------------------------------------------------------------

DEFAULT_FILE = "import_patch.yml"
LIBRARY_DIRNAME = "Artemis-Patches"
INDENT = "  "  # RPCS3 uses 2-space indentation
VERSION = "v1.0.1"
# ----------------------------------------------------------------------------
#  PS3 / XMB  MONTH COLORS   >>> EDIT THESE to taste <<<
# ----------------------------------------------------------------------------
# Like the real PS3 "Original" waves theme, the whole UI recolors by month.
# Sony's exact values live inside DDS textures (lines.qrc) and were never
# published as hex, so these are a faithful match to the seasonal progression
# the XMB used: icy winter blues -> spring pink/green -> summer gold ->
# autumn red/brown. Tweak any month's signature color and the wave, gradient,
# panels and accents all derive from it automatically.
MONTH_BASE = {
    1:  "#3a7bd5",   # January   - icy blue
    2:  "#7a5fc4",   # February  - violet
    3:  "#c95f9e",   # March     - rose / pink
    4:  "#4fae6a",   # April     - spring green
    5:  "#6fbf3a",   # May       - lime green
    6:  "#2f8fd0",   # June      - blue
    7:  "#26b0ad",   # July      - aqua / teal
    8:  "#e0a02a",   # August    - gold
    9:  "#e07a2a",   # September - amber / orange
    10: "#d0432f",   # October   - autumn red
    11: "#9a5a3a",   # November  - bronze / brown
    12: "#5a8fd0",   # December  - winter blue
}
# Set to a month number (1-12) to lock the theme; None = follow the real month.
FORCE_MONTH = None

# These stay constant (semantic / readability), regardless of month.
FG = "#e6eefc"        # near-white text
MUTED = "#8aa0c8"     # subtle text
GOOD = "#36d399"      # valid / success
BAD = "#ff5c6c"       # invalid / error

# Month-derived colors (filled in by apply_month(); June defaults below).
BG = "#0a0f1e"
BG2 = "#111a30"
BG3 = "#0d1424"
ACCENT = "#36a3ff"
ACCENT2 = "#8ad0ff"
SEL = "#1c3a66"
BORDER = "#1d2a45"
WAVE1 = "#13314f"
WAVE2 = "#1e5e9e"
WAVE3 = "#36a3ff"
GRAD1 = "#0a0f1e"
GRAD2 = "#14284e"


def _rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _hx(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def _mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def resolve_month():
    if FORCE_MONTH in MONTH_BASE:
        return FORCE_MONTH
    return datetime.datetime.now().month


def apply_month(month):
    """Derive the full palette from the month's signature color."""
    global BG, BG2, BG3, ACCENT, ACCENT2, SEL, BORDER
    global WAVE1, WAVE2, WAVE3, GRAD1, GRAD2
    base = MONTH_BASE.get(month, MONTH_BASE[6])
    b = _rgb(base)
    blk, wht = (0, 0, 0), (255, 255, 255)
    ACCENT = base
    ACCENT2 = _hx(_mix(b, wht, 0.45))
    BG = _hx(_mix(b, blk, 0.93))
    BG2 = _hx(_mix(b, blk, 0.86))
    BG3 = _hx(_mix(b, blk, 0.90))
    SEL = _hx(_mix(b, blk, 0.62))
    BORDER = _hx(_mix(b, blk, 0.78))
    WAVE1 = _hx(_mix(b, blk, 0.58))
    WAVE2 = _hx(_mix(b, blk, 0.32))
    WAVE3 = base
    GRAD1 = _hx(_mix(b, blk, 0.92))
    GRAD2 = _hx(_mix(b, blk, 0.66))


def app_dir():
    """Folder the app lives in (next to the .exe when frozen by PyInstaller)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def config_dir():
    """Per-user writable folder for settings (used if app_dir isn't writable)."""
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, "Artemis")


def _is_writable(d):
    try:
        os.makedirs(d, exist_ok=True)
        test = os.path.join(d, ".artemis_write_test")
        with open(test, "w") as f:
            f.write("ok")
        os.remove(test)
        return True
    except Exception:
        return False


def data_dir():
    """Where settings + the downloaded library live. Prefer the app folder
    (portable), fall back to a per-user folder if that's read-only."""
    a = app_dir()
    return a if _is_writable(a) else config_dir()


# ============================================================================
#  VALIDATION  (pure logic, unit-testable)
# ============================================================================
INT_TYPES = {
    "byte": 1,
    "le16": 2, "be16": 2,
    "le32": 4, "be32": 4, "bd32": 4,
    "le64": 8, "be64": 8, "bd64": 8,
    "jump": 8, "jump_link": 8, "alloc": 8, "code_alloc": 8,
}
FLOAT_TYPES = {"bef32", "lef32", "bef64", "lef64"}
STRING_TYPES = {"utf8", "cutf8", "c_utf8"}
SPECIAL_TYPES = {"load"}
FILE_TYPES = {"move_file", "hide_file"}
MISC_TYPES = {"bpex"}
ALL_TYPES = (set(INT_TYPES) | FLOAT_TYPES | STRING_TYPES
             | SPECIAL_TYPES | FILE_TYPES | MISC_TYPES)


def _split_top_level(s):
    out, buf, quote = [], [], None
    for ch in s:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch == ",":
            out.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    out.append("".join(buf).strip())
    return out


def _parse_int(tok):
    tok = tok.strip()
    neg = tok.startswith("-")
    if neg:
        tok = tok[1:].strip()
    val = int(tok, 0)
    return -val if neg else val


def _is_quoted(tok):
    tok = tok.strip()
    return len(tok) >= 2 and tok[0] in "\"'" and tok[-1] == tok[0]


def normalize_patch_line(raw):
    line = raw.strip()
    if line.startswith("- "):
        line = line[2:].strip()
    elif line == "-":
        line = ""
    if line.startswith("[") and line.endswith("]"):
        line = line[1:-1].strip()
    return line


def validate_patch_line(raw):
    stripped = raw.strip()
    if stripped == "" or stripped.startswith("#"):
        return True, ""
        
    # FIX: Handle comments at the end of lines cleanly BEFORE stripping brackets
    if "#" in stripped:
        # Only split if the # isn't trapped inside a quoted string
        before = stripped.split("#", 1)[0]
        if before.count('"') % 2 == 0 and before.count("'") % 2 == 0:
            stripped = before.strip()

    inner = normalize_patch_line(stripped)
    if not inner:
        return False, "empty instruction"
        
    toks = _split_top_level(inner)
    if len(toks) < 2:
        return False, "expected at least [ type, value ]"
    ptype = toks[0].strip()
    if ptype not in ALL_TYPES:
        return False, "unknown type '%s'" % ptype
    if ptype in SPECIAL_TYPES:
        if not toks[1].lstrip().startswith("*"):
            return False, "load needs an anchor reference (*name)"
        return True, ""
    if ptype in FILE_TYPES:
        if len(toks) < 2:
            return False, "%s needs a path" % ptype
        return True, ""
    if len(toks) < 3:
        return False, "expected [ %s, offset, value ]" % ptype
    offset, value = toks[1].strip(), toks[2].strip()
    try:
        off = _parse_int(offset)
    except (ValueError, TypeError):
        return False, "offset '%s' is not a valid hex/int (use 0x...)" % offset
    if off < 0:
        return False, "offset must be >= 0"
    if ptype in INT_TYPES:
        try:
            v = _parse_int(value)
        except (ValueError, TypeError):
            return False, "value '%s' is not a valid hex/int (use 0x...)" % value
        width = INT_TYPES[ptype]
        bits = width * 8
        umax = (1 << bits) - 1
        smin = -(1 << (bits - 1))
        if not (smin <= v <= umax):
            return False, "value out of range for %s (%d-byte)" % (ptype, width)
        return True, ""
    if ptype in FLOAT_TYPES:
        if _is_quoted(value):
            return True, ""
        try:
            float(value)
        except ValueError:
            return False, "value '%s' is not a valid float" % value
        return True, ""
    if ptype in STRING_TYPES:
        if not _is_quoted(value):
            return False, "%s value must be a quoted string" % ptype
        return True, ""
    if ptype in MISC_TYPES:
        return True, ""
    return False, "unhandled type '%s'" % ptype


# ============================================================================
#  PATCH FILE MODEL  (format-preserving, line-aware)
# ============================================================================
GROUP_HEADER_RE = re.compile(r"^(?P<key>\S[^:#]*?):\s*(#.*)?$")
SERIAL_RE = re.compile(r"^([A-Za-z0-9_]+)\s*:\s*\[(.*)\]\s*$")


def _is_hash_key(key):
    key = key.strip().strip('"').strip("'")
    if key.startswith("PPU-") or key.startswith("SPU-"):
        return True
    return bool(re.fullmatch(r"[0-9a-fA-F]{32,}", key))


class Cheat:
    __slots__ = ("name", "start", "end", "raw", "patch_lines",
                 "game", "serials", "version_tag", "author", "notes")

    def __init__(self, name, start, end, raw):
        self.name = name
        self.start = start
        self.end = end
        self.raw = raw
        self.patch_lines = []
        self.game = ""
        self.serials = []
        self.version_tag = ""
        self.author = ""
        self.notes = ""


class Group:
    __slots__ = ("header", "hash", "start", "end", "cheats")

    def __init__(self, header, hsh, start):
        self.header = header
        self.hash = hsh
        self.start = start
        self.end = start
        self.cheats = []


class PatchFile:
    def __init__(self, text=""):
        self.text = text
        self.lines = text.split("\n") if text else []
        self.groups = []
        self.parse()

    @classmethod
    def load(cls, path):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return cls(f.read())

    def clean_empty_groups(self):
        """Scans the file and removes any PPU/SPU headers that have no cheats beneath them."""
        cleaned = []
        i, n = 0, len(self.lines)
        
        while i < n:
            line = self.lines[i]
            m = GROUP_HEADER_RE.match(line)
            
            # Check if this line is a PPU/SPU hash header
            if m and _is_hash_key(m.group("key")):
                has_data = False
                j = i + 1
                
                # Look ahead to see if it actually contains indented cheat data
                while j < n:
                    check_line = self.lines[j].strip()
                    
                    # Ignore blank lines and comments while looking ahead
                    if not check_line or check_line.startswith("#"):
                        j += 1
                        continue
                    
                    # If we hit ANOTHER header, the first one is empty
                    next_m = GROUP_HEADER_RE.match(self.lines[j])
                    if next_m and _is_hash_key(next_m.group("key")):
                        break
                    
                    # If we found normal text, the header is valid
                    has_data = True
                    break
                    
                if not has_data:
                    # It's an orphaned header! Skip it so it gets deleted.
                    i += 1
                    continue
                    
            cleaned.append(line)
            i += 1
            
        # Rebuild the file and re-parse
        self.text = "\n".join(cleaned).rstrip("\n") + "\n"
        self.lines = self.text.split("\n")
        self.parse()
    
    def save(self, path, make_backup=True):
        # Auto-validate and sanitize the YAML format to prevent RPCS3 crashes
        self.clean_empty_groups()
        
        if make_backup and os.path.exists(path):
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                shutil.copy2(path, "%s.%s.bak" % (path, stamp))
            except OSError:
                pass
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(self.text)

    def parse(self):
        self.groups = []
        lines = self.lines
        i, n = 0, len(lines)
        current = None
        while i < n:
            line = lines[i]
            if line and not line[0].isspace():
                m = GROUP_HEADER_RE.match(line)
                if m and _is_hash_key(m.group("key")):
                    if current is not None:
                        current.end = i
                    current = Group(line, m.group("key").strip(), i)
                    self.groups.append(current)
                else:
                    if current is not None:
                        current.end = i
                    current = None
            i += 1
        if current is not None:
            current.end = n
        for g in self.groups:
            self._parse_group_cheats(g)

    def _parse_group_cheats(self, g):
        body = self.lines[g.start + 1:g.end]
        base = g.start + 1
        child_indent = None
        for ln in body:
            if ln.strip() == "" or ln.lstrip().startswith("#"):
                continue
            child_indent = len(ln) - len(ln.lstrip())
            break
        if not child_indent:
            return
        cheat_starts = []
        for idx, ln in enumerate(body):
            if ln.strip() == "" or ln.lstrip().startswith("#"):
                continue
            ind = len(ln) - len(ln.lstrip())
            if ind == child_indent and ln.rstrip().endswith(":"):
                name = ln.strip()[:-1].strip().strip('"').strip("'")
                cheat_starts.append((idx, name))
        for k, (idx, name) in enumerate(cheat_starts):
            nxt = cheat_starts[k + 1][0] if k + 1 < len(cheat_starts) else len(body)
            raw = "\n".join(body[idx:nxt]).rstrip("\n")
            c = Cheat(name, base + idx, base + nxt, raw)
            self._parse_cheat_fields(c, body[idx:nxt])
            g.cheats.append(c)

    @staticmethod
    def _parse_cheat_fields(c, block):
        in_patch = False
        in_games = False
        for ln in block:
            s = ln.strip()
            low = s.lower()
            if low.startswith("games:"):
                in_games = True
                continue
            if low.startswith("author:"):
                c.author = s.split(":", 1)[1].strip().strip('"').strip("'")
                in_games = False
            elif low.startswith("notes:"):
                c.notes = s.split(":", 1)[1].strip().strip('"').strip("'")
                in_games = False
            elif low.startswith("patch version"):
                in_games = False
            elif low.startswith("patch:"):
                in_patch = True
                in_games = False
                continue
            elif in_games and s:
                if (s.startswith('"') or s.startswith("'")) and s.endswith(":"):
                    c.game = s[:-1].strip().strip('"').strip("'")
                else:
                    m = SERIAL_RE.match(s)
                    if m:
                        c.serials.append(m.group(1).strip())
                        if not c.version_tag:
                            c.version_tag = m.group(2).strip()
            if in_patch:
                if s.startswith("- ") or s.startswith("-["):
                    ok, msg = validate_patch_line(s)
                    c.patch_lines.append((ln, ok, msg))
                elif s == "" or s.startswith("#"):
                    continue
                else:
                    in_patch = False
        return c

    def all_cheats(self):
        return [(g, c) for g in self.groups for c in g.cheats]

    def hashes(self):
        seen, out = set(), []
        for g in self.groups:
            if g.hash not in seen:
                seen.add(g.hash)
                out.append(g.hash)
        return out

    def build_cheat_block(self, name, game, serial, version_tag,
                          author, notes, patch_lines, patch_version="1.0"):
        i1, i2, i3, i4 = INDENT, INDENT * 2, INDENT * 3, INDENT * 4
        out = ['%s"%s":' % (i1, name), '%sGames:' % i2, '%s"%s":' % (i3, game)]
        serials = [s.strip() for s in re.split(r"[,\s]+", serial) if s.strip()]
        tag = version_tag.strip() or "All"
        for sr in serials or [""]:
            out.append('%s%s: [ %s ]' % (i4, sr, tag))
        out.append('%sAuthor: "%s"' % (i2, author))
        out.append('%sNotes: "%s"' % (i2, notes))
        out.append('%sPatch Version: %s' % (i2, patch_version))
        out.append('%sPatch:' % i2)
        for pl in patch_lines:
            inner = normalize_patch_line(pl)
            if inner == "" or pl.strip().startswith("#"):
                if pl.strip():
                    out.append('%s%s' % (i3, pl.strip()))
                continue
            out.append('%s- [ %s ]' % (i3, inner))
        return "\n".join(out)

    def add_cheat(self, ppu_hash, block_text):
        ppu_hash = ppu_hash.strip()
        text = self.text.rstrip("\n")
        lines = text.split("\n") if text else []
        if not any(l.strip().lower().startswith("version:") for l in lines[:5]):
            lines = ["Version: 1.2", ""] + lines
        target = None
        for g in PatchFile("\n".join(lines)).groups:
            if g.hash == ppu_hash:
                target = g
                break
        if target is not None:
            insert_at = target.end
            while 0 <= insert_at - 1 < len(lines) and lines[insert_at - 1].strip() == "":
                insert_at -= 1
            new_lines = (lines[:insert_at] + [""] + block_text.split("\n")
                         + lines[insert_at:])
        else:
            header = ppu_hash if ppu_hash.endswith(":") else ppu_hash + ":"
            new_lines = lines + ["", header] + block_text.split("\n")
        self.text = "\n".join(new_lines).rstrip("\n") + "\n"
        self.lines = self.text.split("\n")
        self.parse()

    def merge_text(self, other_text, comment=""):
        body = other_text.split("\n")
        while body and (body[0].strip() == ""
                        or body[0].strip().lower().startswith("version:")):
            body.pop(0)
        base = self.text.rstrip("\n")
        chunk = (("\n# %s\n" % comment) if comment else "\n") + "\n".join(body)
        self.text = (base + "\n" + chunk).rstrip("\n") + "\n"
        self.lines = self.text.split("\n")
        self.parse()

    def delete_cheat(self, cheat):
        lines = self.lines[:]
        del lines[cheat.start:cheat.end]
        self.text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).rstrip("\n") + "\n"
        self.lines = self.text.split("\n")
        self.parse()
    
    def update_cheat(self, cheat, new_text):
        """Replaces an existing cheat's block with edited text."""
        lines = self.lines[:]
        # Split the new text into lines, stripping trailing newlines
        new_lines = new_text.rstrip("\n").split("\n")
        
        # Swap the old lines for the new lines
        lines[cheat.start:cheat.end] = new_lines
        
        # Rebuild the file text and re-parse the model
        self.text = "\n".join(lines).rstrip("\n") + "\n"
        self.lines = self.text.split("\n")
        self.parse()

# ============================================================================
#  GITHUB DOWNLOADER  (stdlib only)
# ============================================================================
def download_collection(dest_dir, progress_cb=None):
    """Download the repo zip and extract patch files into dest_dir.
    Returns number of files written. progress_cb(read, total) is optional."""
    req = urllib.request.Request(
        ZIP_URL, headers={"User-Agent": "ArtemisCheatManager/1.0"})
    buf = io.BytesIO()
    with urllib.request.urlopen(req, timeout=60) as resp:
        total = int(resp.headers.get("Content-Length", 0) or 0)
        read = 0
        while True:
            chunk = resp.read(32768)
            if not chunk:
                break
            buf.write(chunk)
            read += len(chunk)
            if progress_cb:
                progress_cb(read, total)
    buf.seek(0)
    os.makedirs(dest_dir, exist_ok=True)
    count = 0
    with zipfile.ZipFile(buf) as z:
        for member in z.namelist():
            # CHANGE THIS LINE: Use standard zipfile metadata check for directories
            if z.getinfo(member).is_dir():
                continue
            
            rel = member.split("/", 1)[1] if "/" in member else member
            if not rel:
                continue
            target = os.path.join(dest_dir, rel)
            os.makedirs(os.path.dirname(target) or dest_dir, exist_ok=True)
            with z.open(member) as src, open(target, "wb") as out:
                shutil.copyfileobj(src, out)
            count += 1
    return count


_FNAME_RE = re.compile(
    r"^(?P<name>.*?)[\s\[]+(?P<serial>[A-Za-z]{2,4}\d{4,5}[A-Za-z]?)\]?\s*(?:v\s*)?(?P<ver>[\d.]+)?", 
    re.IGNORECASE)


def describe_patch_file(path):
    """Return (game, serial, version) for a downloaded patch file.
    Aggressively falls back to filename tracking if YAML parsing yields empty data."""
    game = serial = ver = ""
    fn = os.path.basename(path)
    
    # 1. Try structural parsing first
    try:
        pf = PatchFile.load(path)
        cheats = pf.all_cheats()
        if cheats:
            for _, c in cheats:
                if c.game:
                    game = c.game
                    if c.serials:
                        serial = c.serials[0]
                    ver = c.version_tag
                    break
    except Exception:
        pass
        
    # 2. If structural parsing found nothing, strictly extract from the filename string
    if not game:
        m = _FNAME_RE.match(fn)
        if m:
            game = m.group("name").strip(" -_[")
            serial = m.group("serial") or ""
            ver = (m.group("ver") or "")
        else:
            # Absolute fallback if regex misses the bracket format entirely
            game = fn

    # Clean up title decorations
    game = game.replace("(Artemis)", "").strip()
    return game, serial, ver


# ============================================================================
#  GUI
# ============================================================================
def launch_gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    # -- XMB animated header --------------------------------------------------
    class XMBHeader(tk.Canvas):
        def __init__(self, master, height=92):
            super().__init__(master, height=height, highlightthickness=0, bg=BG)
            self.h = height
            self.phase = 0.0
            self.bind("<Configure>", lambda e: self._draw_static())
            self._animate()

        def _draw_static(self):
            self.delete("static")
            w = max(self.winfo_width(), 10)
            h = self.h
            c1, c2 = _rgb(GRAD1), _rgb(GRAD2)
            for i in range(h):
                t = i / h
                self.create_line(0, i, w, i, fill=_hx(_mix(c1, c2, t)),
                                 tags="static")
            self.create_oval(22, h // 2 - 14, 50, h // 2 + 14, outline=ACCENT,
                             width=2, tags="static")
            self.create_text(36, h // 2, text="A", fill=ACCENT2,
                             font=("Segoe UI", 16, "bold"), tags="static")
            self.create_text(66, h // 2 - 11, anchor="w", text="ARTEMIS",
                             fill=FG, font=("Segoe UI", 20, "bold"), tags="static")
            self.create_text(67, h // 2 + 12, anchor="w",
                             text="RPCS3  CHEAT  MANAGER", fill=ACCENT2,
                             font=("Segoe UI", 9, "bold"), tags="static")
            self.create_text(w - 16, h // 2, anchor="e",
                             text="PS3 PATCH TOOLKIT", fill=MUTED,
                             font=("Segoe UI", 9), tags="static")

        def _animate(self):
            if not self.winfo_exists():
                return
            self.delete("wave")
            w = max(self.winfo_width(), 10)
            h = self.h
            for off, col in ((8, WAVE1), (4, WAVE2), (0, WAVE3)):
                pts = []
                for x in range(0, w + 10, 10):
                    y = (h * 0.74 + off
                         + math.sin(x / w * 6.283 + self.phase) * 6
                         + math.sin(x / w * 13 + self.phase * 1.6) * 2.5)
                    pts += [x, y]
                if len(pts) >= 4:
                    self.create_line(*pts, fill=col, width=1, smooth=True,
                                     tags="wave")
            self.phase += 0.09
            self.after(70, self._animate)

    class App(tk.Tk):
        def __init__(self):
            super().__init__()
            # Change this line to include the global version variable
            self.title(f"ARTEMIS - RPCS3 Cheat Manager ({VERSION})")
            self.geometry("1280x720")
            self.minsize(900, 600)
            self._egg_buffer = ""

            self.month = resolve_month()
            apply_month(self.month)
            self.configure(bg=BG)

            self.settings = self._load_settings()
            self.library_dir = os.path.join(data_dir(), LIBRARY_DIRNAME)
            self.path = None
            self.model = PatchFile("Version: 1.2\n")
            self._tree_map = {}
            self._lib_map = {}
            self._themed_texts = []
            self._chips = []

            self._setup_theme()
            self.header = XMBHeader(self)
            self.header.pack(fill="x")
            self._build_menu()
            self._build_tabs()
            self._startup_open()
            self.bind_all("<Key>", self._on_global_key)

        # ---- settings / persistence ----------------------------------------
        def _settings_path(self):
            return os.path.join(data_dir(), "artemis_settings.json")

        def _load_settings(self):
            try:
                with open(self._settings_path(), "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}

        def _save_settings(self):
            try:
                with open(self._settings_path(), "w", encoding="utf-8") as f:
                    json.dump(self.settings, f, indent=2)
            except Exception:
                pass

        def _startup_open(self):
            last = self.settings.get("last_file")
            default = self.settings.get("default_file")
            if last and os.path.isfile(last):
                self._load_path(last)
            elif default and os.path.isfile(default):
                self._load_path(default)
            else:
                self._open_empty()

        # ---- live re-theme (month preview) ---------------------------------
        def set_month(self, month):
            self.month = month
            apply_month(month)
            self._setup_theme()
            self.configure(bg=BG)
            for t in self._themed_texts:
                self._style_text(t)
            if hasattr(self, "status_lbl"):
                self.status_lbl.configure(bg=BG)
            for tv in (getattr(self, "tree", None), getattr(self, "lib_tree", None)):
                if tv is not None:
                    tv.tag_configure("game", foreground=ACCENT2)
                    tv.tag_configure("bad", foreground=BAD)
            for frame, dot, lbl in self._chips:
                for w in (frame, dot, lbl):
                    w.configure(bg=BG3)
                lbl.configure(fg=FG)
            self.header._draw_static()

        # ---- theme ---------------------------------------------------------
        def _setup_theme(self):
            self.option_add("*TCombobox*Listbox.background", BG2)
            self.option_add("*TCombobox*Listbox.foreground", FG)
            self.option_add("*TCombobox*Listbox.selectBackground", SEL)
            st = ttk.Style(self)
            try:
                st.theme_use("clam")
            except tk.TclError:
                pass
            st.configure(".", background=BG, foreground=FG, bordercolor=BORDER,
                         fieldbackground=BG2, focuscolor=ACCENT)
            st.configure("TFrame", background=BG)
            st.configure("Panel.TFrame", background=BG2)
            st.configure("TLabel", background=BG, foreground=FG)
            st.configure("Muted.TLabel", background=BG, foreground=MUTED)
            st.configure("Head.TLabel", background=BG, foreground=ACCENT2,
                         font=("Segoe UI", 13, "bold"))
            st.configure("TNotebook", background=BG, borderwidth=0)
            st.configure("TNotebook.Tab", background=BG3, foreground=MUTED,
                         padding=(18, 9), borderwidth=0)
            st.map("TNotebook.Tab", background=[("selected", BG2)],
                   foreground=[("selected", ACCENT2)])
            st.configure("Treeview", background=BG2, fieldbackground=BG2,
                         foreground=FG, rowheight=26, borderwidth=0)
            st.configure("Treeview.Heading", background=BG3, foreground=ACCENT2,
                         relief="flat")
            st.map("Treeview.Heading", background=[("active", SEL)])
            st.map("Treeview", background=[("selected", SEL)],
                   foreground=[("selected", "#ffffff")])
            st.configure("TButton", background=BG3, foreground=FG, borderwidth=1,
                         padding=(12, 7))
            st.map("TButton", background=[("active", SEL)],
                   bordercolor=[("active", ACCENT)])
            st.configure("Accent.TButton", background=ACCENT, foreground="#04101f",
                         font=("Segoe UI", 10, "bold"), padding=(14, 8))
            st.map("Accent.TButton", background=[("active", ACCENT2)])
            st.configure("TEntry", fieldbackground=BG2, foreground=FG,
                         bordercolor=BORDER)
            st.configure("TCombobox", fieldbackground=BG2, foreground=FG,
                         background=BG3, arrowcolor=ACCENT, bordercolor=BORDER)
            st.configure("TScrollbar", background=BG3, troughcolor=BG,
                         bordercolor=BG, arrowcolor=MUTED)
            st.configure("Horizontal.TProgressbar", background=ACCENT,
                         troughcolor=BG3, bordercolor=BORDER,
                         lightcolor=ACCENT, darkcolor=ACCENT)

        def _style_text(self, w):
            w.configure(bg=BG2, fg=FG, insertbackground=FG, selectbackground=SEL,
                        selectforeground="#fff", relief="flat",
                        highlightthickness=1, highlightbackground=BORDER,
                        highlightcolor=ACCENT)
            if w not in self._themed_texts:
                self._themed_texts.append(w)

        # ---- menu ----------------------------------------------------------
        def _build_menu(self):
            mbar = tk.Menu(self, bg=BG2, fg=FG, activebackground=SEL,
                           activeforeground="#fff", borderwidth=0)
            fm = tk.Menu(mbar, tearoff=0, bg=BG2, fg=FG, activebackground=SEL,
                         activeforeground="#fff")
            fm.add_command(label="Open...", command=self.open_file)
            fm.add_command(label="Reload current", command=self.reload_file)
            fm.add_separator()
            fm.add_command(label="Save... (choose where)", command=self.save_file)
            fm.add_separator()
            fm.add_command(label="Open pinned default", command=self.open_default)
            fm.add_command(label="Pin current as default",
                           command=self.pin_default)
            fm.add_command(label="Clear pinned default", command=self.clear_default)
            fm.add_separator()
            fm.add_command(label="Quit", command=self.destroy)
            mbar.add_cascade(label="File", menu=fm)
            self.config(menu=mbar)

        # ---- tabs ----------------------------------------------------------
        def _build_tabs(self):
            self.nb = ttk.Notebook(self)
            self.nb.pack(fill="both", expand=True, padx=8, pady=8)
            self._build_cheats_tab()
            self._build_library_tab()
            self._build_about_tab()

        def _build_cheats_tab(self):
            tab = ttk.Frame(self.nb)
            self.nb.add(tab, text="  Cheats  ")
            top = ttk.Frame(tab)
            top.pack(fill="x", padx=4, pady=(4, 2))
            self.path_lbl = ttk.Label(top, text="", style="Muted.TLabel",
                                      anchor="w")
            self.path_lbl.pack(side="left", fill="x", expand=True)
            ttk.Button(top, text="Save\u2026",
                       command=self.save_file).pack(side="right")
            ttk.Button(top, text="Reload",
                       command=self.reload_file).pack(side="right", padx=4)
            self.default_btn = ttk.Menubutton(top, text="\u2605 Default")
            dmenu = tk.Menu(self.default_btn, tearoff=0, bg=BG2, fg=FG,
                            activebackground=SEL, activeforeground="#fff")
            dmenu.add_command(label="Open pinned default",
                              command=self.open_default)
            dmenu.add_command(label="Pin current as default",
                              command=self.pin_default)
            dmenu.add_command(label="Clear pinned default",
                              command=self.clear_default)
            self.default_btn["menu"] = dmenu
            self.default_btn.pack(side="right", padx=4)
            ttk.Button(top, text="Browse\u2026",
                       command=self.open_file).pack(side="right", padx=4)
            ttk.Button(top, text="Get Latest Patches",
                       command=lambda: self.nb.select(1)).pack(side="right",
                                                               padx=(0, 12))

            paned = ttk.Panedwindow(tab, orient="horizontal")
            paned.pack(fill="both", expand=True, padx=4, pady=4)

            left = ttk.Frame(paned)
            paned.add(left, weight=1)
            ttk.Label(left, text="Games & Cheats",
                      style="Head.TLabel").pack(anchor="w", pady=(0, 4))
            tf = ttk.Frame(left)
            tf.pack(fill="both", expand=True)
            self.tree = ttk.Treeview(tf, show="tree", selectmode="browse")
            tsb = ttk.Scrollbar(tf, command=self.tree.yview)
            self.tree.config(yscrollcommand=tsb.set)
            self.tree.pack(side="left", fill="both", expand=True)
            tsb.pack(side="right", fill="y")
            self.tree.tag_configure("game", foreground=ACCENT2)
            self.tree.tag_configure("bad", foreground=BAD)
            self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
            row = ttk.Frame(left)
            row.pack(fill="x", pady=4)
            ttk.Button(row, text="Expand all",
                       command=lambda: self._expand(True)).pack(side="left")
            ttk.Button(row, text="Collapse all",
                       command=lambda: self._expand(False)).pack(side="left",
                                                                 padx=4)
            ttk.Button(row, text="Delete cheat",
                       command=self.delete_selected).pack(side="right")
            self.count_lbl = ttk.Label(left, text="", style="Muted.TLabel")
            self.count_lbl.pack(anchor="w")

            self.right_nb = ttk.Notebook(paned)
            paned.add(self.right_nb, weight=2)
            self._build_details(self.right_nb)
            self._build_add_form(self.right_nb)

        def _build_details(self, parent):
            f = ttk.Frame(parent)
            parent.add(f, text="  Details (Edit)  ")
            
            # The unlocked text editor
            self.detail = tk.Text(f, wrap="none", font=("Consolas", 10))
            self._style_text(self.detail)
            
            ysb = ttk.Scrollbar(f, command=self.detail.yview)
            xsb = ttk.Scrollbar(f, orient="horizontal", command=self.detail.xview)
            self.detail.config(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
            
            # The new save button
            self.save_edit_btn = ttk.Button(f, text="Save Changes to Cheat", command=self.save_cheat_edits)
            
            # Layout
            self.detail.grid(row=0, column=0, sticky="nsew")
            ysb.grid(row=0, column=1, sticky="ns")
            xsb.grid(row=1, column=0, sticky="ew")
            self.save_edit_btn.grid(row=2, column=0, columnspan=2, pady=(6, 0), sticky="e")
            
            f.rowconfigure(0, weight=1)
            f.columnconfigure(0, weight=1)
            
            self.detail.tag_config("bad", foreground=BAD)
            self.detail.tag_config("key", foreground=ACCENT2)

        def _build_add_form(self, parent):
            f = ttk.Frame(parent)
            parent.add(f, text="  Add Cheat  ")
            
            # --- Meta Data Grid (Name, Game, Hash, etc) ---
            grid = ttk.Frame(f)
            grid.pack(fill="x", padx=6, pady=6)
            self.e_hash = ttk.Combobox(grid, values=self.model.hashes())
            self.e_name = ttk.Entry(grid)
            self.e_game = ttk.Entry(grid)
            self.e_serial = ttk.Entry(grid)
            self.e_tag = ttk.Entry(grid)
            self.e_author = ttk.Entry(grid)
            self.e_notes = ttk.Entry(grid)
            self.e_tag.insert(0, "All")
            for r, (t, w) in enumerate([
                    ("PPU hash:", self.e_hash), ("Cheat name:", self.e_name),
                    ("Game title:", self.e_game), ("Serial(s):", self.e_serial),
                    ("Version tag:", self.e_tag), ("Author:", self.e_author),
                    ("Notes:", self.e_notes)]):
                ttk.Label(grid, text=t).grid(row=r, column=0, sticky="w", pady=2)
                w.grid(row=r, column=1, sticky="ew", pady=2)
                w.bind("<KeyRelease>", lambda e: self.validate_form())
            grid.columnconfigure(1, weight=1)

            # --- NEW Quick Add Helper (Address & Value boxes) ---
            helper_frame = ttk.Frame(f)
            helper_frame.pack(fill="x", padx=6, pady=(8, 2))
            
            ttk.Label(helper_frame, text="Quick Add Line:", style="Head.TLabel").pack(side="left", padx=(0, 10))
            
            # The full, real list of supported RPCS3 patch types
            all_patch_types = [
                "byte", "be16", "le16", "be32", "le32", "bd32", 
                "be64", "le64", "bd64", "bef32", "lef32", "bef64", "lef64",
                "utf8", "cutf8", "c_utf8", "jump", "jump_link", 
                "alloc", "code_alloc", "load", "move_file", "hide_file", "bpex"
            ]
            
            # Dropdown for the Type (Width increased to 11 to fit 'code_alloc')
            self.hlp_type = ttk.Combobox(helper_frame, values=all_patch_types, width=11, state="readonly")
            self.hlp_type.set("be32") # Defaults to be32 as it is the most common PS3 data type
            self.hlp_type.pack(side="left", padx=2)
            
            # Entry for Address / Offset
            self.hlp_addr = ttk.Entry(helper_frame, width=14)
            self.hlp_addr.insert(0, "Address")
            self.hlp_addr.bind("<FocusIn>", lambda e: self.hlp_addr.delete(0, 'end') if self.hlp_addr.get() == "Address" else None)
            self.hlp_addr.pack(side="left", padx=2)
            
            # Entry for Value
            self.hlp_val = ttk.Entry(helper_frame, width=14)
            self.hlp_val.insert(0, "Value")
            self.hlp_val.bind("<FocusIn>", lambda e: self.hlp_val.delete(0, 'end') if self.hlp_val.get() == "Value" else None)
            self.hlp_val.pack(side="left", padx=2)
            
            def add_helper_line():
                t = self.hlp_type.get().strip()
                a = self.hlp_addr.get().strip()
                v = self.hlp_val.get().strip()
                if a and v and a != "Address" and v != "Value":
                    # Format it perfectly for RPCS3 and add a newline
                    line = f"- [ {t}, {a}, {v} ]\n"
                    self.patch_text.insert("end", line)
                    # Clear the boxes so you can quickly paste the next line
                    self.hlp_addr.delete(0, "end")
                    self.hlp_val.delete(0, "end")
                    self.hlp_addr.focus_set()
                    self.validate_form()
            
            ttk.Button(helper_frame, text="Insert \u2193", command=add_helper_line).pack(side="left", padx=(4, 0))

            # --- Raw Patch Text Box ---
            ttk.Label(f, text="Raw Patch list (You can still type directly here):", style="Muted.TLabel").pack(anchor="w", padx=6, pady=(6, 0))
            pf = ttk.Frame(f)
            pf.pack(fill="both", expand=True, padx=6)
            self.patch_text = tk.Text(pf, height=8, wrap="none", font=("Consolas", 10), undo=True)
            self._style_text(self.patch_text)
            psb = ttk.Scrollbar(pf, command=self.patch_text.yview)
            self.patch_text.config(yscrollcommand=psb.set)
            self.patch_text.pack(side="left", fill="both", expand=True)
            psb.pack(side="right", fill="y")
            self.patch_text.tag_config("err", foreground=BAD)
            self.patch_text.bind("<KeyRelease>", lambda e: self.validate_form())

            # --- Status and Validate Bar ---
            bar = ttk.Frame(f)
            bar.pack(fill="x", padx=6, pady=6)
            self.status_lbl = tk.Label(bar, text="", anchor="w", bg=BG, fg=BAD)
            self.status_lbl.pack(side="left", fill="x", expand=True)
            self.add_btn = ttk.Button(bar, text="Add to file",
                                      style="Accent.TButton", command=self.add_cheat)
            self.add_btn.pack(side="right")
            ttk.Button(bar, text="Validate",
                       command=self.validate_form).pack(side="right", padx=4)
            self.validate_form()

        # ---- library tab ---------------------------------------------------
        def _build_library_tab(self):
            tab = ttk.Frame(self.nb)
            self.nb.add(tab, text="  Patch Library  ")
            head = ttk.Frame(tab)
            head.pack(fill="x", padx=8, pady=(8, 2))
            ttk.Label(head, text="Artemis Patch Collection",
                      style="Head.TLabel").pack(anchor="w")
            ttk.Label(head, text="github.com/%s/%s" % (GITHUB_OWNER, GITHUB_REPO),
                      style="Muted.TLabel").pack(anchor="w")

            bar = ttk.Frame(tab)
            bar.pack(fill="x", padx=8, pady=6)
            self.dl_btn = ttk.Button(bar, text="\u2b07  DOWNLOAD / UPDATE",
                                     style="Accent.TButton",
                                     command=self.start_download)
            self.dl_btn.pack(side="left")
            ttk.Button(bar, text="Open repo on GitHub",
                       command=lambda: webbrowser.open(SOCIALS[-1][1])).pack(
                side="left", padx=6)
            self.progress = ttk.Progressbar(bar, mode="determinate", length=240)
            self.progress.pack(side="left", padx=10)
            self.dl_status = ttk.Label(bar, text="", style="Muted.TLabel")
            self.dl_status.pack(side="left")

            sf = ttk.Frame(tab)
            sf.pack(fill="x", padx=8)
            ttk.Label(sf, text="Search:", style="Muted.TLabel").pack(side="left")
            self.lib_search = ttk.Entry(sf)
            self.lib_search.pack(side="left", fill="x", expand=True, padx=6)
            self.lib_search.bind("<KeyRelease>", lambda e: self._refresh_library())

            paned = ttk.Panedwindow(tab, orient="horizontal")
            paned.pack(fill="both", expand=True, padx=8, pady=8)
            lf = ttk.Frame(paned)
            paned.add(lf, weight=1)
            self.lib_tree = ttk.Treeview(lf, show="tree", selectmode="browse")
            lsb = ttk.Scrollbar(lf, command=self.lib_tree.yview)
            self.lib_tree.config(yscrollcommand=lsb.set)
            self.lib_tree.pack(side="left", fill="both", expand=True)
            lsb.pack(side="right", fill="y")
            self.lib_tree.tag_configure("game", foreground=ACCENT2)
            self.lib_tree.tag_configure("new_item", foreground="#e0a02a") # Vibrant gold accent
            self.lib_tree.bind("<<TreeviewSelect>>", self.on_lib_select)
            self.lib_tree.bind("<Double-1>", lambda e: self.open_library_file())

            rf = ttk.Frame(paned)
            paned.add(rf, weight=2)
            btns = ttk.Frame(rf)
            btns.pack(fill="x")
            ttk.Button(btns, text="Open in editor",
                       command=self.open_library_file).pack(side="left")
            ttk.Button(btns, text="Merge into current file",
                       command=self.merge_library_file).pack(side="left", padx=6)
            self.lib_preview = tk.Text(rf, wrap="none", font=("Consolas", 9),
                                       state="disabled")
            self._style_text(self.lib_preview)
            self.lib_preview.pack(fill="both", expand=True, pady=6)
            self._lib_files = []
            self._refresh_library()

        # ---- about tab -----------------------------------------------------
        def _build_about_tab(self):
            tab = ttk.Frame(self.nb)
            self.nb.add(tab, text="  About  ")
            wrap = ttk.Frame(tab)
            wrap.place(relx=0.5, rely=0.42, anchor="center")
            ttk.Label(wrap, text="ARTEMIS", font=("Segoe UI", 26, "bold"),
                      background=BG, foreground=FG).pack()
            ttk.Label(wrap, text="RPCS3 Cheat Manager  \u2022  by ChiDreams",
                      style="Muted.TLabel").pack(pady=(0, 4))
            ttk.Label(wrap, text="PS3 netcheat codes ported to RPCS3 patch.yml",
                      style="Muted.TLabel").pack(pady=(0, 16))
            ttk.Label(wrap, text="Find me here", style="Head.TLabel").pack()
            chips = ttk.Frame(wrap)
            chips.pack(pady=8)
            for i, (label, url, color) in enumerate(SOCIALS):
                self._social_chip(chips, label, url, color, i)
            ttk.Label(wrap, text="cheats by dron_3  \u2022  ported by ChiDreams",
                      style="Muted.TLabel").pack(pady=(18, 0))

            mrow = ttk.Frame(wrap)
            mrow.pack(pady=(14, 0))
            ttk.Label(mrow, text="XMB theme:",
                      style="Muted.TLabel").pack(side="left", padx=(0, 6))
            months = ["Auto (this month)", "January", "February", "March",
                      "April", "May", "June", "July", "August", "September",
                      "October", "November", "December"]
            self.month_box = ttk.Combobox(mrow, values=months, width=18,
                                          state="readonly")
            self.month_box.current(0)  # default to Auto (follows real month)
            self.month_box.pack(side="left")
            self.month_box.bind("<<ComboboxSelected>>", self._on_month_pick)

            ttk.Label(wrap, text="( psst \u2014 there's a secret in here )",
                      foreground="#3b4a66", background=BG,
                      font=("Segoe UI", 8, "italic")).pack(pady=(10, 0))
            ttk.Label(wrap, text=f"RPCS3 Cheat Manager {VERSION}  •  by ChiDreams",
                      style="Muted.TLabel").pack(pady=(0, 4))
        def _on_month_pick(self, _evt):
            idx = self.month_box.current()
            self.set_month(resolve_month() if idx == 0 else idx)
            if getattr(self, "lib_tree", None) is not None:
                self.lib_tree.tag_configure("new_item", foreground="#e0a02a")

        def _social_chip(self, parent, label, url, color, idx):
            row, col = divmod(idx, 3)
            frame = tk.Frame(parent, bg=BG3, highlightthickness=1,
                             highlightbackground=BORDER, cursor="hand2")
            frame.grid(row=row, column=col, padx=6, pady=6, sticky="ew")
            dot = tk.Canvas(frame, width=14, height=14, bg=BG3,
                            highlightthickness=0)
            dot.create_oval(2, 2, 12, 12, fill=color, outline="")
            dot.pack(side="left", padx=(10, 6), pady=8)
            lbl = tk.Label(frame, text=label, bg=BG3, fg=FG,
                           font=("Segoe UI", 11, "bold"))
            lbl.pack(side="left", padx=(0, 14), pady=8)

            def enter(_):
                for w in (frame, dot, lbl):
                    w.configure(bg=SEL)
            def leave(_):
                for w in (frame, dot, lbl):
                    w.configure(bg=BG3)
            def click(_):
                webbrowser.open(url)
            for w in (frame, dot, lbl):
                w.bind("<Enter>", enter)
                w.bind("<Leave>", leave)
                w.bind("<Button-1>", click)
            self._chips.append((frame, dot, lbl))

        # ---- file handling -------------------------------------------------
        def _open_empty(self):
            self.path = None
            self.model = PatchFile(
                "Version: 1.2\n\n# No file loaded. Use Browse\u2026 to open your "
                "patch.yml,\n# or download a collection from 'Patch Library'.\n")
            self.refresh_tree()
            self._update_path_label()
            if hasattr(self, "e_hash"):
                self.e_hash["values"] = self.model.hashes()

        def _load_path(self, path):
            try:
                self.model = PatchFile.load(path)
            except Exception as e:
                messagebox.showerror("Load error",
                                     "Couldn't open:\n%s\n\n%s" % (path, e))
                return False
            self.path = path
            self.settings["last_file"] = path
            self.settings["last_dir"] = os.path.dirname(path)
            self._save_settings()
            self.refresh_tree()
            self._update_path_label()
            if hasattr(self, "e_hash"):
                self.e_hash["values"] = self.model.hashes()
            return True

        def _update_path_label(self):
            if not self.path:
                self.path_lbl.config(text="No file loaded \u2014 click Browse\u2026")
                return
            star = ""
            if self.path == self.settings.get("default_file"):
                star = "\u2605 default  \u2022  "
            self.path_lbl.config(text=star + "File:  " + self.path)

        def _initial_dir(self):
            for cand in (os.path.dirname(self.path) if self.path else None,
                         self.settings.get("last_dir")):
                if cand and os.path.isdir(cand):
                    return cand
            return os.path.expanduser("~")

        def reload_file(self):
            if self.path and os.path.isfile(self.path):
                self._load_path(self.path)
            else:
                self._open_empty()

        # ---- pinned default ------------------------------------------------
        def pin_default(self):
            if not self.path:
                messagebox.showinfo("Pin default",
                                    "Open a file first, then pin it as default.")
                return
            self.settings["default_file"] = self.path
            self._save_settings()
            self._update_path_label()
            messagebox.showinfo("Pinned",
                                "Pinned as default:\n%s\n\nUse File \u2192 'Open "
                                "pinned default' to jump back to it anytime."
                                % self.path)

        def clear_default(self):
            if self.settings.pop("default_file", None):
                self._save_settings()
                self._update_path_label()
                messagebox.showinfo("Default cleared", "Pinned default removed.")
            else:
                messagebox.showinfo("Default", "No default is pinned.")

        def open_default(self):
            d = self.settings.get("default_file")
            if not d:
                messagebox.showinfo("Default", "No default pinned yet.\n\n"
                                    "Open a file and choose 'Pin current as "
                                    "default'.")
                return
            if not os.path.isfile(d):
                messagebox.showwarning("Default missing",
                                       "The pinned default no longer exists:\n"
                                       "%s" % d)
                return
            self._load_path(d)
            self.nb.select(0)

        # ---- left tree -----------------------------------------------------
        def refresh_tree(self):
            self.tree.delete(*self.tree.get_children())
            self._tree_map = {}
            groups, order = {}, []
            for g, c in self.model.all_cheats():
                serial = c.serials[0] if c.serials else ""
                key = (c.game or g.hash[:18], serial, c.version_tag)
                if key not in groups:
                    groups[key] = []
                    order.append(key)
                groups[key].append((g, c))
            total = 0
            for key in order:
                game, serial, ver = key
                bits = [game]
                if serial:
                    bits.append("[%s]" % serial)
                if ver:
                    bits.append("v%s" % ver)
                pid = self.tree.insert("", "end", text="  ".join(bits),
                                       open=True, tags=("game",))
                for g, c in groups[key]:
                    total += 1
                    bad = any(not ok for (_, ok, _) in c.patch_lines)
                    txt = ("   \u26a0 " + c.name) if bad else ("   " + c.name)
                    iid = self.tree.insert(pid, "end", text=txt,
                                           tags=("bad",) if bad else ())
                    self._tree_map[iid] = (g, c)
            self.count_lbl.config(text="%d game(s)  \u2022  %d cheat(s)"
                                       % (len(order), total))

        def _expand(self, flag):
            for iid in self.tree.get_children():
                self.tree.item(iid, open=flag)

        def on_tree_select(self, _evt):
            sel = self.tree.selection()
            if not sel or sel[0] not in self._tree_map:
                return
            g, c = self._tree_map[sel[0]]
            
            # --- Auto-switch to the Details tab so you can see the code! ---
            if hasattr(self, "right_nb"):
                self.right_nb.select(0)
            
            # Clear the box and insert the pure raw text
            self.detail.delete("1.0", "end")
            self.detail.insert("end", c.raw)
            
            # Highlight bad lines visually without altering the text
            for i, line in enumerate(c.raw.split("\n"), start=1):
                if line.strip().startswith("- "):
                    ok, _ = validate_patch_line(line)
                    if not ok:
                        self.detail.tag_add("bad", f"{i}.0", f"{i}.end")

        def delete_selected(self):
            sel = self.tree.selection()
            if not sel or sel[0] not in self._tree_map:
                messagebox.showinfo("Delete", "Select a cheat (not a game).")
                return
            g, c = self._tree_map[sel[0]]
            if messagebox.askyesno("Delete cheat", "Delete cheat '%s'?" % c.name):
                self.model.delete_cheat(c)
                self.refresh_tree()
                self.detail.config(state="normal")
                self.detail.delete("1.0", "end")
                self.detail.config(state="disabled")

        def save_cheat_edits(self):
            sel = self.tree.selection()
            if not sel or sel[0] not in self._tree_map:
                from tkinter import messagebox
                messagebox.showinfo("Edit", "Select a cheat from the list first.")
                return
                
            # Get the current cheat and the edited text
            g, c = self._tree_map[sel[0]]
            new_text = self.detail.get("1.0", "end-1c")
            
            # Update the model
            self.model.update_cheat(c, new_text)
            
            # Refresh the UI list
            self.refresh_tree()
            
            # Let the user know it worked
            if hasattr(self, "status_lbl"):
                self.status_lbl.config(text="\u2713  Cheat updated (Remember to click Save… at the top!)", fg=GOOD)
                
        # ---- validation / add ---------------------------------------------
        def validate_form(self):
            self.patch_text.tag_remove("err", "1.0", "end")
            raw = self.patch_text.get("1.0", "end-1c")
            first_err, any_patch = "", False
            for i, line in enumerate(raw.split("\n"), start=1):
                if line.strip() == "":
                    continue
                ok, msg = validate_patch_line(line)
                if not line.strip().startswith("#"):
                    any_patch = True
                if not ok:
                    self.patch_text.tag_add("err", "%d.0" % i, "%d.end" % i)
                    if not first_err:
                        first_err = "Line %d: %s" % (i, msg)
            problems = []
            if not self.e_hash.get().strip():
                problems.append("PPU hash required")
            if not self.e_name.get().strip():
                problems.append("cheat name required")
            if not self.e_game.get().strip():
                problems.append("game title required")
            if not self.e_serial.get().strip():
                problems.append("serial required")
            if not any_patch:
                problems.append("need a patch line")
            if first_err:
                problems.append(first_err)
            if problems:
                self.status_lbl.config(
                    text="\u2717  " + "  \u2022  ".join(problems), fg=BAD)
                try:
                    self.add_btn.state(["disabled"])
                except Exception:
                    pass
                return False
            self.status_lbl.config(text="\u2713  ready to add", fg=GOOD)
            try:
                self.add_btn.state(["!disabled"])
            except Exception:
                pass
            return True

        def add_cheat(self):
            if not self.validate_form():
                self.status_lbl.config(text="\u2717  fix the red items first",
                                       fg=BAD)
                return
            patch_lines = [l for l in self.patch_text.get("1.0", "end-1c").split("\n")
                           if l.strip()]
            block = self.model.build_cheat_block(
                name=self.e_name.get().strip(), game=self.e_game.get().strip(),
                serial=self.e_serial.get().strip(),
                version_tag=self.e_tag.get().strip(),
                author=self.e_author.get().strip(),
                notes=self.e_notes.get().strip(), patch_lines=patch_lines)
            self.model.add_cheat(self.e_hash.get().strip(), block)
            self.refresh_tree()
            self.e_hash["values"] = self.model.hashes()
            self.status_lbl.config(text="\u2713  added '%s' (remember to Save)"
                                        % self.e_name.get().strip(), fg=GOOD)
            self.e_name.delete(0, "end")
            self.patch_text.delete("1.0", "end")
            self.validate_form()

        # ---- file ops ------------------------------------------------------
        def open_file(self):
            p = filedialog.askopenfilename(
                title="Open a patch file",
                initialdir=self._initial_dir(),
                filetypes=[("Patch files", "*.yml *.yaml"),
                           ("All files", "*.*")])
            if p:
                self._load_path(p)
                self.nb.select(0)

        def save_file(self):
            # Always ask where to save; default to the loaded file so a quick
            # Enter overwrites it, but any other RPCS3 location is one click away.
            initial_dir = self._initial_dir()
            initial_name = os.path.basename(self.path) if self.path \
                else DEFAULT_FILE
            p = filedialog.asksaveasfilename(
                title="Save patch file as",
                initialdir=initial_dir, initialfile=initial_name,
                defaultextension=".yml",
                filetypes=[("Patch file", "*.yml *.yaml"),
                           ("All files", "*.*")])
            if not p:
                return
            try:
                self.model.save(p)
            except Exception as e:
                messagebox.showerror("Save error", str(e))
                return
            self.path = p
            self.settings["last_file"] = p
            self.settings["last_dir"] = os.path.dirname(p)
            self._save_settings()
            self._update_path_label()
            if hasattr(self, "status_lbl"):
                self.status_lbl.config(text="\u2713  saved", fg=GOOD)
            messagebox.showinfo("Saved", "Saved to:\n%s\n\n"
                                "(a timestamped .bak was made if it existed)" % p)

        # ---- library -------------------------------------------------------
        def start_download(self):
            try:
                self.dl_btn.state(["disabled"])
            except Exception:
                pass
            self.progress["value"] = 0
            self.dl_status.config(text="Connecting to GitHub...")
            threading.Thread(target=self._download_worker, daemon=True).start()

        def _download_worker(self):
            def prog(read, total):
                self.after(0, self._set_progress, read, total)
            try:
                req = urllib.request.Request(ZIP_URL, headers={"User-Agent": "ArtemisCheatManager/1.0"})
                buf = io.BytesIO()
                with urllib.request.urlopen(req, timeout=60) as resp:
                    total = int(resp.headers.get("Content-Length", 0) or 0)
                    read = 0
                    while True:
                        chunk = resp.read(32768)
                        if not chunk: break
                        buf.write(chunk)
                        read += len(chunk)
                        prog(read, total)
                buf.seek(0)
                
                os.makedirs(self.library_dir, exist_ok=True)
                count = 0
                
                with zipfile.ZipFile(buf) as z:
                    for info in z.infolist():
                        if info.is_dir():
                            continue
                        
                        parts = info.filename.split('/')
                        if len(parts) <= 1:
                            continue
                        
                        raw_filename = parts[-1]
                        if not raw_filename or raw_filename.upper() == "LICENSE" or raw_filename.startswith('.'):
                            continue
                        
                        # Fix the filename string just like a web browser does
                        clean_filename = raw_filename.replace(":", " -")
                        for char in ['*', '?', '"', '<', '>', '|']:
                            clean_filename = clean_filename.replace(char, "")
                            
                        target = os.path.join(self.library_dir, clean_filename)
                        
                        with z.open(info) as src:
                            file_data = src.read()
                        
                        with open(target, "wb") as out:
                            out.write(file_data)
                            
                        count += 1
                        
                self.after(0, self._download_done, count, None)
            except Exception as e:
                self.after(0, self._download_done, 0, e)
        def _set_progress(self, read, total):
            if total > 0:
                self.progress["maximum"] = total
                self.progress["value"] = read
                self.dl_status.config(text="Downloading...  %d KB / %d KB"
                                           % (read // 1024, total // 1024))
            else:
                self.dl_status.config(text="Downloading...  %d KB" % (read // 1024))

        def _download_done(self, count, err):
            try:
                self.dl_btn.state(["!disabled"])
            except Exception:
                pass
            if err is not None:
                self.dl_status.config(text="Failed.")
                msg = str(err)
                if "SSL" in msg or "CERTIFICATE" in msg.upper():
                    msg += ("\n\nTip: an SSL/certificate error usually means "
                            "Python's CA certificates need installing.")
                messagebox.showerror("Download error", msg)
                return
            self.progress["value"] = self.progress["maximum"] or 1
            self.dl_status.config(text="Done \u2713  %d patch files saved" % count)
            self._refresh_library()

        def _refresh_library(self):
            self.lib_tree.delete(*self.lib_tree.get_children())
            self._lib_map = {}
            if not os.path.isdir(self.library_dir):
                self.lib_tree.insert("", "end",
                                     text="  (nothing downloaded yet \u2014 "
                                          "hit DOWNLOAD / UPDATE)")
                return
            query = (self.lib_search.get() or "").lower()
            files = []
            for fn in sorted(os.listdir(self.library_dir)):
                full = os.path.join(self.library_dir, fn)
                if not os.path.isfile(full) or fn.upper() == "LICENSE" or fn.startswith('.'):
                    continue
                game, serial, ver = describe_patch_file(full)
                
                # Check if the file was added/modified in the last 24 hours
                is_new = False
                try:
                    mtime = os.path.getmtime(full)
                    file_date = datetime.datetime.fromtimestamp(mtime)
                    if (datetime.datetime.now() - file_date).days < 1:
                        is_new = True
                except Exception:
                    pass
                    
                files.append((game, serial, ver, full, is_new))
                
            self._lib_files = files
            shown = 0
            for game, serial, ver, full, is_new in files:
                hay = (game + serial + ver + os.path.basename(full)).lower()
                if query and query not in hay:
                    continue
                bits = []
                
                # Add a visual [NEW] tag to the text if it's fresh
                if is_new:
                    bits.append("[NEW]")
                    
                bits.append(game)
                if serial:
                    bits.append("[%s]" % serial)
                if ver:
                    bits.append("v%s" % ver)
                    
                # Apply a special "new_item" color tag if it's new
                tags = ("new_item",) if is_new else ("game",)
                iid = self.lib_tree.insert("", "end", text="  ".join(bits),
                                           tags=tags)
                self._lib_map[iid] = full
                shown += 1
            if shown == 0 and files:
                self.lib_tree.insert("", "end", text="  (no matches)")

        def on_lib_select(self, _evt):
            sel = self.lib_tree.selection()
            if not sel or sel[0] not in self._lib_map:
                return
            path = self._lib_map[sel[0]]
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    txt = f.read()
            except Exception as e:
                txt = "(could not read file: %s)" % e
            self.lib_preview.config(state="normal")
            self.lib_preview.delete("1.0", "end")
            self.lib_preview.insert("end", txt[:20000])
            self.lib_preview.config(state="disabled")

        def _selected_lib_path(self):
            sel = self.lib_tree.selection()
            if not sel or sel[0] not in self._lib_map:
                messagebox.showinfo("Library", "Select a patch from the list.")
                return None
            return self._lib_map[sel[0]]

        def open_library_file(self):
            path = self._selected_lib_path()
            if path:
                self._load_path(path)
                self.nb.select(0)

        def merge_library_file(self):
            path = self._selected_lib_path()
            if not path:
                return
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    txt = f.read()
            except Exception as e:
                messagebox.showerror("Merge error", str(e))
                return
            self.model.merge_text(
                txt, comment="merged from " + os.path.basename(path))
            self.refresh_tree()
            self.e_hash["values"] = self.model.hashes()
            self.nb.select(0)
            messagebox.showinfo("Merged",
                                "Merged into the current file.\n"
                                "Review on the Cheats tab, then Save.\n\n"
                                "Note: heavy anchor (&/*) collisions across "
                                "files are possible \u2014 check before saving.")

        # ---- easter egg ----------------------------------------------------
        def _on_global_key(self, event):
            ch = event.char
            if not ch or not ch.isprintable():
                return
            self._egg_buffer = (self._egg_buffer + ch.lower())[-len(SECRET_WORD):]
            if self._egg_buffer == SECRET_WORD.lower():
                self._egg_buffer = ""
                self._run_easter_egg()

        def _run_easter_egg(self):
            import random
            top = tk.Toplevel(self)
            top.configure(bg="black")
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            w, h = int(sw * 0.7), int(sh * 0.7)
            top.geometry("%dx%d+%d+%d" % (w, h, (sw - w) // 2, (sh - h) // 2))
            top.transient(self)
            cv = tk.Canvas(top, bg="black", highlightthickness=0)
            cv.pack(fill="both", expand=True)
            glyphs = "01\u30a2\u30a4\u30a6\u30a8\u30aa#%&@$<>=*+ABCDEF0123456789"
            cols = max(1, w // 14)
            drops = [random.randint(-40, 0) for _ in range(cols)]
            running = {"on": True}

            def step():
                if not running["on"] or not top.winfo_exists():
                    return
                cv.delete("rain")
                for x in range(cols):
                    y = drops[x]
                    for k in range(8):
                        yy = (y - k) * 16
                        if 0 <= yy < h:
                            shade = "#0f0" if k == 0 else ("#0a0" if k < 3 else "#060")
                            cv.create_text(x * 14 + 8, yy, text=random.choice(glyphs),
                                           fill=shade, font=("Consolas", 12),
                                           tags="rain")
                    drops[x] = y + 1
                    if y * 16 > h and random.random() > 0.975:
                        drops[x] = random.randint(-20, 0)
                cv.create_text(w // 2, h // 2, text=YOUTUBE_URL, fill="#39ff14",
                               font=("Consolas", 16, "bold"), tags="rain")
                cv.create_text(w // 2, h // 2 + 28,
                               text="ARTEMIS  \u2022  cheats by dron_3",
                               fill="#0a0", font=("Consolas", 10), tags="rain")
                top.after(60, step)

            def close(_=None):
                running["on"] = False
                top.destroy()
            top.bind("<Escape>", close)
            top.bind("<Button-1>", close)
            cv.create_text(w // 2, h - 24, text="press Esc or click to close",
                           fill="#070", font=("Consolas", 9))
            top.after(6500, close)
            step()

    App().mainloop()


# ============================================================================
#  SELF-TESTS
# ============================================================================
def _selftest():
    ok = True

    def check(cond, label):
        nonlocal ok
        if not cond:
            ok = False
        print("[%s] %s" % ("PASS" if cond else "FAIL", label))

    for v in ["- [ be32, 0x00100000, 0x60000000 ]", "be32,0x1598E4,0x386003E8",
              "- [ bef32, 0x00012484, 0.01666667 ]", "- [ load, *Iso] ",
              "- [ byte, 0x00d4d9cf, 0x00 ]",
              "- [ utf8, 0x01851328, \"http://\\0\" ]", "# c", ""]:
        good, msg = validate_patch_line(v)
        check(good, "valid: %r" % v)
    for v in ["- [ be8, 0x10, 0x01 ]", "- [ be16, 0x10, 0x12345 ]",
              "- [ be32, nothex, 0x1 ]", "- [ utf8, 0x10, notquoted ]"]:
        good, _ = validate_patch_line(v)
        check(not good, "invalid: %r" % v)

    sample = (
        "Version: 1.2\n# Title: Black Knight Sword\n# Serial: NPEB00859\n"
        "PPU-2906daff22ed8bd1dbcef94ef8e1ec79b73dba5e:\n"
        "  \"Infinite Health\":\n    Games:\n"
        "      \"Black Knight Sword (Artemis)\":\n"
        "        NPEB00859: [ 01.00 ]\n    Author: Serp87\n    Notes: \n"
        "    Patch Version: 1.2\n    Patch:\n"
        "    - [ be32,0x000AA180,0x60000000]\n")
    pf = PatchFile(sample)
    cs = pf.all_cheats()
    check(len(cs) == 1, "parsed 1 cheat")
    g, c = cs[0]
    check(c.game == "Black Knight Sword (Artemis)", "game: %r" % c.game)
    check(c.serials == ["NPEB00859"], "serial: %r" % c.serials)
    check(c.version_tag == "01.00", "version: %r" % c.version_tag)
    check(c.author == "Serp87", "author: %r" % c.author)

    anc = (
        "Version: 1.2\nAnchors:\n  Iso: &Iso\n"
        "      - [ be32,0x00EE0AA0,0x813FFCF4]\n"
        "PPU-722e92071fb285e30de5bc2d941a24de9130e9d9:\n"
        "  Invincibility:\n    Games:\n"
        "      \"Alien: Isolation (Artemis)\":\n"
        "        BLES01697: [ 01.00 ]\n    Author: Xtatu\n    Notes: \n"
        "    Patch Version: 1.0\n    Patch:\n      - [ load, *Iso ]\n")
    pf2 = PatchFile(anc)
    cs2 = pf2.all_cheats()
    check(len(cs2) == 1, "anchors file: 1 cheat (Anchors not a cheat)")
    check(cs2[0][1].game == "Alien: Isolation (Artemis)", "anchor game parsed")
    check(all(o for _, o, _ in cs2[0][1].patch_lines), "load line valid")

    pf.add_cheat("PPU-2906daff22ed8bd1dbcef94ef8e1ec79b73dba5e",
                 pf.build_cheat_block("Max Hearts", "Black Knight Sword (Artemis)",
                                      "NPEB00859", "01.00", "me", "",
                                      ["be32, 0x000AA184, 0x60000000"]))
    check(len(pf.all_cheats()) == 2, "after add: 2 cheats")
    check("0x000AA180" in pf.text, "old line preserved")
    check("0x000AA184" in pf.text, "new line present")

    pf.merge_text(anc, comment="merged")
    check(len(pf.groups) >= 2, "merge added group(s)")

    import tempfile
    d = tempfile.mkdtemp()
    p = os.path.join(d, "Demon's Souls [BLUS30443] v1.00")
    with open(p, "w", encoding="utf-8") as f:
        f.write("Anchors:\n  X: &X\n    - [ be32,0x1,0x2]\n")
    game, serial, ver = describe_patch_file(p)
    check(serial == "BLUS30443", "filename serial fallback: %r" % serial)

    print("\n%s" % ("ALL TESTS PASSED" if ok else "SOME TESTS FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    launch_gui()
