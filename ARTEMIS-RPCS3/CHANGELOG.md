# ARTEMIS‑RPCS3 Cheat Manager
## Changelog

## Version 1.01 — The Precision Update

### Quick Add Code Helper
The manual text box has been replaced with a memory‑editor style interface.  
Users can select a Data Type, enter an Address and Value, and insert a fully formatted RPCS3 patch line.  
This eliminates spacing errors, YAML mistakes, and formatting issues.

### Expanded Patch Type Support
The Quick Add menu now supports the full suite of RPCS3 instruction types.  
byte, be16, be32, be64, bef32, alloc, jump_link, load, utf8, move_file, and additional supported modifiers.

### Live Editor Mode
The Details panel is now fully editable.  
Cheats can be selected, modified directly in raw YAML form, and saved instantly without reloading.

### Smart Auto Focus
Selecting a cheat automatically switches the right panel to Details view.  
This removes manual tab switching and improves workflow speed.

### Anti Crash YAML Sanitization
Fixed an issue where empty PPU or SPU headers remained after deleting or merging cheats.  
These caused RPCS3 to report “expected Map, found Null”.  
The application now removes orphaned headers automatically on save.

### Editor Visual Cleanup
Warning tags displayed in the interface are no longer saved into YAML files.  
Patch data remains clean and unaffected by UI messages.

### Structural Code Fixes
Resolved Python 3 indentation errors inside the PatchFile class.  
The backend now compiles and runs consistently across all supported environments.
