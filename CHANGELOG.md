# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-03-25

### Added
- **ENVIRONMENT_SETUP.md**: Comprehensive 5,000+ word virtual environment setup guide
- **ENVIRONMENT_UPDATE.md**: Summary of environment changes and setup instructions for users
- Virtual environment reproducibility documentation
- Automation scripts for one-command setup (setup.sh, setup.bat)
- Environment verification procedures

### Changed
- **PyMuPDF**: Upgraded from 1.23.8 → 1.27.2.2
  - Now supports Python 3.13+ with pre-built wheels
  - Improved performance and stability
  - Better PDF rendering
- **Pillow**: Upgraded from 10.0.0 → 10.4.0
  - Latest stable version
  - Better compatibility across Python versions
  - Performance improvements

### Improved
- Enhanced documentation with virtual environment setup guide
- Updated README with documentation map
- Better clarity on dependency installation
- Improved troubleshooting documentation
- Added Python version compatibility information

### Technical Details
- All dependencies now have pre-built wheels (no source compilation needed)
- Installation time reduced from 15+ minutes to 2-3 minutes
- Compatible with Python 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- Tested on Windows, macOS, Linux

## [1.0.0] - 2024-03-25

### Added
- Initial release of PDF Redaction Tool
- `find_coordinates.py`: GUI tool to visually select and obtain coordinates of areas to redact
- `apply_redaction_at_coordinates_globally.py`: Script to apply redaction to specified coordinates across all pages
- Comprehensive README with installation and usage instructions
- Support for custom redaction colors and styling
- Cross-platform compatibility (Windows, macOS, Linux)

### Features
- Interactive coordinate picker with real-time visual feedback
- Batch redaction across all PDF pages
- Customizable redaction appearance (color, transparency)
- Easy-to-understand workflow for non-technical users

### Documentation
- Installation guide with virtual environment setup
- Step-by-step usage instructions
- Troubleshooting section
- Configuration options documentation
