# Contributing to ARTEMIS‑RPCS3 Cheat Manager

Thank you for your interest in contributing to ARTEMIS‑RPCS3.  
This project is designed to provide a stable, accurate, and professional environment for creating and editing RPCS3 patch files.  
Contributions are welcome in the form of code improvements, documentation updates, feature suggestions, and bug reports.

## Code Style and Structure

All code should follow consistent formatting and readability standards.  
Python files should use clear naming, organized functions, and predictable structure.  
Indentation must follow strict Python 3 rules to avoid compilation issues.  
Avoid unnecessary complexity, keep functions focused, and ensure changes do not break existing behavior.

## Patch File Handling

When modifying patch‑related logic, ensure that YAML output remains valid for RPCS3.  
Empty PPU and SPU headers should never be produced.  
All generated instructions must follow RPCS3 formatting rules.  
Supported instruction types include byte, be16, be32, be64, bef32, alloc, jump_link, load, utf8, move_file, and additional RPCS3 modifiers.

## Feature Additions

New features should improve workflow, stability, or clarity.  
Examples include editor enhancements, validation tools, or additional patch type support.  
All new features must be tested with real RPCS3 patch files to confirm correct behavior.

## Reporting Issues

If you encounter a problem, provide the following information:  
Application version, operating system, steps to reproduce the issue, expected behavior, actual behavior, and any relevant patch data.  
Clear reports help maintain stability and prevent regressions.

## Submitting Changes

Fork the repository, create a branch for your changes, commit with clear messages, and submit a pull request.  
Describe the purpose of the change, the affected areas, and any testing performed.  
All submissions will be reviewed for accuracy, stability, and compatibility.

## Documentation

Documentation updates are encouraged.  
If you add a feature, update the README or create a new section explaining how it works.  
Clear documentation ensures users understand how to use the tool effectively.

## Community Guidelines

Be respectful, constructive, and focused on improving the project.  
Suggestions and feedback should be clear and actionable.  
The goal is to maintain a reliable and professional tool for RPCS3 modders and cheat developers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License included in this repository.
