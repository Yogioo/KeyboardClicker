#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
屏幕识别功能演示
展示如何使用 ScreenRecognizer 类进行文字和按钮识别
"""

import sys
import os
import time
from pathlib import Path

# 添加父目录到路径中，以便导入模块
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.recognition import ScreenRecognizer
from src.utils.screenshot import ScreenshotTool
from src.utils.screen_labeler import ScreenLabeler

def on_recognition_success(message):
    """识别成功回调"""
    print(f"[识别成功] {message}")

def on_recognition_error(message):
    """识别错误回调"""
    print(f"[识别错误] {message}")

def on_labeler_success(message):
    """标签显示成功回调"""
    print(f"[标签显示] {message}")

def on_labeler_error(message):
    """标签显示错误回调"""
    print(f"[标签错误] {message}")

def demo_basic_recognition():
    """基础识别演示"""
    print("=== 基础识别演示 ===")
    
    # 创建识别器
    recognizer = ScreenRecognizer()
    recognizer.set_recognition_callback(on_recognition_success)
    recognizer.set_error_callback(on_recognition_error)
    
    print("正在进行屏幕识别，请稍候...")
    
    try:
        # 识别当前屏幕
        results = recognizer.recognize_all()
        
        print(f"\n识别结果:")
        print(f"- 总元素数量: {results['total_items']}")
        print(f"- 文字区域: {results['text_count']} 个")
        print(f"- 按钮区域: {results['button_count']} 个")
        
        # 显示前5个文字结果
        if results['text']:
            print(f"\n前5个文字识别结果:")
            for i, text_item in enumerate(results['text'][:5]):
                print(f"{i+1}. 文字: '{text_item['text'][:30]}...' "
                      f"位置: ({text_item['center_x']}, {text_item['center_y']}) "
                      f"大小: {text_item['width']}x{text_item['height']} "
                      f"置信度: {text_item['confidence']:.2f}")
        
        # 显示前5个按钮结果
        if results['buttons']:
            print(f"\n前5个按钮识别结果:")
            for i, button_item in enumerate(results['buttons'][:5]):
                button_text = button_item['text'] if button_item['text'] else "无文字"
                print(f"{i+1}. 按钮: '{button_text[:20]}' "
                      f"位置: ({button_item['center_x']}, {button_item['center_y']}) "
                      f"大小: {button_item['width']}x{button_item['height']} "
                      f"置信度: {button_item['confidence']:.2f}")
                      
    except Exception as e:
        print(f"识别失败: {e}")

def demo_text_search():
    """文字搜索演示"""
    print("\n=== 文字搜索演示 ===")
    
    recognizer = ScreenRecognizer()
    recognizer.set_recognition_callback(on_recognition_success)
    recognizer.set_error_callback(on_recognition_error)
    
    # 搜索常见的界面元素
    search_terms = ["确定", "取消", "保存", "设置", "菜单", "文件", "Edit", "File", "Save"]
    
    for term in search_terms:
        try:
            results = recognizer.find_elements_by_text(term)
            if results:
                print(f"\n找到包含 '{term}' 的元素 {len(results)} 个:")
                for i, item in enumerate(results[:3]):  # 只显示前3个
                    print(f"  {i+1}. {item['type']}: '{item['text'][:30]}' "
                          f"在 ({item['center_x']}, {item['center_y']})")
                break  # 找到一个就停止，避免输出太多
        except Exception as e:
            print(f"搜索 '{term}' 失败: {e}")

def demo_position_detection():
    """位置检测演示"""
    print("\n=== 位置检测演示 ===")
    
    recognizer = ScreenRecognizer()
    recognizer.set_recognition_callback(on_recognition_success)
    recognizer.set_error_callback(on_recognition_error)
    
    # 检测几个常见位置的元素
    test_positions = [
        (100, 100),   # 左上角区域
        (500, 300),   # 中央区域
        (1000, 100),  # 右上角区域（如果存在）
    ]
    
    for x, y in test_positions:
        try:
            element = recognizer.get_element_at_position(x, y)
            if element:
                print(f"位置 ({x}, {y}) 发现元素:")
                print(f"  类型: {element['type']}")
                print(f"  文字: '{element['text'][:30]}...'")
                print(f"  大小: {element['width']}x{element['height']}")
            else:
                print(f"位置 ({x}, {y}) 没有发现元素")
        except Exception as e:
            print(f"位置检测失败 ({x}, {y}): {e}")

def demo_save_annotated():
    """保存标注图像演示"""
    print("\n=== 保存标注图像演示 ===")
    
    recognizer = ScreenRecognizer()
    recognizer.set_recognition_callback(on_recognition_success)
    recognizer.set_error_callback(on_recognition_error)
    
    try:
        # 生成带时间戳的文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_path = f"assets/screenshots/recognition_demo_{timestamp}.png"
        
        # 确保目录存在
        os.makedirs("assets/screenshots", exist_ok=True)
        
        # 保存标注图像
        saved_path = recognizer.save_annotated_image(
            output_path=output_path,
            show_text=True,
            show_buttons=True
        )
        
        print(f"标注图像已保存到: {saved_path}")
        print("可以打开该图像查看识别结果的可视化标注")
        
    except Exception as e:
        print(f"保存标注图像失败: {e}")

def demo_statistics():
    """统计信息演示"""
    print("\n=== 统计信息演示 ===")
    
    recognizer = ScreenRecognizer()
    recognizer.set_recognition_callback(on_recognition_success)
    recognizer.set_error_callback(on_recognition_error)
    
    try:
        stats = recognizer.get_recognition_statistics()
        
        print("识别统计信息:")
        print(f"- 总元素数量: {stats['total_elements']}")
        print(f"- 文字元素: {stats['text_elements']}")
        print(f"- 按钮元素: {stats['button_elements']}")
        
        if stats['text_elements'] > 0:
            print(f"- 文字平均置信度: {stats['average_text_confidence']:.2f}")
            print(f"- 文字长度统计: 最短 {stats['text_length_stats']['min']} "
                  f"最长 {stats['text_length_stats']['max']} "
                  f"平均 {stats['text_length_stats']['average']:.1f}")
        
        if stats['button_elements'] > 0:
            print(f"- 按钮平均置信度: {stats['average_button_confidence']:.2f}")
            print(f"- 按钮大小统计: 最小 {stats['button_size_stats']['min_area']} "
                  f"最大 {stats['button_size_stats']['max_area']} "
                  f"平均 {stats['button_size_stats']['average_area']:.0f}")
                  
    except Exception as e:
        print(f"获取统计信息失败: {e}")

def demo_with_screenshot():
    """结合截图功能演示"""
    print("\n=== 结合截图功能演示 ===")
    
    # 创建截图工具
    screenshot_tool = ScreenshotTool()
    recognizer = ScreenRecognizer()
    
    # 设置回调
    screenshot_tool.set_screenshot_callback(lambda msg: print(f"[截图] {msg}"))
    screenshot_tool.set_error_callback(lambda msg: print(f"[截图错误] {msg}"))
    recognizer.set_recognition_callback(on_recognition_success)
    recognizer.set_error_callback(on_recognition_error)
    
    try:
        print("正在截取屏幕...")
        # 先截图
        screenshot_path = screenshot_tool.capture_and_save_full_screen()
        
        print(f"对截图文件进行识别: {screenshot_path}")
        # 然后识别截图文件
        results = recognizer.recognize_all(screenshot_path)
        
        print(f"文件识别结果: 发现 {results['total_items']} 个元素")
        
    except Exception as e:
        print(f"截图识别演示失败: {e}")

def demo_screen_labeler():
    """屏幕标签显示演示"""
    print("\n=== 屏幕标签显示演示 ===")
    
    # 创建识别器和标签显示器
    recognizer = ScreenRecognizer()
    labeler = ScreenLabeler()
    
    # 设置回调
    recognizer.set_recognition_callback(on_recognition_success)
    recognizer.set_error_callback(on_recognition_error)
    labeler.SetCallback(on_labeler_success)
    labeler.SetErrorCallback(on_labeler_error)
    
    try:
        print("正在识别屏幕元素...")
        results = recognizer.recognize_all()
        
        if results['total_items'] == 0:
            print("没有识别到任何元素，展示测试标签...")
            # 如果没有识别到元素，显示测试标签
            labeler.ShowTestLabels(count=6, duration=5.0)
            return
        
        # 合并所有识别到的元素
        all_elements = []
        
        # 添加文字元素
        for text_item in results.get('text', []):
            all_elements.append({
                'center_x': text_item['center_x'],
                'center_y': text_item['center_y'],
                'text': text_item['text'],
                'type': 'text',
                'confidence': text_item['confidence']
            })
        
        # 添加按钮元素
        for button_item in results.get('buttons', []):
            all_elements.append({
                'center_x': button_item['center_x'],
                'center_y': button_item['center_y'],
                'text': button_item.get('text', '按钮'),
                'type': 'button',
                'confidence': button_item['confidence']
            })
        
        if all_elements:
            print(f"将为 {len(all_elements)} 个元素显示标签...")
            print("标签将显示10秒钟...")
            
            # 显示标签
            success = labeler.ShowLabels(all_elements, duration=10.0)
            
            if success:
                # 显示标签映射
                labels = labeler.GetDisplayedLabels()
                print("\n标签映射:")
                for i, (element, label) in enumerate(zip(all_elements, labels)):
                    element_text = element['text'][:20] if element['text'] else '无文字'
                    print(f"  {label}: {element['type']} - '{element_text}' "
                          f"位置:({element['center_x']}, {element['center_y']})")
                    if i >= 9:  # 只显示前10个
                        if len(all_elements) > 10:
                            print(f"  ... 还有 {len(all_elements) - 10} 个元素")
                        break
                
                print("\n提示: 标签将在10秒后自动消失")
                print("按Ctrl+C可以提前结束程序")
                
                # 等待标签显示完成
                time.sleep(11)
            else:
                print("标签显示失败")
        else:
            print("没有找到可以显示标签的元素")
            
    except KeyboardInterrupt:
        print("\n用户中断，正在关闭标签...")
        labeler.HideLabels()
    except Exception as e:
        print(f"屏幕标签演示失败: {e}")
        try:
            labeler.HideLabels()
        except:
            pass

def demo_labeler_test():
    """标签生成测试演示"""
    print("\n=== 标签生成测试演示 ===")
    
    labeler = ScreenLabeler()
    labeler.SetCallback(on_labeler_success)
    labeler.SetErrorCallback(on_labeler_error)
    
    try:
        # 测试标签生成
        print("测试生成前100个标签:")
        test_labels = labeler.TestLabelGeneration(100)
        
        # 显示前30个标签
        if test_labels:
            print("前30个标签:")
            for i in range(min(30, len(test_labels))):
                print(f"  {i+1:2d}: {test_labels[i]}")
            
            if len(test_labels) > 30:
                print(f"  ... 还有 {len(test_labels) - 30} 个标签")
        
        # 显示测试标签
        print("\n显示测试标签网格 (3x2)...")
        labeler.ShowTestLabels(count=6, duration=5.0)
        
        print("测试标签将显示5秒钟...")
        time.sleep(6)
        
    except KeyboardInterrupt:
        print("\n用户中断")
        labeler.HideLabels()
    except Exception as e:
        print(f"标签测试失败: {e}")

def demo_advanced_features():
    """高级功能演示"""
    print("\n=== 高级功能演示 ===")
    
    recognizer = ScreenRecognizer()
    recognizer.set_recognition_callback(on_recognition_success)
    recognizer.set_error_callback(on_recognition_error)
    
    # 设置自定义参数
    print("设置自定义识别参数...")
    recognizer.set_button_detection_params(
        min_area=50,      # 降低最小按钮面积
        max_area=30000,   # 降低最大按钮面积
        aspect_ratio_range=(0.1, 10.0)  # 扩大长宽比范围
    )
    
    # 设置自定义OCR配置
    recognizer.set_tesseract_config('--oem 3 --psm 11')  # 稀疏文字模式
    
    try:
        print("使用自定义参数进行识别...")
        results = recognizer.recognize_all()
        print(f"自定义参数识别结果: {results['total_items']} 个元素")
        
    except Exception as e:
        print(f"高级功能演示失败: {e}")

def main():
    """主演示函数"""
    print("屏幕识别功能演示程序")
    print("=" * 50)
    
    print("\n注意事项:")
    print("1. 需要安装 tesseract-ocr 程序")
    print("2. 需要安装 Python 依赖: pip install -r requirements.txt")
    print("3. 程序将识别当前屏幕内容")
    print("4. 识别过程可能需要几秒钟时间")
    
    input("\n按 Enter 键开始演示...")
    
    try:
        # 运行各种演示
        demo_basic_recognition()
        demo_text_search()
        demo_position_detection()
        demo_save_annotated()
        demo_statistics()
        demo_with_screenshot()
        demo_advanced_features()
        
        # 新增: 标签显示功能演示
        demo_labeler_test()
        demo_screen_labeler()
        
        print("\n" + "=" * 50)
        print("演示完成！")
        print("\n可以查看以下文件了解更多用法:")
        print("- src/utils/recognition.py - 识别功能源代码")
        print("- src/utils/screen_labeler.py - 标签显示功能源代码")
        print("- docs/screenshot_usage.md - 截图功能文档")
        print("- assets/screenshots/ - 保存的截图和标注图像")
        
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"\n演示过程中发生错误: {e}")
        print("请检查依赖是否正确安装")

if __name__ == "__main__":
    main()