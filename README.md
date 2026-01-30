# Business Card Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://doc.qt.io/qtforpython/)

A desktop GUI application for creating, managing, and exporting professional business cards. Design templates with draggable fields, manage multiple cards via spreadsheet-like interface, and export to PDF or Word documents.

![Business Card Generator](https://img.shields.io/badge/status-active-success.svg)

## Features

- 🎨 **Visual Card Designer** - Drag-and-drop field positioning on card preview
- 📝 **Text & Image Fields** - Support for customizable text and image placeholders
- 🎯 **Template-Based Design** - Create reusable card layouts
- 📊 **Spreadsheet Data Entry** - Manage multiple cards in a table view
- 💾 **Project Persistence** - Save/load projects with JSON serialization
- 📥 **Excel Import** - Bulk import card data from Excel files
- 📤 **Multi-Format Export** - Export to PDF and Word (DOCX)
- ✂️ **Print-Ready Output** - Cut lines for easy printing and cutting
- 🔄 **Z-Order Control** - Bring to front/send to back layer management
- 📋 **Copy/Paste Fields** - Duplicate fields with automatic naming

## Screenshots

The application features a three-panel layout:
1. **Card Designer** (left) - Visual preview with draggable fields
2. **Data Table** (center) - Spreadsheet for card data entry
3. **Properties Panel** (right) - Field styling editor

## Installation

### Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Quick Start

```bash
# Clone the repository
git clone https://github.com/ultrasardine/business-card-generator.git
cd business-card-generator

# Install dependencies
uv sync

# Run the application
uv run python main.py
```

### Development Installation

```bash
# Clone and install with dev dependencies
git clone https://github.com/ultrasardine/business-card-generator.git
cd business-card-generator
uv sync --extra dev

# Run tests
uv run pytest
```

## Usage

### Creating a New Project

1. Launch the application: `uv run python main.py`
2. Go to **File → New Project** (Ctrl+N)
3. Enter a project name
4. Add fields using **+ Add Field** button (Text or Image)
5. Drag fields on the card preview to position them
6. Add cards using **+ Add Card** button
7. Fill in card data in the table

### Designing Cards

- **Add Fields**: Click "+ Add Field" and choose Text or Image type
- **Position Fields**: Drag fields on the card preview
- **Style Fields**: Select a field and use the Properties panel to adjust:
  - Font family, size, color
  - Bold/italic styling
  - Position and dimensions
- **Layer Order**: Right-click a field for z-order options (Bring to Front, Send to Back, etc.)
- **Copy/Paste**: Right-click to copy fields, paste creates duplicates with `_1`, `_2` suffixes

### Managing Card Data

- **Add Cards**: Click "+ Add Card" to create new rows
- **Edit Data**: Double-click cells to edit text values
- **Image Fields**: Click image cells to select image files
- **Remove Cards**: Select a row and click "- Remove Card"

### Importing from Excel

1. Go to **File → Import from Excel** (Ctrl+I)
2. Select an Excel file (.xlsx or .xls)
3. The first row becomes field names
4. Image columns are auto-detected by file extensions or header keywords

### Exporting Cards

1. Go to **File → Export** (Ctrl+E)
2. Choose format: PDF or Word (DOCX)
3. Select cards per page (1, 2, 4, 6, 8, or 10)
4. Choose save location
5. Exports include cut lines for easy printing

## Project Structure

```
business-card-generator/
├── main.py                          # Application entry point
├── pyproject.toml                   # Project config and dependencies
├── src/
│   └── business_card_generator/
│       ├── models/
│       │   └── card.py              # Data models (FieldDefinition, CardTemplate, CardRow)
│       ├── core/
│       │   ├── card_data_model.py   # Qt table model (QAbstractTableModel)
│       │   └── export_engine.py     # PDF/DOCX export logic
│       └── ui/
│           ├── main_window.py       # Main window with menu and 3-panel layout
│           ├── card_designer.py     # Visual card preview with draggable fields
│           ├── card_table_view.py   # Spreadsheet-like data table
│           └── details_bar.py       # Field property editor panel
└── tests/                           # Test suite
```

## Architecture

### Data Models

- **FieldDefinition**: Defines a field's properties (name, type, position, styling, z-index)
- **CardTemplate**: Collection of field definitions with background color
- **CardRow**: Individual card data (field ID → value mapping)

### Key Components

| Component | Purpose |
|-----------|---------|
| `CardDataModel` | Qt table model bridging data and UI |
| `CardDesigner` | Visual card preview with draggable widgets |
| `CardTableWidget` | Spreadsheet interface for data entry |
| `DetailsBar` | Property editor for selected fields |
| `ExportEngine` | PDF and DOCX generation |

### Data Flow

```
User Input → CardDataModel → Signals → UI Components
                ↓
         JSON Persistence
                ↓
         Project Files (~/.business-card-generator/<project>/)
```

## Configuration

### Card Dimensions

Standard business card size: **3.5" × 2"** (336 × 192 pixels at 96 DPI)

### Project Storage

Projects are stored in `~/.business-card-generator/<project-name>/`:
- `project.json` - Template and card data
- `images/` - Copied image files

### Supported Formats

| Format | Import | Export |
|--------|--------|--------|
| Excel (.xlsx, .xls) | ✅ | ❌ |
| PDF | ❌ | ✅ |
| Word (.docx) | ❌ | ✅ |
| JSON (project) | ✅ | ✅ |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Project |
| Ctrl+O | Open Project |
| Ctrl+S | Save Project |
| Ctrl+I | Import from Excel |
| Ctrl+E | Export |
| Ctrl+Q | Exit |

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.13+ |
| GUI Framework | PySide6 (Qt for Python) |
| PDF Generation | ReportLab |
| Word Export | python-docx |
| Excel Import | openpyxl |
| Testing | pytest, hypothesis, pytest-qt |
| Package Manager | uv |

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=src
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Write docstrings for public APIs
- Use Qt signals/slots for component communication

### Adding Dependencies

```bash
# Add runtime dependency
uv add <package-name>

# Add dev dependency
uv add --dev <package-name>
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Commit with clear messages
5. Push and open a Pull Request

## Security

See [SECURITY.md](SECURITY.md) for security considerations and vulnerability reporting.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 🐛 [Report a bug](https://github.com/ultrasardine/business-card-generator/issues)
- 💡 [Request a feature](https://github.com/ultrasardine/business-card-generator/issues)
- 📖 [Documentation](https://github.com/ultrasardine/business-card-generator)

## Acknowledgments

Built with:
- [PySide6](https://doc.qt.io/qtforpython/) - Qt for Python
- [ReportLab](https://www.reportlab.com/) - PDF generation
- [python-docx](https://python-docx.readthedocs.io/) - Word document creation
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel file handling
