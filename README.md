# **ARTEMIS — Patch Manager**  
### **PS3 Cheat Management & Patch Library Tool**

A single‑file, zero‑dependency desktop app for managing **Artemis‑style PS3 cheat patches** (`imported_patch.yml` format and compatible variants).  
Built for porting, organizing, validating, and maintaining PS3 cheats across multiple platforms that support the Artemis patch format.

Pure **Python 3 + Tkinter** — no external libraries, no pip installs. Runs as a script or can be built into a standalone `.exe`.

> Cheats by **Host of Creators** · porting, tooling, and patch management by **ChiDreams**

---

## **Important Disclaimer**

This project is **not supported, endorsed, or affiliated with the RPCS3 team** or any other emulator or PS3 project.  
All patches, tools, and conversions are provided independently by **ChiDreams**.

If you encounter issues, bugs, or need support, **please direct all questions to this repository**, not to the RPCS3 team or any emulator developers.

---

## **What Artemis Patch Manager Does**

Artemis Patch Manager reads, validates, edits, and organizes YAML‑based cheat patch files used by PS3 environments that support the Artemis/RPCS3 patch format.  
Instead of hand‑editing a massive `imported_patch.yml` and hoping the syntax is correct, you get a real UI that understands the format and prevents broken patch lines.

It can also pull the entire **Artemis Patch Collection** directly from GitHub, giving you a browsable library of ready‑made cheats.

---

## **Features**

### **Cheats Tab — Browse & Organize**
- Cheats grouped by game, shown as `Game  [SERIAL]  vVERSION`, read directly from each patch’s `Games:` block.
- Invalid patch lines flagged with a red ⚠ for instant visibility.
- Detailed YAML view with highlighted errors and explanations.
- Expand/collapse all, delete cheats, live counts for games and cheats.

### **Add Cheat — With Live Validation**
- Form for hash, name, game, serials, version, author, notes, and patch lines.
- **Real‑time validation** of every patch line.
- Writes new cheats in **exact Artemis/RPCS3 v1.2 format** without disturbing existing formatting.

### **Patch Library — GitHub Integration**
- One‑click download of the latest patch collection from  
  `chidreams/Artemis-Patch-Collection-RPCS3`.
- Searchable list of all games in the collection.
- Load patches directly into the editor or merge them into your current file.

### **File Handling**
- Open any patch file from any location.
- Remembers your last file and reopens it on launch.
- Bookmark a default working file for fast access.
- Safe saving with timestamped `.bak` backups.
- Settings stored in `artemis_settings.json`.

### **PS3 / XMB Theme**
- Animated XMB‑style wave header.
- Full UI recolors by month, matching the PS3 “Original” theme.
- Preview or lock any month via the About tab.
- Hidden easter egg (type around).

### **Validation Engine**
Understands all real patch types used in Artemis/RPCS3 format, including:

`byte`, `le16`/`be16`, `le32`/`be32`/`bd32`, `le64`/`be64`/`bd64`,  
`jump`, `jump_link`, `alloc`, `code_alloc`,  
`bef32`/`lef32`/`bef64`/`lef64`,  
`utf8`/`cutf8`,  
`load` (with anchors),  
`move_file`, `hide_file`, `bpex`.

Includes width/range checks and strict YAML validation.

---

## **Running It**

Requires **Python 3** with Tkinter (bundled on Windows/macOS; Linux users install `python3-tk`).

```bash
python cheat_manager.py
```

Run built‑in tests:

```bash
python cheat_manager.py --selftest
```

---

## **Building a Standalone App**

PyInstaller builds per‑OS (not cross‑platform).

### **Windows**
Place `build_windows_exe.bat` next to `cheat_manager.py` and double‑click.  
Output: `dist/ARTEMIS.exe`.

### **Manual Build**
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name ARTEMIS cheat_manager.py
```

See `BUILD_STANDALONE.txt` for full details.

---

## **Configuration**

Editable at the top of `cheat_manager.py`:

| Setting | Description |
|--------|-------------|
| `SOCIALS` | Social links shown on the About tab. |
| `SECRET_WORD` | Easter egg trigger phrase. |
| `MONTH_BASE` | Base colors for each month. |
| `FORCE_MONTH` | Lock theme to a specific month. |
| `GITHUB_OWNER` / `GITHUB_REPO` / `GITHUB_BRANCH` | Patch library source. |
| `DEFAULT_FILE` | Default filename when saving. |
| `LIBRARY_DIRNAME` | Folder for downloaded patches. |

> ⚠ When editing `SOCIALS`, keep the exact tuple format:  
> `("Name", "https://...", "#color"),`

---

## **Patch Format (Quick Primer)**

A cheat lives under a `PPU-<hash>:` block:

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

Multiple serials can be listed under `Games:` when the decrypted ELF is identical across regions.

---

## **Requirements**

- Python 3.8+  
- Tkinter  
- Internet only for GitHub patch downloads  
- PyInstaller (optional, for building `.exe`)

---

## **Credits & License**

- Cheats authored by **Host of Creators**  
- Porting, patch management, and tooling by **ChiDreams**

Patch collection:  
`https://github.com/chidreams/Artemis-Patch-Collection-RPCS3` [(github.com in Bing)](https://www.bing.com/search?q="https%3A%2F%2Fgithub.com%2Fchidreams%2FArtemis-Patch-Collection-RPCS3")

License: **MIT**
