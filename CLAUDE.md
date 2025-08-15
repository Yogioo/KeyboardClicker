# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
1. 用中文回复用户
2. 代码中不要使用 Emoji

## Project Overview

KeyboardClicker is a Windows-based grid coordinate system that enables users to interact with their screen using keyboard-driven navigation. The project implements a recursive 3x3 grid system where users can quickly navigate to precise screen coordinates using the keyboard instead of a mouse.

### Core Concept
- **Grid Navigation**: Screen is divided into a 3x3 grid using keys `QWEASDZXC`
- **Recursive Targeting**: Each key press subdivides the selected area into another 3x3 grid
- **Command System**: Default action is left-click; suffixes like `R` (right-click) and `H` (hover) modify behavior
- **Visual Feedback**: Real-time transparent overlay shows grid divisions and current path

## Architecture

The project follows a modular 3-layer architecture:

```
src/
├── core/           # Core business logic (grid calculations, input processing, commands)
├── platform/       # Windows-specific operations (hotkeys, mouse control)
├── ui/             # PyQt6 visual overlay and user interface
└── main.py         # Application entry point and module integration
```

### Key Modules

#### Core Logic (`src/core/`)
- **GridCalculator**: Handles 3x3 grid mathematics and recursive subdivision
- **InputProcessor**: Processes keyboard input and command parsing (QWEASDZXC mapping)
- **CommandExecutor**: Executes actions (left-click, right-click with `R`, hover with `H`)
- **GridCoordinateSystem**: Main controller coordinating all core operations

#### Platform Layer (`src/platform/`)
- **HotkeyManager**: Global hotkey listening (Alt+G activation)
- **MouseController**: Low-level mouse operations using `pynput`

#### UI Layer (`src/ui/`)
- **GridOverlay**: PyQt6 transparent overlay showing grid lines and path indicator

## Development Commands

This is a Python project using PyQt6:

```bash
# Install dependencies
pip install -r requirements.txt
# Or install manually:
pip install PyQt6 pynput pytest pytest-cov

# Run the application
python src/main.py

# Development utilities
python -c "import sys; print(sys.path)"  # 检查Python路径
python -c "import PyQt6; print('PyQt6 installed')"  # 检查PyQt6安装

# Run tests using custom test runner
python tests/run_tests.py

# Run specific test suites
python tests/run_tests.py --core         # 仅运行核心模块测试
python tests/run_tests.py --all          # 运行所有测试
python tests/run_tests.py --verbose      # 详细输出

# Run specific test modules or classes
python tests/run_tests.py --test tests.core.test_grid_calculator
python tests/run_tests.py --test tests.core.test_input_processor.TestInputProcessor

# Generate test report
python tests/run_tests.py --report test_report.txt

# Alternative: Use pytest directly
python -m pytest tests/
python -m pytest tests/core/
python -m pytest tests/platform/
python -m pytest tests/ui/

# Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=html
python -m pytest tests/ --cov=src --cov-report=term-missing

# Code quality and formatting
python -m flake8 src/             # 代码风格检查
python -m black src/              # 代码格式化
python -m isort src/              # 导入排序

# Project structure analysis
find src/ -name "*.py" | wc -l    # 统计Python文件数量
find tests/ -name "*.py" | wc -l  # 统计测试文件数量

# Quick debugging
python -c "from src.core.grid_calculator import GridCalculator; print('Core module accessible')"
python -c "from src.platform.mouse_controller import MouseController; print('Platform module accessible')"

# Performance testing (when implemented)
python -m cProfile -o profile.out src/main.py
python -c "import pstats; pstats.Stats('profile.out').sort_stats('cumulative').print_stats(10)"
```

## Code Conventions

### Naming Conventions (from global CLAUDE.md)
- **Private variables**: `_abs` (underscore prefix)
- **Public/methods/classes/properties**: `Abc` (PascalCase)

### Code Organization
- Use `#region` and `#endregion` for organizing code sections
- Follow Python PEP8 standards
- All public methods should have docstring documentation

### Key Implementation Details

#### Grid System
- **Primary Layout**: 3x3 grid mapped to `QWEASDZXC` (Q=top-left, E=top-right, C=bottom-right, etc.)
- **Recursive Navigation**: Each key press subdivides the selected area into another 3x3 grid
- **Activation**: Global hotkey `Alt+G` activates the system
- **Exit**: `Esc` key or completion of action exits grid mode

#### Command System
- **Default**: Final key in path executes left-click
- **Right-click**: Append `R` to path (e.g., `EDCR`)
- **Hover**: Append `H` to path (e.g., `EDCH`) - moves cursor without clicking

#### Performance Requirements
- **Response Time**: < 50ms for key input processing
- **Precision**: 100% accuracy in coordinate calculations
- **Stability**: Must handle long-running operation without memory leaks

## Testing Strategy

### Test Structure
```
tests/
├── core/           # Unit tests for core business logic
├── platform/       # Tests for Windows-specific operations (using mocks)
└── ui/             # UI component tests (state-based, not pixel-based)
```

### Test Requirements
- **Coverage**: 100% for all core modules
- **Mock Strategy**: Platform-specific operations should be mocked to avoid system interference
- **Integration Tests**: Full workflow testing from activation to execution

## Technical Stack

- **Language**: Python
- **GUI Framework**: PyQt6 (for transparent overlays)
- **Input Handling**: `pynput` library for global hotkeys and mouse control
- **Target Platform**: Windows only
- **Testing**: pytest

## MVP Implementation Status

Current state appears to be early development with module structure defined but implementation pending. The project follows a well-planned modular approach with comprehensive documentation in the `docs/` folder.

### Development Priority
1. Core logic implementation (grid calculations, input processing)
2. Platform integration (hotkeys, mouse control)
3. UI overlay development
4. Testing and validation
5. Performance optimization

## Important Notes

- This is a **defensive tool** for productivity enhancement, not for automation or malicious purposes
- Focus on user experience: "zero-delay" interaction between positioning and execution
- Maintain clean separation between business logic, platform operations, and UI
- All coordinate calculations must be precise and deterministic