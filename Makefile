# Business Card Generator - Makefile
# Development and build automation

.PHONY: help install run test clean build-windows build-macos build-linux

# Default target
help:
	@echo "Business Card Generator - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install      - Install dependencies using uv"
	@echo "  make run          - Run the application"
	@echo "  make test         - Run all tests"
	@echo "  make clean        - Remove build artifacts"
	@echo ""
	@echo "Packaging:"
	@echo "  make build-windows - Build Windows executable"
	@echo "  make build-macos   - Build macOS application bundle"
	@echo "  make build-linux   - Build Linux AppImage"

# Install dependencies
install:
	uv sync

# Run the application
run:
	uv run python main.py

# Run tests
test:
	uv run pytest

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.spec
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .hypothesis/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Build Windows executable using PyInstaller
build-windows:
	uv run pyinstaller --name "BusinessCardGenerator" \
		--windowed \
		--onefile \
		--add-data "src:src" \
		main.py

# Build macOS application bundle using PyInstaller
build-macos:
	uv run pyinstaller --name "BusinessCardGenerator" \
		--windowed \
		--onefile \
		--add-data "src:src" \
		main.py

# Build Linux AppImage using PyInstaller
build-linux:
	uv run pyinstaller --name "BusinessCardGenerator" \
		--windowed \
		--onefile \
		--add-data "src:src" \
		main.py
