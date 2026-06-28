# ARTEMIS‑RPCS3 Cheat Manager
## Frequently Asked Questions

## What is ARTEMIS‑RPCS3 Cheat Manager
ARTEMIS‑RPCS3 is a tool designed to create, edit, organize, and maintain RPCS3 patch files.  
It provides a professional editing environment for YAML‑based cheats and modding instructions used by the RPCS3 emulator.

## Why does RPCS3 show “expected Map, found Null”
This error appears when a patch file contains empty PPU or SPU headers.  
These headers can be created when deleting cheats or merging files manually.  
ARTEMIS automatically removes orphaned headers when saving, preventing this issue.

## Why are my patch lines formatted differently
ARTEMIS formats patch lines according to RPCS3 standards.  
Spacing, structure, and instruction layout follow the emulator’s expected format.  
This ensures compatibility and prevents YAML parsing errors.

## Why does Quick Add auto‑format my input
Quick Add is designed to eliminate formatting mistakes.  
Selecting a Data Type and entering an Address and Value ensures the output is valid for RPCS3.  
This prevents common issues such as incorrect spacing, invalid instruction types, or malformed YAML.

## Why can I edit cheats directly in the Details panel
Live Editor Mode allows direct editing of raw YAML.  
This provides full control over patch lines and makes the tool suitable for advanced modders and cheat developers.

## Why does the editor switch to Details automatically
Smart Auto Focus improves workflow by switching to the Details view when a cheat is selected.  
This removes unnecessary navigation and keeps editing efficient.

## Why are warning messages not saved into my YAML file
UI warnings are visual indicators only.  
They are intentionally separated from the actual patch data to keep YAML files clean and valid.

## Why does the application sanitize my file on save
Sanitization prevents invalid YAML structures, empty headers, and formatting issues.  
This ensures RPCS3 can load the patch file without errors.

## Where can I get help or report issues
All support, questions, and troubleshooting are handled through the official Discord community.  
Join the Discord server to receive assistance, report bugs, request features, or share patch files.

## Discord Support
For help, visit the official ARTEMIS‑RPCS3 Discord community. in the about of the program 
This is the primary location for support, updates, testing, and communication.
