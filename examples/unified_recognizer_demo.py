# -*- coding: utf-8 -*-
"""
统一图像识别器演示

演示统一识别算法的使用方法和性能对比。
"""

import cv2
import numpy as np
import time
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.unified_recognizer import UnifiedVisualRecognizer, UnifiedRecognitionConfig
from src.utils.screenshot import ScreenshotTool
from src.utils.bounding_box_overlay import BoundingBoxOverlay

def demo_basic_usage():
    """基本使用演示"""
    print("=== 统一识别器基本使用演示 ===")
    
    # 1. 创建识别器
    recognizer = UnifiedVisualRecognizer()
    
    # 2. 截取屏幕
    screenshot_tool = ScreenshotTool()
    image_pil = screenshot_tool.capture_full_screen()
    image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    
    if image is None:
        print("截图失败")
        return
    
    print(f"截图尺寸: {image.shape}")
    
    # 3. 执行识别
    start_time = time.time()
    results = recognizer.DetectClickableElements(image)
    recognition_time = time.time() - start_time
    
    print(f"识别完成，耗时: {recognition_time:.3f}秒")
    print(f"检测到 {len(results)} 个可点击元素")
    
    # 4. 显示结果统计
    type_counts = {}
    for result in results:
        element_type = result['type']
        type_counts[element_type] = type_counts.get(element_type, 0) + 1
    
    print("元素类型统计:")
    for element_type, count in type_counts.items():
        print(f"  {element_type}: {count}")
    
    # 5. 显示前5个最高置信度的结果
    sorted_results = sorted(results, key=lambda x: x['confidence'], reverse=True)
    print("\n前5个最高置信度的元素:")
    for i, result in enumerate(sorted_results[:5]):
        bbox = result['bbox']
        print(f"  {i+1}. {result['type']} - 置信度: {result['confidence']:.3f} - 位置: {bbox}")

def demo_configuration():
    """配置演示"""
    print("\n=== 配置演示 ===")
    
    # 1. 使用快速配置
    config = UnifiedRecognitionConfig()
    config.LoadFastConfig()
    
    recognizer = UnifiedVisualRecognizer(config)
    
    # 2. 截取屏幕
    screenshot_tool = ScreenshotTool()
    image_pil = screenshot_tool.capture_full_screen()
    image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    
    if image is None:
        print("截图失败")
        return
    
    # 3. 快速识别
    start_time = time.time()
    results_fast = recognizer.DetectClickableElements(image)
    fast_time = time.time() - start_time
    
    print(f"快速模式: {len(results_fast)} 个元素，耗时: {fast_time:.3f}秒")
    
    # 4. 使用精确配置
    config.LoadAccurateConfig()
    recognizer.UpdateConfig(config)
    
    start_time = time.time()
    results_accurate = recognizer.DetectClickableElements(image)
    accurate_time = time.time() - start_time
    
    print(f"精确模式: {len(results_accurate)} 个元素，耗时: {accurate_time:.3f}秒")
    
    # 5. 性能对比
    print(f"速度提升: {accurate_time/fast_time:.2f}x")

def demo_single_type_detection():
    """单类型检测演示"""
    print("\n=== 单类型检测演示 ===")
    
    recognizer = UnifiedVisualRecognizer()
    screenshot_tool = ScreenshotTool()
    image_pil = screenshot_tool.capture_full_screen()
    image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    
    if image is None:
        print("截图失败")
        return
    
    # 检测不同类型的元素
    element_types = ['button', 'icon', 'text', 'link', 'input']
    
    for element_type in element_types:
        start_time = time.time()
        results = recognizer.DetectSingleType(element_type, image)
        detection_time = time.time() - start_time
        
        print(f"{element_type}: {len(results)} 个，耗时: {detection_time:.3f}秒")
        
        # 显示最高置信度的结果
        if results:
            best_result = max(results, key=lambda x: x['confidence'])
            bbox = best_result['bbox']
            print(f"  最佳: 置信度 {best_result['confidence']:.3f}, 位置 {bbox}")

def demo_visual_overlay():
    """可视化覆盖演示"""
    print("\n=== 可视化覆盖演示 ===")
    
    try:
        recognizer = UnifiedVisualRecognizer()
        screenshot_tool = ScreenshotTool()
        bbox_overlay = BoundingBoxOverlay()
        
        # 截图
        image_pil = screenshot_tool.capture_full_screen()
        image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        if image is None:
            print("截图失败")
            return
        
        # 识别
        results = recognizer.DetectClickableElements(image)
        print(f"检测到 {len(results)} 个元素")
        
        if not results:
            print("没有检测到元素")
            return
        
        # 按类型分组显示
        type_colors = {
            'button': 'red',
            'icon': 'blue',
            'text': 'green',
            'link': 'yellow',
            'input': 'purple'
        }
        
        print("正在显示边界框覆盖...")
        
        for element_type, color in type_colors.items():
            type_results = [r for r in results if r['type'] == element_type]
            if type_results:
                print(f"显示 {len(type_results)} 个 {element_type} (颜色: {color})")
                
                # 转换为边界框坐标列表
                coords = [(r['bbox'][0], r['bbox'][1], r['bbox'][2], r['bbox'][3]) for r in type_results]
                
                # 显示边界框
                bbox_overlay.ShowBoundingBoxesFromCoords(coords, box_color=color, duration=2.0)
                
                # 等待用户确认
                input(f"按回车键继续显示下一类型...")
        
        print("演示完成")
        
    except Exception as e:
        print(f"可视化演示失败: {e}")

def demo_performance_analysis():
    """性能分析演示"""
    print("\n=== 性能分析演示 ===")
    
    recognizer = UnifiedVisualRecognizer()
    screenshot_tool = ScreenshotTool()
    
    # 多次测试获取平均性能
    test_count = 5
    times = []
    
    print(f"执行 {test_count} 次识别测试...")
    
    for i in range(test_count):
        image_pil = screenshot_tool.capture_full_screen()
        image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        if image is None:
            continue
        
        start_time = time.time()
        results = recognizer.DetectClickableElements(image)
        recognition_time = time.time() - start_time
        
        times.append(recognition_time)
        print(f"  测试 {i+1}: {len(results)} 个元素，耗时 {recognition_time:.3f}秒")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n性能统计:")
        print(f"  平均时间: {avg_time:.3f}秒")
        print(f"  最快时间: {min_time:.3f}秒")
        print(f"  最慢时间: {max_time:.3f}秒")
        
        # 获取系统性能统计
        stats = recognizer.GetPerformanceStats()
        print(f"  缓存命中率: {stats.get('cache_hit_rate', 0):.2%}")

def demo_diagnosis():
    """诊断演示"""
    print("\n=== 诊断演示 ===")
    
    recognizer = UnifiedVisualRecognizer()
    screenshot_tool = ScreenshotTool()
    
    image_pil = screenshot_tool.capture_full_screen()
    image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    if image is None:
        print("截图失败")
        return
    
    # 执行诊断
    diagnosis = recognizer.DiagnoseImage(image)
    
    print("图像诊断结果:")
    
    # 图像信息
    image_info = diagnosis.get('image_info', {})
    print(f"  图像尺寸: {image_info.get('shape', 'N/A')}")
    print(f"  图像大小: {image_info.get('size_mb', 0):.2f} MB")
    
    # 金字塔信息
    pyramid_info = diagnosis.get('pyramid_info', {})
    print(f"  金字塔层数: {pyramid_info.get('levels', 0)}")
    print(f"  总像素数: {pyramid_info.get('total_pixels', 0):,}")
    
    # 特征信息
    print(f"  特征数量: {diagnosis.get('feature_count', 0)}")
    
    # 分类结果
    classification_results = diagnosis.get('classification_results', {})
    print("  分类结果:")
    for element_type, count in classification_results.items():
        print(f"    {element_type}: {count}")
    
    # 处理时间
    processing_times = diagnosis.get('processing_times', {})
    print("  处理时间:")
    for stage, time_cost in processing_times.items():
        print(f"    {stage}: {time_cost:.3f}秒")

def main():
    """主函数"""
    print("统一图像识别器演示程序")
    print("=" * 50)
    
    try:
        # 基本使用演示
        demo_basic_usage()
        
        # 配置演示
        demo_configuration()
        
        # 单类型检测演示
        demo_single_type_detection()
        
        # 性能分析演示
        demo_performance_analysis()
        
        # 诊断演示
        demo_diagnosis()
        
        # 询问是否进行可视化演示
        user_input = input("\n是否进行可视化覆盖演示? (会在屏幕上显示边界框) [y/N]: ")
        if user_input.lower() in ['y', 'yes']:
            demo_visual_overlay()
        
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"\n演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()