# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
python main.py
```
**Note**: Must be run with administrator privileges on Windows for global keyboard monitoring.

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Creating Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Testing Multi-screen Support
```bash
python tests/test_multiscreen.py
```

### Running Screenshot Demo
```bash
python examples/screenshot_demo.py
```

### Testing Bounding Box Overlay
```bash
python examples/test_bounding_box_overlay.py
python examples/improved_bbox_test.py
```

### Running OCR Integration Demo
```bash
python examples/ocr_label_integration_demo.py
```

## Project Structure

```
KeyboardClicker/
├── src/                          # 源代码目录
│   ├── core/                     # 核心功能模块
│   │   └── clicker.py           # 点击和键盘监听功能
│   ├── gui/                      # GUI界面模块  
│   │   └── gui.py               # Tkinter用户界面
│   └── utils/                    # 工具类模块
│       ├── screenshot.py        # 截图功能
│       ├── recognition.py       # OCR文字识别功能
│       ├── screen_labeler.py    # 屏幕标签显示功能
│       └── bounding_box_overlay.py  # 边界框覆盖层工具
├── tests/                        # 测试文件
│   └── test_multiscreen.py      # 多屏幕功能测试
├── docs/                         # 文档
│   ├── screenshot_usage.md      # 截图功能使用说明
│   └── 多屏幕支持说明.md         # 多屏幕支持文档
├── examples/                     # 示例和演示
│   ├── screenshot_demo.py       # 截图功能演示
│   ├── ocr_label_integration_demo.py  # OCR识别与标签集成演示
│   ├── test_bounding_box_overlay.py   # 边界框覆盖层测试
│   ├── improved_bbox_test.py    # 改进版边界框测试
│   ├── bbox_usage_example.py    # 边界框使用示例
│   └── usage_with_new_bbox_module.py  # 新模块迁移示例
├── assets/                       # 资源文件
│   └── screenshots/             # 截图文件存储
├── main.py                       # 主程序入口
├── requirements.txt              # 依赖包列表
├── README.md                     # 项目说明
├── CLAUDE.md                     # Claude Code指导文档
└── KeyboardClicker.code-workspace # VS Code工作区配置
```

## Code Architecture

### Core Components

**Modular Architecture**: The application follows a clean separation of concerns with core modules and utility tools:

1. **ClickerTool** (`src/core/clicker.py`) - Core functionality module
   - Handles mouse clicking operations
   - Global keyboard event monitoring (F1 key)
   - Multi-screen coordinate validation and positioning
   - Screen information detection and management

2. **ClickerGUI** (`src/gui/gui.py`) - User interface module  
   - Tkinter-based GUI with coordinate input and status display
   - Real-time mouse position tracking
   - Callback-based communication with core functionality
   - Multi-screen information display with refresh capability

### Utility Tools

3. **ScreenshotTool** (`src/utils/screenshot.py`) - Screenshot functionality
   - Full-screen and region-based screenshot capture
   - Automatic file naming with timestamps
   - Screenshot file management (list, delete, info)
   - PIL Image processing integration

4. **ScreenRecognizer** (`src/utils/recognition.py`) - OCR text recognition
   - Tesseract-based text detection and recognition
   - Configurable OCR parameters and confidence thresholds
   - Multiple recognition methods for enhanced accuracy
   - Support for various image preprocessing techniques

5. **ScreenLabeler** (`src/utils/screen_labeler.py`) - Screen label overlay
   - Generates unique labels for detected elements
   - Displays labels as overlay windows on screen
   - Supports customizable label styles and positioning
   - Automatic label generation algorithms (alphabetic, numeric)

6. **BoundingBoxOverlay** (`src/utils/bounding_box_overlay.py`) - Bounding box visualization
   - Displays transparent colored rectangles over detected areas
   - Configurable colors, line widths, and transparency
   - Support for timed auto-hide or permanent display
   - Easy integration with detection results from other modules

### Application Controller

**KeyboardClickerApp** (`main.py`) - Main application controller that:
- Manages inter-module communication through callback patterns
- Handles error propagation between modules
- Controls application lifecycle and cleanup

### Key Features

**Multi-screen Support**: Comprehensive multi-monitor environment support including:
- Virtual screen boundary detection using tkinter
- Negative coordinate handling for extended displays
- Dynamic screen configuration refresh for hot-plugged monitors
- Coordinate validation across all connected displays

**Defensive Programming**: All modules implement:
- Comprehensive error handling with user feedback
- Input validation for coordinates and file operations  
- Safe cleanup procedures and resource management

## Dependencies

### Core Dependencies
- `pyautogui==0.9.54` - Mouse automation and screen operations
- `keyboard==0.13.5` - Global keyboard event monitoring  
- `pillow==10.0.0` - Image processing for screenshots
- `tkinter` - Built-in GUI framework (no installation required)

### OCR and Recognition Dependencies  
- `pytesseract` - Python wrapper for Tesseract OCR engine
- `opencv-python` - Computer vision library for image processing
- `numpy` - Numerical computing for image array operations

**Note**: Tesseract OCR engine must be installed separately on the system.

## Code Style Guidelines

- Private variables use underscore prefix: `_variable_name`
- Public methods/classes/properties use PascalCase: `MethodName`
- Follow #region/#endregion for code organization where necessary
- Chinese comments and documentation are used throughout the codebase

## Platform Requirements

- Windows 10/11 (multi-screen detection optimized for Windows)
- Administrator privileges required for global keyboard monitoring
- Python 3.7 or higher

## Testing Notes

Use `tests/test_multiscreen.py` to verify multi-screen functionality is working correctly in your environment before making changes to screen detection logic.

## Module Usage Guide

### BoundingBoxOverlay Usage
```python
from src.utils.bounding_box_overlay import BoundingBoxOverlay

# Basic usage
bbox_overlay = BoundingBoxOverlay()

# Display detection results
detections = [{'bbox': (x, y, width, height), 'text': 'content'}]
bbox_overlay.ShowBoundingBoxes(detections, duration=3.0, box_color='red')

# Display custom bounding box
bbox_overlay.ShowCustomBoundingBox(100, 100, 200, 80, box_color='blue')

# Display from coordinate list
coords = [(x1, y1, w1, h1), (x2, y2, w2, h2)]
bbox_overlay.ShowBoundingBoxesFromCoords(coords, box_color='green')

# Hide all bounding boxes
bbox_overlay.HideBoundingBoxes()
```

### Integration with Other Modules
```python
# Example: Using BoundingBoxOverlay with OCR results
from src.utils.bounding_box_overlay import BoundingBoxOverlay
from src.utils.recognition import ScreenRecognizer

class MyModule:
    def __init__(self):
        self._bbox_overlay = BoundingBoxOverlay()
        self._recognizer = ScreenRecognizer()
    
    def analyze_and_highlight(self, image_path):
        # Recognize text
        results = self._recognizer.recognize_text(image_path)
        # Display bounding boxes
        self._bbox_overlay.ShowBoundingBoxes(results, duration=5.0)
```

所有测试代码存放在`tests`目录下
所有配置文件存放在`config`目录下
所有案例存放在`examples`目录下

## File Organization Guidelines

- **src/**: All source code organized by functionality
  - **core/**: Core business logic and main functionality
  - **gui/**: User interface components
  - **utils/**: Utility classes and helper functions
- **tests/**: All test files with `test_` prefix
- **docs/**: Documentation files (Markdown format)
- **examples/**: Demo scripts and usage examples
- **assets/**: Static resources like images, icons, screenshots
- **config/**: Configuration files (reserved for future use)
- **scripts/**: Build, deployment, or utility scripts (reserved for future use)