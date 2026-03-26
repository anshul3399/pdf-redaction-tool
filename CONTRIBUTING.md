# Contributing to PDF Redaction Tool

Thank you for your interest in contributing to the PDF Redaction Tool! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with the following information:
- A clear, descriptive title
- A detailed description of the bug
- Steps to reproduce the issue
- Your environment (Python version, OS, installed packages)
- Any error messages or screenshots

### Suggesting Enhancements

We welcome feature suggestions! Please open an issue with:
- A clear title describing the enhancement
- A detailed description of the proposed functionality
- Use cases and examples
- Any relevant screenshots or mockups

### Code Contributions

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/pdf-redaction-tool.git
   cd pdf-redaction-tool
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
6. **Make your changes** and test thoroughly
7. **Commit with clear messages**:
   ```bash
   git commit -m "Description of changes"
   ```
8. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
9. **Open a Pull Request** on the main repository with:
   - A clear description of changes
   - Reference to any related issues
   - Any testing instructions

## Code Style

- Follow PEP 8 conventions
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and concise

## Testing

Please test your changes thoroughly before submitting a PR:
- Test with various PDF files
- Test with different coordinate values
- Verify output files are correctly redacted

## Reporting Security Issues

Please email security concerns privately rather than using the issue tracker.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing!
