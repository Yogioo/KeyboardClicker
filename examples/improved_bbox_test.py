#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的边界框测试程序
确保边界框能够正确显示
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.bounding_box_overlay import BoundingBoxOverlay


def test_with_proper_timing():
    """确保有足够时间显示的测试"""
    print("=== 改进的边界框显示测试 ===")
    
    bbox_overlay = BoundingBoxOverlay()
    
    # 设置回调
    def info_callback(msg):
        print(f"[INFO] {msg}")
    
    def error_callback(msg):
        print(f"[ERROR] {msg}")
    
    bbox_overlay.SetInfoCallback(info_callback)
    bbox_overlay.SetErrorCallback(error_callback)
    
    try:
        print("\n测试1: 显示单个边界框")
        print("请注意屏幕左上角区域...")
        
        success = bbox_overlay.ShowCustomBoundingBox(
            x=100, y=100, width=200, height=80,
            duration=None,  # 永久显示
            box_color='red', 
            box_width=3
        )
        
        if success:
            print(f"边界框已创建，活跃数量: {bbox_overlay.GetActiveBoxCount()}")
            print("红色边界框应该在 (100,100) 位置显示")
            print("等待5秒...")
            
            # 手动更新循环，确保显示
            for i in range(50):  # 5秒，每0.1秒更新一次
                time.sleep(0.1)
                # 可以在这里添加额外的更新逻辑
            
            print("隐藏边界框...")
            bbox_overlay.HideBoundingBoxes()
        else:
            print("边界框创建失败")
        
        print("\n测试2: 显示多个边界框")
        print("请注意屏幕中间区域...")
        
        detections = [
            {'bbox': (300, 200, 150, 60), 'text': '区域1'},
            {'bbox': (500, 250, 120, 50), 'text': '区域2'},
            {'bbox': (350, 350, 180, 70), 'text': '区域3'}
        ]
        
        success = bbox_overlay.ShowBoundingBoxes(
            detections, 
            duration=None,
            box_color='blue',
            box_width=2
        )
        
        if success:
            print(f"多个边界框已创建，活跃数量: {bbox_overlay.GetActiveBoxCount()}")
            print("蓝色边界框应该在屏幕中间显示")
            print("等待5秒...")
            
            for i in range(50):
                time.sleep(0.1)
            
            print("隐藏所有边界框...")
            bbox_overlay.HideBoundingBoxes()
        else:
            print("多个边界框创建失败")
        
        print("\n测试3: 自动计时边界框")
        print("这个边界框将显示3秒后自动消失...")
        
        success = bbox_overlay.ShowCustomBoundingBox(
            x=600, y=100, width=180, height=90,
            duration=3.0,  # 3秒后自动隐藏
            box_color='green',
            box_width=4
        )
        
        if success:
            print("绿色边界框应该在右上角显示3秒")
            # 等待足够时间让自动隐藏生效
            time.sleep(4)
            print(f"3秒后活跃边界框数量: {bbox_overlay.GetActiveBoxCount()}")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
    finally:
        # 确保清理
        bbox_overlay.HideBoundingBoxes()


def interactive_timing_test():
    """交互式计时测试"""
    print("\n=== 交互式计时测试 ===")
    
    bbox_overlay = BoundingBoxOverlay()
    
    try:
        while True:
            print("\n选择测试:")
            print("1. 显示边界框并等待用户按键")
            print("2. 显示边界框固定时间")
            print("3. 连续显示多个边界框") 
            print("0. 退出")
            
            choice = input("请选择 (0-3): ").strip()
            
            if choice == '1':
                print("创建边界框...")
                bbox_overlay.ShowCustomBoundingBox(200, 200, 150, 75, box_color='red')
                print("边界框已显示，按Enter继续...")
                input()
                bbox_overlay.HideBoundingBoxes()
                
            elif choice == '2':
                duration = float(input("显示多少秒? ") or "3")
                print(f"边界框将显示{duration}秒...")
                bbox_overlay.ShowCustomBoundingBox(300, 300, 100, 50, duration=duration, box_color='blue')
                time.sleep(duration + 0.5)  # 多等0.5秒确保清理
                
            elif choice == '3':
                coords = [(100, 100, 80, 40), (250, 150, 90, 45), (400, 200, 100, 50)]
                print("显示3个边界框...")
                bbox_overlay.ShowBoundingBoxesFromCoords(coords, box_color='green')
                print("边界框已显示，按Enter继续...")
                input()
                bbox_overlay.HideBoundingBoxes()
                
            elif choice == '0':
                break
            else:
                print("无效选择")
                
    except KeyboardInterrupt:
        print("\n用户中断测试")
    finally:
        bbox_overlay.HideBoundingBoxes()


if __name__ == "__main__":
    print("改进的边界框显示测试程序")
    print("这个版本确保有足够的时间让边界框显示")
    
    try:
        test_type = input("\n选择测试类型 (1=自动测试, 2=交互式测试): ").strip()
        
        if test_type == '2':
            interactive_timing_test()
        else:
            test_with_proper_timing()
            
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试程序执行出错: {e}")