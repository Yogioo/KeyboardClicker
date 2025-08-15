# KeyboardClicker - 快速视觉识别工具

一个高性能的视觉识别桌面工具，专注于快速识别屏幕上的可点击元素，实现亚秒级性能的视觉分析。

## 功能特点

- ⚡ **极速识别**: 0-1秒内完成全屏元素识别和标签显示
- 🔍 **视觉算法**: 基于优化的计算机视觉算法，无需OCR，高精度识别
- 🎯 **智能检测**: 识别按钮、图标、链接、输入框等多种可点击元素
- 🏷️ **智能标签**: 自动生成标签覆盖层，便于快速定位元素
- 📦 **边界框显示**: 实时显示元素边界框，支持透明度和颜色自定义
- 🖥️ **多屏幕支持**: 完整支持多显示器环境，自动处理扩展屏幕和负坐标
- ⚙️ **高度优化**: 并行处理、ROI优化、缓存机制等多重性能优化
- 🎮 **简单易用**: 一键截图识别，直观的图形界面
- 📊 **性能监控**: 详细的性能分析和识别统计报告

## 系统要求

- Windows 10/11
- Python 3.7 或更高版本
- 管理员权限（用于全局键盘监听）

## 安装步骤

### 1. 克隆项目
```bash
git clone <repository-url>
cd KeyboardClicker
```

### 2. 创建虚拟环境（推荐）
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行程序
```bash
python main.py
```

**注意**: 首次运行时，Windows可能会提示需要管理员权限，请选择"是"以允许程序监听全局键盘事件。

## 使用方法

### 快速开始

1. **启动程序**
   ```bash
   python main.py
   ```

2. **选择识别模式**
   - **📦 显示边界框**: 一键截图并在所有可点击元素周围显示红色边界框
   - **🏷️ 显示标签**: 一键截图并为每个可点击元素显示字母标签

3. **识别流程**
   - 点击任一按钮后，程序会自动截图全屏
   - 使用优化的视觉算法快速识别可点击元素
   - 实时显示识别结果和性能统计

4. **结果查看**
   - **边界框模式**: 红色矩形框标记每个可点击区域
   - **标签模式**: A、B、C等字母标签标记每个元素位置
   - 状态栏显示识别到的元素数量和耗时

### 界面功能

- **📦 显示边界框**: 快速识别并用边界框标记可点击元素
- **🏷️ 显示标签**: 快速识别并用字母标签标记元素位置  
- **❌ 隐藏所有显示**: 清除屏幕上的所有边界框和标签
- **🔧 检查配置状态**: 查看当前检测算法配置和性能参数
- **状态显示**: 实时显示识别进度、结果统计和系统状态

## 常见问题

### Q: 识别速度慢或识别不到元素
A: 请检查：
- 程序是否正在使用优化的视觉算法（查看控制台输出）
- 点击"🔧 检查配置状态"查看是否启用了并行处理和缓存
- 确保屏幕内容清晰，避免过于复杂的背景

### Q: 标签显示位置不准确
A: 请确认：
- 屏幕缩放设置（建议使用100%缩放）
- 是否在多显示器环境下使用
- 重新运行识别以更新坐标

### Q: 程序性能优化建议
A: 推荐设置：
- 启用并行处理（4个工作线程）
- 启用ROI优化和缓存机制
- 根据需要选择特定元素类型进行识别

### Q: 如何查看详细的识别结果
A: 查看控制台输出中的性能分析报告，包含：
- 截图耗时、识别耗时、渲染耗时
- 识别到的元素数量和类型分布
- 识别精度和置信度统计

## 技术说明

### 架构设计

**现代化架构**: 基于高性能视觉识别引擎的模块化设计：

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

3. **OptimizedBoundingBoxOverlay** (`src/utils/optimized_bbox_overlay.py`) - 优化边界框显示
   - 高性能边界框渲染引擎
   - 支持透明度、颜色、线宽自定义
   - 批量显示和隐藏操作
   - 多屏幕环境兼容

4. **ScreenLabeler** (`src/utils/screen_labeler.py`) - 智能标签系统
   - 自动生成字母标签（A-Z, AA-ZZ等）
   - 精确定位标签覆盖层
   - 支持大量元素的标签显示
   - 自定义标签样式和持续时间

5. **DetectionConfig** (`src/utils/detection_config.py`) - 检测配置管理
   - 统一的检测参数配置中心
   - 各元素类型的面积、长宽比、置信度设置
   - 性能优化参数管理
   - 实时配置状态查看

**应用控制器**: **KeyboardClickerApp** (`main.py`) - 快速视觉识别应用
- 简化的GUI界面，专注于核心识别功能
- 实时状态反馈和性能统计
- 一键式操作流程
- 详细的配置状态查看功能

### 关键特性

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

**多屏幕支持**: 全面的多显示器环境支持：
- 自动检测虚拟屏幕边界
- 扩展显示器的负坐标处理
- 动态屏幕配置刷新
- 跨屏幕坐标验证

### 依赖库

#### 核心依赖
- **pyautogui**: 屏幕截图和基础图像操作
- **pillow**: 图像处理和格式转换
- **tkinter**: 内置GUI框架，用于用户界面

#### 视觉识别依赖  
- **opencv-python**: 计算机视觉算法和图像处理
- **numpy**: 数值计算和图像数组操作
- **pytesseract**: OCR引擎（仅用于备用文本识别）

#### 可选依赖
- **keyboard**: 全局键盘事件监听（用于扩展功能）

**注意**: 新版本主要使用计算机视觉算法，无需安装Tesseract OCR引擎。

### 项目结构
```
KeyboardClicker/
├── src/                          # 源代码目录
│   ├── core/                     # 核心功能模块（保留）
│   │   └── clicker.py           # 传统点击功能
│   ├── gui/                      # GUI界面模块  
│   │   └── gui.py               # 传统Tkinter界面（保留）
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
│       │   └── spatial_analyzer.py           # 空间分析器
│       └── recognition.py                # 传统OCR识别（保留）
├── tests/                        # 测试文件
│   ├── test_fast_recognition.py  # 🆕 快速识别测试
│   └── test_multiscreen.py      # 多屏幕功能测试
├── docs/                         # 文档
│   ├── unified_recognizer_usage.md       # 🆕 统一识别器使用文档
│   └── main_integration_report.md       # 🆕 主集成报告
├── examples/                     # 示例和演示
│   ├── fast_visual_recognition_demo.py  # 🆕 快速视觉识别演示
│   ├── unified_recognizer_demo.py       # 🆕 统一识别器演示
│   └── main_integration_example.py      # 🆕 主集成示例
├── assets/screenshots/           # 截图存储
├── main.py                       # 🆕 主程序（快速视觉识别工具）
├── requirements.txt              # 依赖包列表
├── README.md                     # 项目说明
└── CLAUDE.md                     # Claude Code指导文档
```

## 快速识别功能

项目的核心功能是基于计算机视觉的快速元素识别：

- ⚡ **亚秒级识别**: 0-1秒内完成全屏元素检测
- 🎯 **多元素类型**: 按钮、图标、链接、输入框、文本框
- 🏷️ **智能标签**: 自动为元素分配字母标签（A、B、C...）
- 📦 **边界框显示**: 彩色边界框标记可点击区域
- 📊 **性能监控**: 详细的识别和渲染性能分析

### 快速使用识别功能

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

# 获取识别结果
detections = integrator.get_current_detections()
print(f"识别到 {len(detections)} 个可点击元素")

# 隐藏所有显示
integrator.hide_all()
```

### 运行快速识别演示

```bash
python examples/fast_visual_recognition_demo.py
python examples/unified_recognizer_demo.py
```

详细使用说明请参考 [unified_recognizer_usage.md](docs/unified_recognizer_usage.md)

## 性能优化特性

项目采用多重优化策略确保高性能识别：

- ⚡ **并行处理**: 多线程并行检测不同区域的元素
- 🎯 **ROI优化**: 智能识别感兴趣区域，跳过空白区域
- 💾 **缓存机制**: 缓存重复计算结果，提升响应速度
- 🔄 **图像金字塔**: 多尺度分析，提高检测精度
- 🧠 **智能去重**: 自动合并重叠区域，消除冗余检测

### 性能配置示例

```python
from src.utils.fast_label_integrator import FastLabelIntegrator

integrator = FastLabelIntegrator()

# 配置性能参数
integrator.configure_recognition(
    performance={
        'use_parallel': True,     # 启用并行处理
        'max_workers': 4,         # 4个工作线程
        'roi_optimization': True, # 启用ROI优化
        'cache_enabled': True     # 启用缓存
    }
)
```

### 运行性能测试

```bash
python examples/performance_comparison.py
python examples/bbox_performance_comparison.py
```

### 查看详细性能报告

程序运行时会在控制台输出详细的性能分析：
- 截图耗时、识别耗时、渲染耗时
- 每个元素的平均检测时间
- 识别吞吐量和处理速度

## 测试

### 快速识别功能测试

项目提供了完整的测试脚本来验证识别功能的准确性和性能：

```bash
# 快速识别功能测试
python tests/test_fast_recognition.py

# 多屏幕环境测试
python tests/test_multiscreen.py
```

**测试内容包括**：
- **识别准确性**: 验证不同类型元素的识别精度
- **性能基准**: 测试识别速度和内存使用
- **多屏幕支持**: 验证扩展显示器环境下的功能
- **并发处理**: 测试并行识别的稳定性

**建议测试场景**：
1. **单屏幕环境** - 验证基本识别功能和性能
2. **双屏幕环境** - 测试跨屏幕识别和坐标处理
3. **复杂界面** - 测试大量元素的识别准确性
4. **性能压力** - 测试连续识别的稳定性

## 功能规划

### 已完成功能 ✅
- [x] ~~快速视觉识别引擎~~ ✅ 已完成
- [x] ~~统一识别适配器架构~~ ✅ 已完成  
- [x] ~~亚秒级性能优化~~ ✅ 已完成
- [x] ~~智能标签系统~~ ✅ 已完成
- [x] ~~优化边界框显示~~ ✅ 已完成
- [x] ~~并行处理和缓存~~ ✅ 已完成
- [x] ~~多屏幕支持~~ ✅ 已完成
- [x] ~~检测配置管理~~ ✅ 已完成

### 后续规划 🚀
- [ ] 机器学习模型集成（提升识别精度）
- [ ] 自定义元素类型训练
- [ ] 实时性能监控面板
- [ ] API接口和命令行工具
- [ ] 插件系统和扩展框架

## 许可证

本项目采用 MIT 许可证。详情请参考 LICENSE 文件。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 免责声明

本工具专为学习计算机视觉和界面自动化技术而设计。请仅用于合法的个人学习和开发用途。使用本工具进行任何自动化操作时，请确保遵守相关软件的使用条款和法律法规。使用本工具所产生的任何后果由用户自行承担。