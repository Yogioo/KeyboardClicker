# KeyboardClicker - 键盘触发屏幕点击工具

一个简单实用的桌面工具，通过键盘快捷键触发鼠标点击屏幕上的指定位置。

## 功能特点

- 🎯 **精确定位**: 支持像素级精确的屏幕坐标设置
- ⌨️ **快捷键触发**: 使用F1键快速触发点击操作
- 🖱️ **实时坐标**: 实时显示当前鼠标位置，方便定位
- 🎮 **简单易用**: 直观的图形界面，操作简单
- 🔄 **状态反馈**: 清晰的状态提示，了解程序运行状态
- 📸 **截图功能**: 支持全屏和区域截图，便于后续开发和调试
- 🖥️ **多屏幕支持**: 完整支持多显示器环境，自动处理扩展屏幕和负坐标
- 🔍 **OCR识别**: 基于Tesseract的文字识别功能，支持多种识别模式
- 🏷️ **智能标签**: 为识别结果自动生成唯一标签，支持屏幕覆盖显示
- 📦 **边界框工具**: 独立的边界框覆盖层模块，可视化检测结果和目标区域

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

### 基本操作流程

1. **启动程序**
   - 以管理员身份运行命令提示符或PowerShell
   - 执行 `python main.py` 启动程序

2. **设置目标位置**
   - 移动鼠标到你想要点击的屏幕位置
   - 点击"获取当前位置"按钮，程序会自动填入当前鼠标坐标
   - 或者手动在X、Y坐标框中输入目标坐标

3. **开始监听**
   - 点击"开始监听"按钮
   - 程序状态会显示为"监听中"

4. **触发点击**
   - 按下F1键，程序会在设定的坐标位置执行鼠标左键点击
   - 可以重复按F1键进行多次点击

5. **停止监听**
   - 点击"停止监听"按钮结束键盘监听

### 界面说明

- **当前鼠标位置**: 实时显示鼠标的X、Y坐标
- **目标位置设置**: 设置要点击的屏幕坐标
- **获取当前位置**: 一键获取当前鼠标位置并填入目标坐标
- **开始/停止监听**: 控制F1键监听的开启和关闭
- **状态显示**: 显示程序当前状态（待机/监听中/点击中）

## 常见问题

### Q: 程序无法启动或提示权限错误
A: 请确保以管理员身份运行程序。右键点击命令提示符，选择"以管理员身份运行"。

### Q: 按F1键没有反应
A: 请检查：
- 程序是否显示"监听中"状态
- 是否以管理员权限运行
- 目标坐标是否设置正确

### Q: 点击位置不准确
A: 请确认：
- 屏幕缩放设置（建议使用100%缩放）
- 目标坐标是否正确
- 是否在多显示器环境下使用

### Q: 如何退出程序
A: 点击"停止监听"按钮，然后关闭程序窗口即可。

## 技术说明

### 架构设计

**模块化架构**: 应用采用清晰的关注点分离，包含三个主要模块：

1. **ClickerTool** (`src/core/clicker.py`) - 核心功能模块
   - 处理鼠标点击操作
   - 全局键盘事件监听（F1键）
   - 多屏幕坐标验证和定位
   - 屏幕信息检测和管理

2. **ClickerGUI** (`src/gui/gui.py`) - 用户界面模块  
   - 基于Tkinter的GUI界面，支持坐标输入和状态显示
   - 实时鼠标位置追踪
   - 基于回调的核心功能通信
   - 多屏幕信息显示和刷新功能

3. **ScreenshotTool** (`src/utils/screenshot.py`) - 截图功能
   - 全屏和区域截图捕获
   - 带时间戳的自动文件命名
   - 截图文件管理（列表、删除、信息获取）
   - PIL图像处理集成

4. **ScreenRecognizer** (`src/utils/recognition.py`) - OCR文字识别
   - 基于Tesseract的文字检测和识别
   - 可配置的OCR参数和置信度阈值
   - 多种识别方法提升准确性
   - 支持各种图像预处理技术

5. **ScreenLabeler** (`src/utils/screen_labeler.py`) - 屏幕标签覆盖
   - 为检测元素生成唯一标签
   - 屏幕覆盖层标签显示
   - 支持自定义标签样式和位置
   - 自动标签生成算法（字母、数字）

6. **BoundingBoxOverlay** (`src/utils/bounding_box_overlay.py`) - 边界框可视化
   - 在检测区域上显示透明彩色矩形
   - 可配置颜色、线宽和透明度
   - 支持定时自动隐藏或永久显示
   - 易于与其他模块的检测结果集成

**应用控制器**: **KeyboardClickerApp** (`main.py`) - 主应用控制器
- 通过回调模式管理模块间通信
- 处理模块间错误传播
- 控制应用生命周期和清理

### 关键特性

**多屏幕支持**: 全面的多显示器环境支持，包括：
- 使用tkinter进行虚拟屏幕边界检测
- 扩展显示器的负坐标处理
- 热插拔显示器的动态屏幕配置刷新
- 所有连接显示器的坐标验证

**防御性编程**: 所有模块实现：
- 全面的错误处理和用户反馈
- 坐标和文件操作的输入验证  
- 安全的清理程序和资源管理

### 依赖库

#### 核心依赖
- **pyautogui**: 用于鼠标点击、屏幕坐标操作和截图功能
- **keyboard**: 用于全局键盘事件监听
- **tkinter**: Python内置GUI库，用于创建用户界面
- **pillow**: 图像处理库，用于截图功能和图片处理

#### OCR和识别依赖
- **pytesseract**: Tesseract OCR引擎的Python包装器
- **opencv-python**: 计算机视觉库，用于图像处理
- **numpy**: 数值计算库，用于图像数组操作

**注意**: 需要单独安装Tesseract OCR引擎。

### 文件结构
```
KeyboardClicker/
├── src/                          # 源代码目录
│   ├── core/                     # 核心功能模块
│   │   └── clicker.py           # 点击和键盘监听功能
│   ├── gui/                      # GUI界面模块  
│   │   └── gui.py               # Tkinter用户界面
│   └── utils/                    # 工具类模块
│       ├── screenshot.py        # 截图功能
│       ├── recognition.py       # OCR文字识别
│       ├── screen_labeler.py    # 屏幕标签显示
│       └── bounding_box_overlay.py  # 边界框覆盖层
├── tests/                        # 测试文件
│   └── test_multiscreen.py      # 多屏幕功能测试
├── docs/                         # 文档
│   ├── screenshot_usage.md      # 截图功能使用说明
│   ├── bounding_box_overlay.md  # 边界框覆盖层文档
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
├── config/                       # 配置文件（预留）
├── scripts/                      # 构建和部署脚本（预留）
├── main.py                       # 主程序入口
├── requirements.txt              # 依赖包列表
├── README.md                     # 项目说明
├── CLAUDE.md                     # Claude Code指导文档
└── KeyboardClicker.code-workspace # VS Code工作区配置
```

## 截图功能

项目现已集成完整的截图功能模块，支持：

- ✅ **全屏截图**: 捕获整个桌面
- ✅ **区域截图**: 捕获指定区域
- ✅ **自动保存**: 支持自定义文件名和保存路径
- ✅ **文件管理**: 截图列表、删除、信息获取
- ✅ **多种格式**: 支持PNG、JPG、BMP等格式

### 快速使用截图功能

```python
from src.utils.screenshot import ScreenshotTool

# 创建截图工具
screenshot_tool = ScreenshotTool()

# 全屏截图
file_path = screenshot_tool.capture_and_save_full_screen()
print(f"截图已保存: {file_path}")

# 区域截图 (x, y, width, height)
region_path = screenshot_tool.capture_and_save_region(100, 100, 400, 300)
```

### 运行截图演示

```bash
python examples/screenshot_demo.py
```

详细使用说明请参考 [screenshot_usage.md](docs/screenshot_usage.md)

## 边界框覆盖层功能

项目新增了独立的边界框可视化模块，可以在屏幕上显示透明的彩色边界框：

- ✅ **检测结果可视化**: 为OCR识别结果显示边界框
- ✅ **自定义边界框**: 在任意位置显示边界框
- ✅ **可配置样式**: 支持颜色、线宽、透明度自定义
- ✅ **定时显示**: 支持自动隐藏或永久显示
- ✅ **易于集成**: 其他模块可轻松调用

### 快速使用边界框功能

```python
from src.utils.bounding_box_overlay import BoundingBoxOverlay

# 创建边界框工具
bbox_overlay = BoundingBoxOverlay()

# 显示自定义边界框
bbox_overlay.ShowCustomBoundingBox(
    x=100, y=100, width=200, height=80,
    duration=3.0,           # 显示3秒
    box_color='red',        # 红色边界框
    box_width=2             # 线宽2像素
)

# 显示检测结果的边界框
detections = [{'bbox': (x, y, w, h), 'text': '内容'}]
bbox_overlay.ShowBoundingBoxes(detections, duration=5.0, box_color='blue')

# 隐藏所有边界框
bbox_overlay.HideBoundingBoxes()
```

### 运行边界框演示

```bash
python examples/improved_bbox_test.py
python examples/bbox_usage_example.py
```

详细使用说明请参考 [bounding_box_overlay.md](docs/bounding_box_overlay.md)

## OCR识别与标签功能

项目集成了完整的OCR文字识别和智能标签系统：

- ✅ **多种识别模式**: 标准、深度、超级激进模式
- ✅ **智能标签生成**: 为识别结果自动生成唯一标签
- ✅ **屏幕覆盖显示**: 标签直接显示在检测位置上方
- ✅ **边界框预览**: 可选择先显示边界框再显示标签

### 运行OCR演示

```bash
python examples/ocr_label_integration_demo.py
```

## 测试

### 多屏幕功能测试

项目提供了专门的多屏幕测试脚本来验证多显示器环境下的功能：

```bash
python tests/test_multiscreen.py
```

**测试内容包括**：
- 屏幕边界检测和虚拟坐标系统
- 负坐标处理（扩展显示器）
- 坐标验证功能
- 屏幕信息获取和显示

**建议测试场景**：
1. **单屏幕环境** - 验证基本功能正常工作
2. **双屏幕环境** - 测试扩展屏幕和负坐标处理
3. **热插拔测试** - 连接/断开显示器时测试动态刷新功能

更多多屏幕支持信息请参考 [多屏幕支持说明.md](docs/多屏幕支持说明.md)

## 功能规划

### 已完成功能 ✅
- [x] ~~截图功能集成~~ ✅ 已完成
- [x] ~~多屏幕支持~~ ✅ 已完成  
- [x] ~~模块化架构重构~~ ✅ 已完成
- [x] ~~OCR文字识别功能~~ ✅ 已完成
- [x] ~~智能标签系统~~ ✅ 已完成
- [x] ~~边界框覆盖层模块~~ ✅ 已完成

### 后续规划 🚀
- [ ] 截图功能集成到GUI界面
- [ ] OCR功能集成到主界面
- [ ] 配置文件系统
- [ ] 更多识别算法支持

## 许可证

本项目采用 MIT 许可证。详情请参考 LICENSE 文件。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 免责声明

本工具仅供学习和个人使用。请勿用于任何可能违反软件使用条款或法律法规的自动化操作。使用本工具所产生的任何后果由用户自行承担。