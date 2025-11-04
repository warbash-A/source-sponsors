# Contributing to Source Sponsors

Thank you for your interest in contributing to Source Sponsors!

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version)

### Suggesting Features

We welcome feature suggestions! Please open an issue with:
- Clear description of the feature
- Use case and benefits
- Any implementation ideas

### Code Contributions

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/source-sponsors.git
cd source-sponsors

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run tests (when available)
python -m pytest
```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and modular

## Areas for Contribution

- **Event Discovery**: Add more event sources beyond Eventbrite
- **Sponsor Extraction**: Improve scraping algorithms and patterns
- **Contact Finding**: Better email discovery methods
- **Email Templates**: More template variations
- **Testing**: Unit tests and integration tests
- **Documentation**: Improve docs and examples
- **Integrations**: CRM systems, email platforms

## Questions?

Feel free to open an issue for any questions about contributing.
