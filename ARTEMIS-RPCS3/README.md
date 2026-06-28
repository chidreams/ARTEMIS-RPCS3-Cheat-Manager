# ARTEMIS‑RPCS3 Cheat Manager

ARTEMIS‑RPCS3 is a patch and cheat management tool designed for RPCS3.  
It provides a streamlined workflow for creating, editing, organizing, and maintaining YAML‑based patch files used by the emulator.  
The application focuses on accuracy, stability, and a professional editing experience.

## Features

### Quick Add Code Helper
A memory‑editor style interface for adding new patch lines.  
Select a Data Type, enter an Address and Value, and generate a correctly formatted RPCS3 instruction.  
Supports byte, be16, be32, be64, bef32, alloc, jump_link, load, utf8, move_file, and more.

### Live Editor Mode
Cheats can be selected and edited directly in raw YAML form.  
Changes are saved instantly without reloading or rebuilding the file.

### Expanded Patch Type Support
The Quick Add menu includes the full suite of RPCS3 instruction types.  
If RPCS3 supports the instruction, ARTEMIS supports it.

### Smart Auto Focus
Selecting a cheat automatically switches the right panel to Details view.  
This keeps the workflow efficient and reduces unnecessary navigation.

### Automatic YAML Sanitization
The application removes empty PPU and SPU headers created during deletion or merging.  
This prevents RPCS3 errors such as “expected Map, found Null”.

### Clean Editing Environment
UI warnings and temporary markers are never written into YAML files.  
Patch data remains clean and accurate.

### Stable Backend
Python 3 indentation issues have been resolved.  
The PatchFile class now compiles and runs consistently across all environments.

## Purpose

ARTEMIS‑RPCS3 is built to support modders, cheat developers, and patch creators working with RPCS3.  
It provides a reliable environment for editing YAML patches, organizing cheat libraries, and maintaining clean, valid files.

## Usage

Load your existing patch file or create a new one.  
Use Quick Add to generate new instructions.  
Use Live Editor Mode to modify existing cheats.  
Save your changes and the application will automatically sanitize and validate the file.

## License

This project is provided for educational and modding purposes.  
Ensure compliance with RPCS3 guidelines and game ownership requirements.
