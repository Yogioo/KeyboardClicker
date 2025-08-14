#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
边界框覆盖层使用示例
展示如何在其他模块中使用BoundingBoxOverlay
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.bounding_box_overlay import BoundingBoxOverlay


def example_with_ocr_results():
    """示例：配合OCR识别结果使用"""
    print("=== 示例：配合OCR识别结果使用 ===")
    
    # 模拟OCR识别结果
    ocr_results = [
        {
            'text': '开始按钮',
            'bbox': (100, 100, 80, 30),
            'confidence': 0.95,
            'center_x': 140,
            'center_y': 115
        },
        {
            'text': '设置选项', 
            'bbox': (200, 150, 90, 25),
            'confidence': 0.88,
            'center_x': 245,
            'center_y': 162
        },
        {
            'text': '退出程序',
            'bbox': (300, 200, 70, 28),
            'confidence': 0.92,
            'center_x': 335,
            'center_y': 214
        }
    ]
    
    # 创建边界框工具
    bbox_overlay = BoundingBoxOverlay()
    
    try:
        # 显示OCR结果的边界框
        print("显示OCR识别结果的边界框...")
        success = bbox_overlay.ShowBoundingBoxes(ocr_results, duration=3.0, box_color='blue')
        
        if success:
            print(f"成功显示 {len(ocr_results)} 个文字区域的边界框")
            print("边界框将显示3秒...")
            time.sleep(3)
        else:
            print("显示边界框失败")
            
    finally:
        bbox_overlay.HideBoundingBoxes()


def example_with_click_targets():
    """示例：标识可点击目标区域"""
    print("\n=== 示例：标识可点击目标区域 ===")
    
    # 模拟可点击区域
    click_targets = [
        (50, 50, 100, 40),    # 菜单按钮
        (200, 50, 80, 40),    # 工具按钮
        (320, 50, 90, 40),    # 帮助按钮
        (450, 100, 120, 50),  # 主要操作按钮
    ]
    
    bbox_overlay = BoundingBoxOverlay()
    
    try:
        # 用红色边界框标识可点击区域
        print("用红色边界框标识可点击区域...")
        success = bbox_overlay.ShowBoundingBoxesFromCoords(
            click_targets, 
            duration=4.0, 
            box_color='red', 
            box_width=3
        )
        
        if success:
            print(f"成功标识 {len(click_targets)} 个可点击区域")
            print("红色边界框将显示4秒...")
            time.sleep(4)
            
    finally:
        bbox_overlay.HideBoundingBoxes()


def example_with_step_by_step_guide():
    """示例：分步引导用户操作"""
    print("\n=== 示例：分步引导用户操作 ===")
    
    bbox_overlay = BoundingBoxOverlay()
    
    try:
        # 步骤1：点击开始按钮
        print("步骤1: 请点击开始按钮")
        bbox_overlay.ShowCustomBoundingBox(
            100, 300, 100, 35, 
            duration=2.0, 
            box_color='green', 
            box_width=4
        )
        time.sleep(2)
        
        # 步骤2：选择选项
        print("步骤2: 请选择相应选项")
        bbox_overlay.ShowCustomBoundingBox(
            250, 350, 120, 40, 
            duration=2.0, 
            box_color='orange', 
            box_width=4
        )
        time.sleep(2)
        
        # 步骤3：确认操作
        print("步骤3: 请确认操作")
        bbox_overlay.ShowCustomBoundingBox(
            400, 400, 80, 30, 
            duration=2.0, 
            box_color='blue', 
            box_width=4
        )
        time.sleep(2)
        
        print("引导完成！")
        
    finally:
        bbox_overlay.HideBoundingBoxes()


def example_integration_in_class():
    """示例：在类中集成边界框功能"""
    print("\n=== 示例：在类中集成边界框功能 ===")
    
    class MyApplication:
        """示例应用类，集成了边界框显示功能"""
        
        def __init__(self):
            self._bbox_overlay = BoundingBoxOverlay()
            # 设置回调
            self._bbox_overlay.SetInfoCallback(self._OnBboxInfo)
            self._bbox_overlay.SetErrorCallback(self._OnBboxError)
        
        def _OnBboxInfo(self, message):
            print(f"[应用-边界框] {message}")
        
        def _OnBboxError(self, message):
            print(f"[应用-错误] {message}")
        
        def HighlightArea(self, x, y, width, height, duration=None, color='red'):
            """高亮显示指定区域"""
            return self._bbox_overlay.ShowCustomBoundingBox(
                x, y, width, height, duration, color
            )
        
        def HighlightDetections(self, detections, duration=None):
            """高亮显示检测结果"""
            return self._bbox_overlay.ShowBoundingBoxes(detections, duration)
        
        def ClearHighlights(self):
            """清除所有高亮"""
            self._bbox_overlay.HideBoundingBoxes()
        
        def GetHighlightCount(self):
            """获取当前高亮数量"""
            return self._bbox_overlay.GetActiveBoxCount()
    
    # 使用示例
    app = MyApplication()
    
    try:
        # 高亮某个区域
        print("应用高亮区域...")
        success = app.HighlightArea(500, 250, 150, 60, duration=2.0, color='purple')
        if success:
            print(f"当前高亮数量: {app.GetHighlightCount()}")
            time.sleep(2)
        
        # 高亮多个检测结果
        detections = [
            {'bbox': (100, 400, 80, 25)},
            {'bbox': (200, 400, 90, 25)}
        ]
        print("应用高亮检测结果...")
        app.HighlightDetections(detections, duration=2.0)
        time.sleep(2)
        
    finally:
        app.ClearHighlights()


if __name__ == "__main__":
    print("边界框覆盖层使用示例")
    print("展示如何在不同场景中使用BoundingBoxOverlay模块")
    
    try:
        # 运行所有示例
        example_with_ocr_results()
        example_with_click_targets()
        example_with_step_by_step_guide()
        example_integration_in_class()
        
        print("\n=== 所有示例演示完成 ===")
        print("BoundingBoxOverlay模块可以轻松集成到其他模块中使用！")
        
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"\n演示过程中发生错误: {e}")