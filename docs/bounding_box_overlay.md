# BoundingBoxOverlay 边界框覆盖层工具

## 概述

`BoundingBoxOverlay` 是一个独立的边界框显示工具模块，用于在屏幕上显示透明的彩色边界框，标识检测到的区域或目标。该模块从原始的 OCR 集成演示中提取而来，现在可以被项目中的任何其他组件轻松复用。

## 主要功能

- ✅ 显示检测结果的边界框
- ✅ 显示自定义位置的边界框  
- ✅ 从坐标列表批量显示边界框
- ✅ 可配置的颜色、线宽、透明度
- ✅ 支持自动定时隐藏或永久显示
- ✅ 完善的错误处理和回调机制
- ✅ 跨平台兼容（Windows测试通过）

## 文件位置

```
src/utils/bounding_box_overlay.py
```

## 快速开始

### 基本使用

```python
from src.utils.bounding_box_overlay import BoundingBoxOverlay

# 创建边界框工具
bbox_overlay = BoundingBoxOverlay()

# 显示自定义边界框
bbox_overlay.ShowCustomBoundingBox(
    x=100, y=100, width=200, height=80,
    duration=3.0,           # 显示3秒
    box_color='red',        # 红色边界框
    box_width=2,            # 线宽2像素
    alpha=0.8               # 80%透明度
)

# 隐藏所有边界框
bbox_overlay.HideBoundingBoxes()
```

### 显示检测结果

```python
# 检测结果格式
detections = [
    {
        'bbox': (100, 100, 150, 50),    # (x, y, width, height)
        'text': '开始按钮',
        'confidence': 0.95
    },
    {
        'bbox': (300, 200, 120, 40),
        'text': '设置选项', 
        'confidence': 0.88
    }
]

# 显示检测结果的边界框
bbox_overlay.ShowBoundingBoxes(
    detections, 
    duration=5.0,           # 5秒后自动隐藏
    box_color='blue',       # 蓝色边界框
    box_width=3             # 3像素线宽
)
```

### 从坐标列表显示

```python
# 坐标列表格式: [(x, y, width, height), ...]
coordinates = [
    (50, 50, 100, 40),      # 第一个区域
    (200, 100, 120, 50),    # 第二个区域
    (350, 150, 80, 30)      # 第三个区域
]

bbox_overlay.ShowBoundingBoxesFromCoords(
    coordinates,
    duration=None,          # 永久显示，直到手动隐藏
    box_color='green',
    box_width=2
)
```

## API 参考

### 类：BoundingBoxOverlay

#### 构造函数
```python
def __init__(self)
```
创建边界框覆盖层实例。

#### 主要方法

##### ShowBoundingBoxes
```python
def ShowBoundingBoxes(self, detections, duration=None, box_color='red', box_width=2, alpha=0.8) -> bool
```
显示检测结果的边界框。

**参数：**
- `detections` (List[Dict]): 检测结果列表，每个元素必须包含 `'bbox'` 字段
- `duration` (float, optional): 显示持续时间（秒），`None` 表示永久显示
- `box_color` (str): 边界框颜色，默认 `'red'`
- `box_width` (int): 边界框线宽，默认 `2`
- `alpha` (float): 窗口透明度，默认 `0.8`

**返回：** `bool` - 成功返回 `True`，失败返回 `False`

##### ShowCustomBoundingBox
```python
def ShowCustomBoundingBox(self, x, y, width, height, duration=None, box_color='red', box_width=2, alpha=0.8) -> bool
```
显示单个自定义边界框。

**参数：**
- `x`, `y` (int): 左上角坐标
- `width`, `height` (int): 宽度和高度
- 其他参数同 `ShowBoundingBoxes`

##### ShowBoundingBoxesFromCoords
```python
def ShowBoundingBoxesFromCoords(self, coords_list, duration=None, box_color='red', box_width=2, alpha=0.8) -> bool
```
从坐标列表显示边界框。

**参数：**
- `coords_list` (List[tuple]): 坐标列表，每个元素为 `(x, y, width, height)`
- 其他参数同 `ShowBoundingBoxes`

##### HideBoundingBoxes
```python
def HideBoundingBoxes(self)
```
隐藏所有边界框。

#### 辅助方法

##### SetInfoCallback / SetErrorCallback
```python
def SetInfoCallback(self, callback)
def SetErrorCallback(self, callback)
```
设置信息和错误回调函数。

##### GetActiveBoxCount / IsShowing
```python
def GetActiveBoxCount(self) -> int
def IsShowing(self) -> bool
```
获取当前活跃边界框数量和显示状态。

## 配置选项

### 支持的颜色
- `'red'` - 红色（默认）
- `'blue'` - 蓝色
- `'green'` - 绿色  
- `'yellow'` - 黄色
- `'purple'` - 紫色
- `'orange'` - 橙色
- `'black'` - 黑色
- `'white'` - 白色

### 线宽范围
- 推荐范围：1-10 像素
- 默认：2 像素

### 透明度范围
- 范围：0.1-1.0
- 0.1 = 高度透明，1.0 = 完全不透明
- 默认：0.8

## 使用场景

### 1. OCR 结果可视化
```python
# OCR 识别后显示文字区域
ocr_results = recognizer.recognize_text(image)
bbox_overlay.ShowBoundingBoxes(ocr_results, duration=3.0, box_color='blue')
```

### 2. 点击目标高亮
```python
# 高亮可点击的按钮区域
click_targets = [(100, 200, 80, 30), (250, 200, 90, 30)]
bbox_overlay.ShowBoundingBoxesFromCoords(click_targets, box_color='green')
```

### 3. 分步操作引导
```python
# 步骤引导，逐步高亮不同区域
bbox_overlay.ShowCustomBoundingBox(100, 100, 120, 40, duration=2.0, box_color='red')
time.sleep(2)
bbox_overlay.ShowCustomBoundingBox(250, 150, 100, 35, duration=2.0, box_color='blue')
```

### 4. 在类中集成使用
```python
class MyApplication:
    def __init__(self):
        self._bbox_overlay = BoundingBoxOverlay()
        self._bbox_overlay.SetInfoCallback(self._on_bbox_info)
    
    def highlight_area(self, x, y, w, h):
        return self._bbox_overlay.ShowCustomBoundingBox(x, y, w, h)
    
    def clear_highlights(self):
        self._bbox_overlay.HideBoundingBoxes()
    
    def _on_bbox_info(self, message):
        print(f"[应用] {message}")
```

## 测试文件

项目提供了多个测试文件来验证功能：

- `examples/test_bounding_box_overlay.py` - 基础功能测试
- `examples/improved_bbox_test.py` - 改进版测试（解决显示时机问题）
- `examples/bbox_usage_example.py` - 各种使用场景示例
- `examples/usage_with_new_bbox_module.py` - 迁移示例

运行测试：
```bash
python examples/improved_bbox_test.py
```

## 注意事项

1. **Windows 兼容性**：在 Windows 环境下测试通过，支持透明窗口显示
2. **显示时机**：模块已优化窗口显示时机，确保边界框能正确显示
3. **资源清理**：使用完毕后建议调用 `HideBoundingBoxes()` 清理资源
4. **坐标系统**：使用屏幕绝对坐标系统，左上角为 (0,0)
5. **性能考虑**：避免同时显示过多边界框，建议不超过20个

## 错误处理

模块内置了完善的错误处理机制：

```python
# 设置错误回调
def error_handler(message):
    print(f"边界框错误: {message}")

bbox_overlay.SetErrorCallback(error_handler)

# 常见错误情况
# 1. 空检测结果
bbox_overlay.ShowBoundingBoxes([])  # 返回 False，触发错误回调

# 2. 缺少必要字段
invalid_data = [{'text': '无bbox字段'}]
bbox_overlay.ShowBoundingBoxes(invalid_data)  # 返回 False

# 3. 坐标格式错误
invalid_coords = [(100, 100)]  # 缺少 width, height
bbox_overlay.ShowBoundingBoxesFromCoords(invalid_coords)  # 返回 False
```

## 版本历史

- **v1.0** - 从 OCR 集成演示中提取独立模块
- **v1.1** - 添加强制窗口更新机制，解决显示时机问题
- **v1.2** - 完善错误处理和回调机制

## 贡献

如需改进此模块，请确保：
1. 保持 API 兼容性
2. 添加适当的测试用例
3. 更新文档说明