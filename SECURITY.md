# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it by creating a private security advisory on GitHub or by opening an issue.

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond as quickly as possible and work with you to address the issue.

## Security Considerations

Business Card Generator is a desktop application that:

- Reads and writes files to the user's home directory (`~/.business-card-generator/`)
- Imports Excel files from user-selected locations
- Exports PDF and Word documents to user-selected locations
- Copies image files to project directories

### File System Access

- The application only accesses files explicitly selected by the user
- Project data is stored in a dedicated directory under the user's home folder
- No network access is required for core functionality

### Data Handling

- Card data is stored locally in JSON format
- No data is transmitted over the network
- Image files are copied to project folders (not referenced externally)

### Third-Party Dependencies

The application uses well-established libraries:
- PySide6 (Qt for Python) - GUI framework
- ReportLab - PDF generation
- python-docx - Word document creation
- openpyxl - Excel file reading

Keep dependencies updated to receive security patches.
