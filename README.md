# ARTEMIS — RPCS3 Cheat Manager

A single-file, zero-dependency desktop app for managing **RPCS3 `patch.yml`**
cheat files. Built for porting and organizing PS3 cheats (netcheat → RPCS3
patch format), with a PS3 XMB-flavored interface.

Pure **Python 3 + Tkinter** — no `pip install` of anything, no external
libraries. Runs as a script, or build it into a standalone `.exe` that needs
no Python at all.

> Cheats by **dron_3** · ported & tooling by **ChiDreams**

---

## What it does

ARTEMIS reads, validates, edits, and organizes the YAML patch files RPCS3 uses
for cheats. Instead of hand-editing a giant `patch.yml` and hoping the syntax
is right, you get a real UI that understands the format and won't let you write
a broken patch line.

It can also pull the whole **Artemis Patch Collection** straight from GitHub so
you have a browsable library of ready-made cheats.

---

## Features

### Cheats tab — browse & organize
- Cheats are **grouped by game**, shown as `Game  [SERIAL]  vVERSION`, read
  directly from each patch's `Games:` block (falls back to the filename if a
  file has no block).
- Cheats are nested under their game; any cheat with an invalid patch line is
  flagged with a red ⚠ so problems are obvious at a glance.
- **Details** view shows the exact YAML of the selected cheat, with invalid
  lines highlighted and explained.
- Delete cheats, expand/collapse all, live cheat/game counts.

### Add Cheat — with live validation
- A form for hash, name, game, serial(s), version tag, author, notes, and patch
  lines.
- **Every patch line is validated as you type.** Invalid lines turn red with a
  reason (bad type, offset not hex, value out of range for the byte width,
  unquoted string, missing anchor for `load`, etc.).
- New cheats are written in **exact RPCS3 v1.2 format** and **appended without
  disturbing existing formatting** — your hand-tuned file stays intact.

### Patch Library — download from GitHub
- One button downloads the latest patches from
  `chidreams/Artemis-Patch-Collection-RPCS3` (zip via codeload, with a live
  progress bar) and extracts them into a local `Artemis-Patches/` folder.
- Searchable list of every game in the collection.
- **Open in editor** loads a patch as your active file, or **Merge into current
  file** appends it to what you're working on.

### File handling — open anything, anywhere
- **Browse…** opens any patch file from any location (RPCS3's `patches\`,
  `dev_hdd0`, an extension-less collection file — whatever).
- **Remembers your last file** and reopens it on launch.
- **Pinnable default**: bookmark your main working file and snap back to it in
  one click, no matter how many library files you've opened.
- **Save always asks where** (pre-filled with the current file — press Enter to
  overwrite), and makes a timestamped `.bak` before overwriting.
- Settings live in `artemis_settings.json` (next to the app if writable, else
  your per-user app-data folder).

### PS3 / XMB theme
- Animated XMB-style wave header.
- The whole UI **recolors by month**, like the real PS3 "Original" theme —
  icy winter blues → spring pink/green → summer gold → autumn red/brown.
- Auto-follows the real month, or pick any month from the **XMB theme**
  dropdown on the About tab to preview. Lock it with `FORCE_MONTH`.
- (There may or may not be a hidden easter egg. Type around.)

### Validation engine
Understands the real RPCS3 patch types from the emulator's source:
`byte`, `le16`/`be16`, `le32`/`be32`/`bd32`, `le64`/`be64`/`bd64`,
`jump`/`jump_link`, `alloc`/`code_alloc`, floats (`bef32`/`lef32`/`bef64`/
`lef64`), strings (`utf8`/`cutf8`), `load` (with `*anchor`), `move_file`/
`hide_file`, and `bpex` — with width/range checks on integer values.

---

## Running it

You need **Python 3** with Tkinter (bundled on Windows/macOS; on Debian/Ubuntu
Linux install `python3-tk`).

```bash
python cheat_manager.py
```

Run the built-in tests (no GUI):

```bash
python cheat_manager.py --selftest
```

---

## Building a standalone app (no Python needed to run)

PyInstaller is **not** a cross-compiler — build on the OS you want to run on.

**Windows (easy):** put `build_windows_exe.bat` next to `cheat_manager.py` and
double-click it. Output: `dist\ARTEMIS.exe`.

**Any OS (manual):**
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name ARTEMIS cheat_manager.py
```

See `BUILD_STANDALONE.txt` for full details, icons, and notes.

---

## Configuration

Everything tweakable is at the top of `cheat_manager.py`:

| Setting | What it controls |
|---|---|
| `SOCIALS` | Your social links shown on the About tab. Each entry is `("Name", "url", "#dotcolor")`. |
| `SECRET_WORD` | The phrase that triggers the easter egg. |
| `MONTH_BASE` | The 12 signature colors (one per month) the whole theme derives from. |
| `FORCE_MONTH` | Set `1`–`12` to lock the theme to one month; `None` follows the real date. |
| `GITHUB_OWNER` / `GITHUB_REPO` / `GITHUB_BRANCH` | Which repo the Library tab downloads from. |
| `DEFAULT_FILE` | Default filename suggested when saving with nothing loaded. |
| `LIBRARY_DIRNAME` | Folder name the downloaded collection extracts into. |

> ⚠ When editing `SOCIALS`, keep each line shaped exactly like
> `("Name", "https://...", "#color"),` — parentheses around it, all three
> pieces in quotes, comma at the end. A missing `)` or `"` is the usual cause
> of a build/syntax error.

---

## RPCS3 patch format (quick primer)

A cheat lives under a `PPU-<hash>:` block keyed to the game's decrypted
executable hash:

```yaml
Version: 1.2
PPU-<hash>:
  "Infinite Health":
    Games:
      "Game Title":
        BLUS12345: [ 01.00 ]
    Author: You
    Notes: ""
    Patch Version: 1.0
    Patch:
      - [ be32, 0x00100000, 0x60000000 ]
```

The same patch can target multiple regions/versions by listing more serials
under `Games:` — useful when a decrypted ELF is identical across regions (the
**PPU hash** is the definitive check: same hash = same binary = same offsets).

---

## Requirements

- Python 3.8+ with Tkinter (standard library; Linux: `sudo apt install python3-tk`)
- Internet only for the optional GitHub download feature
- For building: `pyinstaller`

---

## Credits & license

- Cheats authored by **dron_3**; ported and maintained by **ChiDreams**.
- Patch collection: https://github.com/chidreams/Artemis-Patch-Collection-RPCS3

License: _add a LICENSE file (MIT is a common choice for tools like this; you
already use one in the patch-collection repo and can reuse it here)._
