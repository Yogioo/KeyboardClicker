# 截图功能工具类使用说明

## 概述

`ScreenshotTool` 是一个功能完整的截图工具类，提供了桌面截图、区域截图、图片保存和管理等功能。该工具类遵循项目的模块化架构设计，可以轻松集成到现有项目中。

## 功能特性

- ✅ 全屏截图
- ✅ 指定区域截图
- ✅ 自动生成文件名（基于时间戳）
- ✅ 自定义保存路径
- ✅ 截图文件管理（列表、删除、信息获取）
- ✅ 错误处理和回调机制
- ✅ 屏幕尺寸获取
- ✅ 支持多种图片格式（PNG、JPG、BMP等）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 基本使用

```python
from screenshot import ScreenshotTool

# 创建截图工具实例
screenshot_tool = ScreenshotTool()

# 全屏截图并保存
screenshot_path = screenshot_tool.capture_and_save_full_screen()
print(f"截图已保存到: {screenshot_path}")

# 区域截图（x, y, width, height）
region_path = screenshot_tool.capture_and_save_region(100, 100, 400, 300)
print(f"区域截图已保存到: {region_path}")
```

### 3. 运行演示

```bash
python screenshot_demo.py
```

## 详细API说明

### 初始化

```python
screenshot_tool = ScreenshotTool()
```

### 屏幕信息

```python
# 获取屏幕尺寸
width, height = screenshot_tool.get_screen_size()
print(f"屏幕尺寸: {width} x {height}")
```

### 截图功能

#### 全屏截图

```python
# 方法1: 捕获并返回PIL Image对象
image = screenshot_tool.capture_full_screen()

# 方法2: 直接捕获并保存
file_path = screenshot_tool.capture_and_save_full_screen()

# 方法3: 自定义文件名和路径
file_path = screenshot_tool.capture_and_save_full_screen(
    filename="my_screenshot.png",
    save_path="my_screenshots"
)
```

#### 区域截图

```python
# 截取指定区域 (x, y, width, height)
image = screenshot_tool.capture_region(100, 100, 400, 300)

# 直接保存区域截图
file_path = screenshot_tool.capture_and_save_region(
    100, 100, 400, 300,
    filename="region.png"
)
```

### 文件管理

#### 保存截图

```python
# 保存PIL Image对象
image = screenshot_tool.capture_full_screen()
file_path = screenshot_tool.save_screenshot(
    image,
    filename="custom_name.png",
    save_path="custom_folder"
)
```

#### 获取截图列表

```python
# 获取默认目录下的所有截图
screenshots = screenshot_tool.get_all_screenshots()

# 获取指定目录下的截图
screenshots = screenshot_tool.get_all_screenshots("custom_folder")

for screenshot_path in screenshots:
    print(screenshot_path)
```

#### 获取截图信息

```python
info = screenshot_tool.get_screenshot_info("screenshots/example.png")
if info:
    print(f"文件名: {info['filename']}")
    print(f"尺寸: {info['width']} x {info['height']}")
    print(f"大小: {info['size_bytes']} bytes")
    print(f"创建时间: {info['created_time']}")
    print(f"格式: {info['format']}")
```

#### 删除截图

```python
success = screenshot_tool.delete_screenshot("screenshots/example.png")
if success:
    print("截图已删除")
```

### 配置管理

#### 设置默认保存路径

```python
# 设置新的默认保存路径
screenshot_tool.set_default_save_path("my_screenshots")

# 获取当前默认保存路径
current_path = screenshot_tool.get_default_save_path()
print(f"当前保存路径: {current_path}")
```

### 回调函数

```python
def on_screenshot_success(message):
    print(f"[成功] {message}")

def on_error(message):
    print(f"[错误] {message}")

# 设置回调函数
screenshot_tool.set_screenshot_callback(on_screenshot_success)
screenshot_tool.set_error_callback(on_error)
```

## 集成到现有项目

### 在主应用中使用

```python
# 在 main.py 中集成
from screenshot import ScreenshotTool

class KeyboardClickerApp:
    def __init__(self):
        self.clicker = ClickerTool()
        self.gui = ClickerGUI()
        self.screenshot = ScreenshotTool()  # 添加截图工具
        
        self._setup_callbacks()
        
    def _setup_callbacks(self):
        # 现有回调...
        
        # 添加截图相关回调
        self.screenshot.set_screenshot_callback(self._handle_screenshot_success)
        self.screenshot.set_error_callback(self._handle_screenshot_error)
        
    def _handle_screenshot_success(self, message):
        """处理截图成功"""
        self.gui.show_info("截图", message)
        
    def _handle_screenshot_error(self, message):
        """处理截图错误"""
        self.gui.show_error("截图错误", message)
        
    def take_screenshot(self):
        """执行截图操作"""
        try:
            file_path = self.screenshot.capture_and_save_full_screen()
            return file_path
        except Exception as e:
            self.gui.show_error("截图失败", str(e))
            return None
```

## 常见用例

### 1. 定时截图

```python
import time
import threading

def auto_screenshot():
    screenshot_tool = ScreenshotTool()
    
    while True:
        try:
            file_path = screenshot_tool.capture_and_save_full_screen()
            print(f"自动截图完成: {file_path}")
            time.sleep(60)  # 每分钟截图一次
        except Exception as e:
            print(f"自动截图失败: {e}")
            break

# 在后台线程中运行
thread = threading.Thread(target=auto_screenshot, daemon=True)
thread.start()
```

### 2. 截图对比

```python
from PIL import ImageChops

def compare_screenshots(path1, path2):
    """比较两个截图的差异"""
    try:
        from PIL import Image
        img1 = Image.open(path1)
        img2 = Image.open(path2)
        
        diff = ImageChops.difference(img1, img2)
        return diff.getbbox() is not None  # 如果有差异返回True
    except Exception as e:
        print(f"比较截图失败: {e}")
        return False

# 使用示例
screenshot_tool = ScreenshotTool()
path1 = screenshot_tool.capture_and_save_full_screen()
time.sleep(5)
path2 = screenshot_tool.capture_and_save_full_screen()

if compare_screenshots(path1, path2):
    print("屏幕内容发生了变化")
else:
    print("屏幕内容没有变化")
```

### 3. 批量处理截图

```python
def process_all_screenshots():
    """处理所有截图文件"""
    screenshot_tool = ScreenshotTool()
    screenshots = screenshot_tool.get_all_screenshots()
    
    for screenshot_path in screenshots:
        info = screenshot_tool.get_screenshot_info(screenshot_path)
        if info:
            print(f"处理: {info['filename']} ({info['width']}x{info['height']})")
            
            # 这里可以添加你的处理逻辑
            # 例如: 压缩图片、添加水印、格式转换等
```

## 注意事项

1. **权限要求**: 截图功能需要屏幕访问权限，某些系统可能需要用户授权
2. **性能考虑**: 全屏截图会占用较多内存，频繁截图时注意内存管理
3. **文件大小**: 高分辨率屏幕的截图文件可能较大，建议根据需要调整保存格式
4. **线程安全**: 在多线程环境中使用时，建议为每个线程创建独立的实例

## 错误处理

所有方法都包含完善的错误处理机制，通过回调函数可以获取详细的错误信息：

```python
def handle_error(error_message):
    print(f"截图操作失败: {error_message}")
    # 这里可以添加日志记录、用户通知等逻辑

screenshot_tool.set_error_callback(handle_error)
```

## 扩展功能

该工具类设计为可扩展的，你可以根据需要添加更多功能：

- 图片压缩和优化
- 水印添加
- 格式转换
- 云存储上传
- 截图标注
- OCR文字识别

---

更多使用示例请参考 `screenshot_demo.py` 文件。