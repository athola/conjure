# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-23

### Added
- **UV Package Manager**: Complete migration to UV for modern Python dependency management
- **Build System**: Comprehensive Makefile with standardized development workflow
- **License**: MIT license added for proper open-source licensing
- **Development Tools**: Full suite of code quality tools (ruff, mypy, bandit, typos, etc.)
- **CI/CD Ready**: Pre-commit hooks and comprehensive validation pipeline
- **Type Safety**: Modern type hints and mypy configuration across all Python tools

### Changed
- **Modernized Python**: Updated to modern Python 3.10+ syntax and type annotations
- **Tool Architecture**: Refactored quota tracker and usage logger with proper CLI interfaces
- **Build Configuration**: Complete project structure modernization with pyproject.toml
- **Development Experience**: Improved developer workflow with standardized commands

### Fixed
- **Dependency Management**: Resolved dependency installation and management issues
- **Code Quality**: Addressed linting and formatting inconsistencies
- **Type Safety**: Fixed type annotation issues across the codebase

### Technical Details
- Added `uv.lock` for reproducible dependency management
- Implemented comprehensive ruff configuration with security and quality rules
- Added mypy strict type checking with proper configuration
- Created pre-commit hooks setup for automated quality checks
- Added Makefile targets for all common development operations

## [1.0.0] - 2025-11-14

### Added
- **Core Framework**: Initial release of the intelligent delegation framework
- **Delegation Core**: Framework for assessing task delegation suitability
- **Gemini Integration**: Gemini CLI delegation with quota tracking
- **Qwen Integration**: Qwen MCP delegation capabilities
- **Plugin System**: Complete Claude Code plugin integration
- **Tools**: Quota tracking and usage logging utilities