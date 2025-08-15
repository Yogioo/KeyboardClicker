# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
python main.py
```
**Note**: 新版本为快速视觉识别工具，无需管理员权限。主要功能：
- 📦 显示边界框：一键截图并用红色边界框标记可点击元素
- 🏷️ 显示标签：一键截图并为每个元素显示字母标签
- 🔧 检查配置状态：查看检测算法配置和性能参数

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

### Testing Fast Recognition
```bash
python tests/test_fast_recognition.py
```

### Testing Multi-screen Support
```bash
python tests/test_multiscreen.py
```

### Running Fast Visual Recognition Demos
```bash
python examples/fast_visual_recognition_demo.py
python examples/unified_recognizer_demo.py
python examples/main_integration_example.py
```

### Performance Testing
```bash
python examples/performance_comparison.py
python examples/bbox_performance_comparison.py
```

## Project Structure

```
KeyboardClicker/
├── src/                          # 源代码目录
│   ├── core/                     # 核心功能模块（保留）
│   │   └── clicker.py           # 传统点击功能
│   ├── gui/                      # GUI界面模块  
│   │   ├── gui.py               # 传统Tkinter界面（保留）
│   │   └── debug_config_gui.py  # 配置调试界面
│   └── utils/                    # 核心工具模块
│       ├── fast_label_integrator.py      # 🆕 快速标签集成器（核心）
│       ├── unified_recognizer_adapter.py # 🆕 统一识别适配器
│       ├── optimized_bbox_overlay.py     # 🆕 优化边界框显示
│       ├── detection_config.py           # 🆕 检测配置管理
│       ├── screenshot.py                 # 截图功能
│       ├── screen_labeler.py             # 智能标签系统
│       ├── unified_recognizer/           # 🆕 统一识别引擎
│       │   ├── unified_visual_recognizer.py  # 视觉识别核心
│       │   ├── element_classifier.py         # 元素分类器
│       │   ├── feature_extractor.py          # 特征提取器
│       │   ├── image_pyramid.py              # 图像金字塔
│       │   ├── spatial_analyzer.py           # 空间分析器
│       │   └── recognition_config.py         # 识别配置
│       ├── fast_visual_recognizer.py     # 快速视觉识别器（已替换）
│       ├── bounding_box_overlay.py       # 传统边界框（保留）
│       └── recognition.py               # 传统OCR识别（保留）
├── tests/                        # 测试文件
│   ├── test_fast_recognition.py  # 🆕 快速识别测试
│   └── test_multiscreen.py      # 多屏幕功能测试
├── docs/                         # 文档
│   ├── unified_recognizer_usage.md       # 🆕 统一识别器使用文档
│   ├── main_integration_report.md       # 🆕 主集成报告
│   ├── bounding_box_overlay.md          # 边界框覆盖层文档
│   ├── screenshot_usage.md              # 截图功能使用说明
│   ├── 统一图像识别算法设计方案.md        # 算法设计方案
│   └── 多屏幕支持说明.md                # 多屏幕支持文档
├── examples/                     # 示例和演示
│   ├── fast_visual_recognition_demo.py  # 🆕 快速视觉识别演示
│   ├── unified_recognizer_demo.py       # 🆕 统一识别器演示
│   ├── main_integration_example.py      # 🆕 主集成示例
│   ├── performance_comparison.py        # 🆕 性能对比测试
│   ├── bbox_performance_comparison.py   # 🆕 边界框性能对比
│   └── [其他保留的示例文件...]
├── assets/                       # 资源文件
│   └── screenshots/             # 截图文件存储
├── main.py                       # 🆕 主程序（快速视觉识别工具）
├── requirements.txt              # 依赖包列表
├── README.md                     # 项目说明
├── CLAUDE.md                     # Claude Code指导文档
└── KeyboardClicker.code-workspace # VS Code工作区配置
```

## Code Architecture

### Core Components

**现代化架构**: 基于高性能视觉识别的模块化设计：

1. **FastLabelIntegrator** (`src/utils/fast_label_integrator.py`) - 核心快速识别引擎
   - 集成截图、识别、标签显示全流程  
   - 0-1秒内完成全屏元素识别
   - 详细性能监控和分析报告
   - 优化的识别参数配置管理

2. **UnifiedRecognizerAdapter** (`src/utils/unified_recognizer_adapter.py`) - 统一识别适配器
   - 基于计算机视觉的元素识别（无需OCR）
   - 支持按钮、图标、链接、输入框等多种元素类型
   - 并行处理、ROI优化、缓存机制
   - 可配置的置信度阈值和面积范围

3. **UnifiedVisualRecognizer** (`src/utils/unified_recognizer/`) - 统一视觉识别引擎
   - `unified_visual_recognizer.py` - 视觉识别核心
   - `element_classifier.py` - 元素分类器
   - `feature_extractor.py` - 特征提取器  
   - `spatial_analyzer.py` - 空间分析器
   - `image_pyramid.py` - 图像金字塔

4. **OptimizedBoundingBoxOverlay** (`src/utils/optimized_bbox_overlay.py`) - 优化边界框显示
   - 高性能边界框渲染引擎
   - 支持透明度、颜色、线宽自定义
   - 批量显示和隐藏操作
   - 多屏幕环境兼容

5. **DetectionConfig** (`src/utils/detection_config.py`) - 检测配置管理
   - 统一的检测参数配置中心
   - 各元素类型的面积、长宽比、置信度设置
   - 性能优化参数管理
   - 实时配置状态查看

### Application Controller

**KeyboardClickerApp** (`main.py`) - 快速视觉识别应用：
- 简化的GUI界面，专注于核心识别功能
- 实时状态反馈和性能统计
- 一键式操作流程
- 详细的配置状态查看功能

### Key Features

**极速性能**: 亚秒级视觉识别性能，包括：
- 并行处理架构，支持多线程元素检测
- ROI（感兴趣区域）优化算法
- 智能缓存机制减少重复计算
- 优化的图像金字塔和特征提取

**高精度识别**: 基于计算机视觉的智能识别：
- 无需OCR，直接识别UI元素的视觉特征
- 支持按钮、图标、链接、输入框等多种类型
- 可配置的置信度阈值和面积范围
- 智能去重和重叠区域合并

**Multi-screen Support**: 全面的多显示器环境支持：
- 自动检测虚拟屏幕边界
- 扩展显示器的负坐标处理
- 动态屏幕配置刷新
- 跨屏幕坐标验证

**性能监控**: 详细的性能分析和监控：
- 实时识别速度和精度统计
- 内存使用和处理吞吐量监控
- 分阶段性能分析（截图、识别、渲染）
- 可视化性能报告输出

## Dependencies

### Core Dependencies
- `pyautogui==0.9.54` - 屏幕截图和基础图像操作
- `pillow>=10.0.0` - 图像处理和格式转换
- `tkinter` - 内置GUI框架，用于用户界面

### 视觉识别依赖  
- `opencv-python==4.8.1.78` - 计算机视觉算法和图像处理
- `numpy==1.24.3` - 数值计算和图像数组操作
- `pytesseract==0.3.10` - OCR引擎（仅用于备用文本识别）

### 可选依赖
- `keyboard==0.13.5` - 全局键盘事件监听（用于扩展功能）

**Note**: 新版本主要使用计算机视觉算法，无需安装Tesseract OCR引擎。

## Code Style Guidelines

- Private variables use underscore prefix: `_variable_name`
- Public methods/classes/properties use PascalCase: `MethodName`
- Follow #region/#endregion for code organization where necessary
- Chinese comments and documentation are used throughout the codebase

## Platform Requirements

- Windows 10/11 (multi-screen detection optimized for Windows)
- Python 3.7 or higher
- **Note**: 新版本快速视觉识别工具无需管理员权限

## Testing Notes

### 快速识别测试
Use `tests/test_fast_recognition.py` to verify fast visual recognition functionality, performance benchmarks, and accuracy metrics.

### 多屏幕测试  
Use `tests/test_multiscreen.py` to verify multi-screen functionality is working correctly in your environment before making changes to screen detection logic.

### 性能测试
Use performance comparison scripts in `examples/` to benchmark recognition speed and rendering performance.

## Module Usage Guide

### FastLabelIntegrator Usage（推荐）
```python
from src.utils.fast_label_integrator import FastLabelIntegrator

# 创建快速识别集成器
integrator = FastLabelIntegrator()

# 一键分析：截图 + 识别 + 显示标签
success = integrator.analyze_and_label(
    max_labels=50,      # 最多显示50个标签
    show_boxes=True,    # 先显示边界框
    duration=None       # 永久显示
)

# 仅显示边界框
integrator.capture_and_recognize()
integrator.show_bounding_boxes(duration=3.0, box_color='red')

# 获取识别结果
detections = integrator.get_current_detections()
print(f"识别到 {len(detections)} 个可点击元素")

# 隐藏所有显示
integrator.hide_all()
```

### UnifiedRecognizerAdapter Usage（高级）
```python
from src.utils.unified_recognizer_adapter import UnifiedRecognizerAdapter

# 创建统一识别适配器
recognizer = UnifiedRecognizerAdapter()

# 配置性能参数
recognizer.configure_performance(
    use_parallel=True,
    max_workers=4,
    roi_optimization=True,
    cache_enabled=True
)

# 检测可点击元素
elements = recognizer.detect_clickable_elements(screenshot_path)
print(f"检测到 {len(elements)} 个元素")
```

### 检测配置管理
```python
from src.utils.detection_config import detection_config

# 查看启用的检测类型
enabled_types = detection_config.get_enabled_detection_types()
print(f"启用的检测类型: {enabled_types}")

# 获取元素参数
params = detection_config.get_element_params('button')
print(f"按钮检测参数: {params}")

# 打印完整配置
detection_config.print_config()
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