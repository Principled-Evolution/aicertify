# Repository Cleanup Plan

## Directories and Files to Keep

### Core Package
- `aicertify/__init__.py` - Package initialization
- `aicertify/api.py` - Core API module
- `aicertify/application.py` - Application management
- `aicertify/regulations.py` - Regulation set management

### Core Modules
- `aicertify/api/` - API implementation
- `aicertify/models/` - Data models
- `aicertify/opa_core/` - OPA integration
- `aicertify/opa_policies/` - OPA policies
- `aicertify/report_generation/` - Report generation
- `aicertify/utils/` - Utility functions

### Examples
- `examples/quickstart.py` - Main quickstart example
- `examples/README.md` - Examples documentation

### Package Files
- `setup.py` - Package setup
- `README.md` - Main documentation
- `.gitignore` - Git ignore file
- `LICENSE` - License file

## Directories and Files to Remove

### Development and Testing
- `aicertify/cli/` - CLI implementation
- `aicertify/decorators-phase-2/` - Experimental code
- `aicertify/development/` - Development scripts
- `aicertify/examples/` - Old examples directory
- `aicertify/tests/` - Test files
- `aicertify/system_evaluators/` - System evaluators
- `aicertify_cli.py` - CLI entry point
- `tests/` - Test files in root directory

### Documentation and Scripts
- `docs/` - Documentation and planning files
- `examples/` (current) - Old examples in root
- `scripts/` - Various scripts

### Temporary and Output Directories
- `debug_output/` - Debug output
- `memory-bank/` - Memory bank
- `temp_reports/` - Temporary reports
- `reports/` - Generated reports
- Any `__pycache__` directories

## Implementation Steps

1. Create new `examples` directory
2. Move `aicertify/examples/quickstart.py` to `examples/quickstart.py`
3. Create new README.md files
4. Remove unnecessary directories and files
5. Update imports if needed
6. Test the quickstart example to ensure it works

## Notes

- The OPA policies submodule should be preserved
- The core functionality needed for the quickstart example must be maintained
- All temporary and generated files should be removed
- Documentation should be simplified and focused on the quickstart example
