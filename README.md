# Luganda Hunspell Dictionary

**⚠️ Status: This Hunspell dictionary is still under active development and subject to frequent changes. Use at your own discretion.**

A comprehensive Hunspell dictionary for the Luganda language (spoken in Uganda) with tools for dictionary generation, validation, and integration into spell-checking systems.

## 📋 Table of Contents

- [Overview](#overview)
- [Project Status](#project-status)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Dictionary Files](#dictionary-files)
- [Tools & Utilities](#tools--utilities)
- [Building & Development](#building--development)
- [Integration](#integration)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project provides a Hunspell-compatible dictionary for the Luganda language, along with a suite of tools for managing, generating, and validating morphological rules and word lists. Luganda is an agglutinative language with complex prefix and suffix systems, requiring sophisticated affix rules for accurate spell-checking.

The project includes:
- **Dictionary Files** (`Luganda.aff` and `Luganda.dic`) - Core Hunspell dictionary
- **Tools** - Python and Java utilities for dictionary generation and validation
- **Generator App** - JavaFX application for visualizing and generating prefixed word forms
- **Scripts** - Automation scripts for dictionary processing and cleaning

## Project Status

### ⚠️ Development Status

**This dictionary is still under active development.** The following should be noted:

- Morphological rules are continuously being refined and tested
- Word list coverage is expanding
- Integration with spell-checking systems (like LanguageTool) may have limitations
- Breaking changes may occur without deprecation warnings
- Community contributions and feedback are welcome

**Expected Changes:**
- Expansion of prefix/suffix rule coverage
- Refinement of existing morphological rules
- Validation and expansion of base word list
- Performance optimizations

## Features

- ✅ Comprehensive Luganda morphological rules (prefixes, suffixes, combinations)
- ✅ Base word dictionary with thousands of Luganda terms
- ✅ Tools for generating cross-product word forms
- ✅ GUI application for visualizing affix combinations
- ✅ Python utilities for dictionary validation and cleaning
- ✅ Integration-ready format for spell-checking frameworks
- ✅ Open-source (GPL v3) and community-driven

## Project Structure

```
.
├── Luganda.aff                    # Hunspell affix file (morphological rules)
├── Luganda.dic                    # Hunspell dictionary file (word list)
├── README.md                      # This file
├── README-LugandaGenerator.md      # Documentation for the Generator app
├── LICENSE                        # GPL v3 license
│
├── lugandahunspelldictionary/     # Maven Java project
│   ├── pom.xml                    # Maven configuration
│   ├── src/main/                  # Java source code (future expansion)
│   └── target/                    # Build artifacts
│
├── resources/                     # Reference and supporting files
│   ├── en_US.*                    # English reference dictionary
│   ├── lg.aff, lg.dic             # Alternative Luganda dictionary format
│   ├── lg.txt                     # Luganda text samples
│   ├── Luganda_Dictionary.txt      # Full word list
│   └── Raw_Luganda.dic            # Unprocessed word list
│
├── scripts/                       # Automation and processing scripts
│   ├── clean_dict.py              # Python script for dictionary cleaning
│   ├── clean_dict.ps1             # PowerShell script for dictionary cleaning
│   └── ...
│
└── tools/                         # Utility programs
    ├── LugandaDictionaryUpdaterGUI.java    # GUI for dictionary updates
    ├── PrefixSimulator.java                # Prefix rule simulator
    ├── check_hunspell_counts.py            # Validate dictionary statistics
    ├── check_word.py                       # Word validation utility
    ├── update_aff_*.py                     # Affix rule generators (30+ scripts)
    ├── gen_cross_product_script.py         # Cross-product generator
    └── ... (additional utilities)
```

## Getting Started

### Prerequisites

- **Python 3.7+** (for scripts)
- **Java 11+** (for GUI application)
- **Maven 3.6+** (for building)
- **Hunspell** (for testing dictionaries locally, optional)

### Basic Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ukashakabandayawe/Luganda-Hunspell-Dictionary.git
   cd Luganda-Hunspell-Dictionary
   ```

2. **View the dictionary files:**
   - `Luganda.aff` - Contains morphological rules and character mappings
   - `Luganda.dic` - Contains the base word list

3. **Test with Hunspell (if installed):**
   ```bash
   hunspell -d Luganda test_file.txt
   ```

## Dictionary Files

### Luganda.aff (Affix File)

Contains the morphological rules for Luganda, including:
- **SET**: Character encoding declaration
- **FLAG**: Flag type specification
- **PFX Rules**: Prefix (class) rules with conditions
- **SFX Rules**: Suffix rules (if implemented)
- **ALIAS**: Word class definitions

Example structure:
```
SET UTF-8
FLAG long

PFX A Y 1
PFX A 0 a .

PFX B Y 2
PFX B 0 ba .
PFX B 0 ba/C .
```

### Luganda.dic (Dictionary File)

Contains the base word list with flags for morphological processing:
- First line: word count
- Subsequent lines: words with optional flags
- Format: `word/FLAGS`

Example:
```
1000
kola/A
musyi/B
...
```

## Tools & Utilities

### Luganda Dictionary Generator (JavaFX App)

A GUI application for visualizing and generating prefixed word forms.

**Features:**
- Load custom `.aff` files
- Input root words interactively
- Generate all possible prefixed forms based on PFX rules
- Display results in a table
- Export results to CSV

**Documentation:** See [README-LugandaGenerator.md](README-LugandaGenerator.md)

### Python Utilities

#### Dictionary Cleaning Scripts
- `clean_dict.py` - Clean and validate dictionary files
- `check_word.py` - Look up individual words and their rules
- `check_hunspell_counts.py` - Validate word counts in dictionary

#### Affix Update Generators
The `tools/` directory contains 30+ scripts (`update_aff_*.py`) that generate specific cross-product rules:
- Examples: `update_aff_BD.py`, `update_aff_BH.py`, `update_aff_cross_products.py`
- These scripts generate complex morphological combinations
- Each script handles specific prefix/suffix interactions

#### Specialized Tools
- `gen_cross_product_script.py` - Generate cross-product rule scripts
- `PrefixSimulator.java` - Simulate prefix application in Java
- `cross_product_common.py` - Common cross-product utilities

## Building & Development

### Build the Maven Project

```bash
cd lugandahunspelldictionary
mvn clean compile
```

### Run the Generator Application

```bash
cd lugandahunspelldictionary
mvn javafx:run
```

### Run Python Scripts

Ensure Python is in your PATH, then:

```bash
cd tools
python check_word.py
python clean_dict.py
python check_hunspell_counts.py
```

### PowerShell Automation

Windows users can use provided PowerShell scripts:

```powershell
.\scripts\clean_dict.ps1
```

## Integration

### Integration with LanguageTool

This dictionary can be integrated with LanguageTool for spell-checking:

```powershell
# Copy dictionary files to LanguageTool hunspell directory
Copy-Item -Force `
  -Path Luganda.aff, Luganda.dic `
  -Destination "E:\languagetool\languagetool-language-modules\lg\src\main\resources\org\languagetool\resource\lg\hunspell"
```

A pre-configured task is available:
```bash
# Run the copy task
mvn -f lugandahunspelldictionary/pom.xml "process: Copy Luganda.aff/Luganda.dic to LanguageTool hunspell"
```

### Integration with Other Spell Checkers

The `Luganda.aff` and `Luganda.dic` files follow the Hunspell format and can be integrated with any Hunspell-compatible spell-checker:
- Firefox/Thunderbird
- LibreOffice/OpenOffice
- VS Code spell-check extensions
- Custom Hunspell implementations

## Contributing

Contributions are welcome! Areas where help is needed:

1. **Morphological Rules** - Expand and refine affix rules
2. **Word List** - Add missing Luganda words
3. **Testing** - Validate rules against corpus data
4. **Tools** - Improve or create new utilities
5. **Documentation** - Improve and translate documentation

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test thoroughly
5. Submit a pull request with a description of changes

### Reporting Issues

Please report bugs and suggest improvements via GitHub Issues. Include:
- Description of the issue
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (OS, tool versions, etc.)

## License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

The Luganda Hunspell Dictionary is free software: you can redistribute it and/or modify it under the terms of the GPL v3 as published by the Free Software Foundation.

## Citation

If you use this dictionary in academic or professional work, please cite:

```
Luganda Hunspell Dictionary
https://github.com/ukashakabandayawe/Luganda-Hunspell-Dictionary
```

## Support

For questions or support:
- **GitHub Issues**: [Report issues here](https://github.com/ukashakabandayawe/Luganda-Hunspell-Dictionary/issues)
- **Discussions**: [Join the discussion](https://github.com/ukashakabandayawe/Luganda-Hunspell-Dictionary/discussions)

## Acknowledgments

- Luganda linguistic community for feedback and contributions
- Hunspell project for the spell-checking framework
- LanguageTool community for integration support

---

**Last Updated:** January 2026  
**Status:** 🔄 Active Development  
**Language:** Luganda (lg)  
**Format:** Hunspell
