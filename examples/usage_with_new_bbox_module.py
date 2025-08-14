#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用新边界框模块的示例
展示如何将现有代码迁移到使用新的BoundingBoxOverlay模块
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.bounding_box_overlay import BoundingBoxOverlay


class SimplifiedOCRIntegrator:
    """简化的OCR集成器，使用新的BoundingBoxOverlay模块"""
    
    def __init__(self):
        # 使用新的边界框覆盖层模块
        self._bbox_overlay = BoundingBoxOverlay()
        
        # 模拟的检测结果
        self._current_detections = []
        
        # 设置回调
        self._bbox_overlay.SetInfoCallback(self._OnInfo)
        self._bbox_overlay.SetErrorCallback(self._OnError)
    
    def _OnInfo(self, message):
        print(f"[边界框] {message}")
    
    def _OnError(self, message):
        print(f"[错误] {message}")
    
    def MockDetectText(self):
        """模拟文字检测（替代真实的OCR）"""
        # 模拟检测到的文字区域
        self._current_detections = [
            {
                'text': '开始游戏',
                'bbox': (100, 100, 120, 40),
                'confidence': 0.95,
                'center_x': 160,
                'center_y': 120
            },
            {
                'text': '设置选项',
                'bbox': (250, 150, 100, 35),
                'confidence': 0.88,
                'center_x': 300,
                'center_y': 167
            },
            {
                'text': '退出程序',
                'bbox': (400, 200, 80, 30),
                'confidence': 0.92,
                'center_x': 440,
                'center_y': 215
            },
            {
                'text': '帮助文档',
                'bbox': (150, 250, 90, 25),
                'confidence': 0.85,
                'center_x': 195,
                'center_y': 262
            }
        ]
        
        print(f"[检测] 模拟检测到 {len(self._current_detections)} 个文字区域")
        return len(self._current_detections) > 0
    
    def ShowTextBoundingBoxes(self, duration=None, box_color='red', box_width=2):
        """显示文字边界框 - 现在使用新模块"""
        if not self._current_detections:
            self._OnError("没有检测结果，请先执行文字检测")
            return False
        
        # 使用新的BoundingBoxOverlay模块
        return self._bbox_overlay.ShowBoundingBoxes(
            self._current_detections, 
            duration=duration,
            box_color=box_color,
            box_width=box_width
        )
    
    def HideBoundingBoxes(self):
        """隐藏边界框 - 使用新模块"""
        self._bbox_overlay.HideBoundingBoxes()
    
    def AnalyzeAndShowBoxes(self, duration=3.0):
        """分析并显示边界框的完整流程"""
        print("\n=== 开始分析流程 ===")
        
        # 1. 模拟检测文字
        if not self.MockDetectText():
            return False
        
        # 2. 显示边界框
        print("[流程] 显示文字边界框...")
        success = self.ShowTextBoundingBoxes(duration=duration, box_color='blue', box_width=3)
        
        if success:
            print(f"[流程] 边界框将显示 {duration} 秒")
            if duration:
                time.sleep(duration)
        
        return success
    
    def GetDetectionCount(self):
        """获取检测结果数量"""
        return len(self._current_detections)
    
    def GetCurrentDetections(self):
        """获取当前检测结果"""
        return self._current_detections.copy()


def demo_migration_example():
    """演示迁移示例"""
    print("=== 演示：迁移到新边界框模块 ===")
    print("展示如何将现有代码改为使用新的BoundingBoxOverlay模块")
    
    integrator = SimplifiedOCRIntegrator()
    
    try:
        # 演示1: 基本流程
        print("\n演示1: 基本检测和边界框显示")
        success = integrator.AnalyzeAndShowBoxes(duration=3.0)
        if success:
            print("✓ 使用新模块成功显示边界框")
        
        # 演示2: 自定义样式
        print("\n演示2: 自定义边界框样式")
        if integrator.MockDetectText():
            integrator.ShowTextBoundingBoxes(duration=2.0, box_color='green', box_width=4)
            print("✓ 绿色粗边界框显示2秒")
            time.sleep(2)
        
        # 演示3: 永久显示然后手动隐藏
        print("\n演示3: 永久显示和手动控制")
        if integrator.MockDetectText():
            integrator.ShowTextBoundingBoxes(duration=None, box_color='red')
            print("✓ 红色边界框永久显示")
            print("等待2秒后手动隐藏...")
            time.sleep(2)
            integrator.HideBoundingBoxes()
            print("✓ 边界框已手动隐藏")
        
        print("\n=== 迁移演示完成 ===")
        print("新模块的优势:")
        print("- 代码更简洁，职责单一")
        print("- 可配置的颜色和样式")
        print("- 更好的错误处理")
        print("- 易于在多个模块间复用")
        
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
    finally:
        integrator.HideBoundingBoxes()


def demo_before_and_after():
    """演示迁移前后的代码对比"""
    print("\n=== 代码迁移对比 ===")
    
    print("迁移前 (原始代码):")
    print("- 需要自己管理tkinter窗口")
    print("- 需要手写_create_bbox_window方法")
    print("- 需要管理_bbox_windows列表") 
    print("- 需要处理窗口创建和销毁的细节")
    
    print("\n迁移后 (使用新模块):")
    print("- 只需导入BoundingBoxOverlay")
    print("- 调用ShowBoundingBoxes()方法")
    print("- 调用HideBoundingBoxes()方法")
    print("- 所有细节都被封装了")
    
    print("\n代码行数对比:")
    print("- 原始实现: ~100行 (包含窗口管理逻辑)")
    print("- 使用新模块: ~10行 (只需要调用API)")
    
    print("\n可维护性:")
    print("- 原始: 每个模块都要重复实现边界框逻辑")
    print("- 新模块: 集中维护，一处修改，处处受益")


if __name__ == "__main__":
    print("新边界框模块使用示例")
    print("展示如何迁移现有代码以使用新的BoundingBoxOverlay模块")
    
    try:
        demo_migration_example()
        demo_before_and_after()
        
        print("\n🎉 新模块已成功提取并可以使用！")
        print("\n使用方法:")
        print("from src.utils.bounding_box_overlay import BoundingBoxOverlay")
        print("bbox_overlay = BoundingBoxOverlay()")
        print("bbox_overlay.ShowBoundingBoxes(detections)")
        
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"\n演示过程中发生错误: {e}")