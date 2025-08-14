#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
边界框覆盖层测试程序
测试新提取的BoundingBoxOverlay模块功能
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.bounding_box_overlay import BoundingBoxOverlay


def test_basic_functionality():
    """测试基本功能"""
    print("=== 测试边界框覆盖层基本功能 ===")
    
    # 创建边界框工具
    bbox_overlay = BoundingBoxOverlay()
    
    # 设置回调函数
    def info_callback(msg):
        print(f"[信息] {msg}")
    
    def error_callback(msg):
        print(f"[错误] {msg}")
    
    bbox_overlay.SetInfoCallback(info_callback)
    bbox_overlay.SetErrorCallback(error_callback)
    
    try:
        # 测试1: 显示检测结果的边界框
        print("\n测试1: 显示检测结果边界框")
        detections = [
            {'bbox': (100, 100, 200, 50), 'text': '测试文字1', 'confidence': 0.95},
            {'bbox': (350, 150, 180, 40), 'text': '测试文字2', 'confidence': 0.88},
            {'bbox': (100, 250, 150, 35), 'text': '测试文字3', 'confidence': 0.92}
        ]
        
        success = bbox_overlay.ShowBoundingBoxes(detections, duration=3.0)
        print(f"显示结果: {'成功' if success else '失败'}")
        if success:
            print(f"当前显示边界框数量: {bbox_overlay.GetActiveBoxCount()}")
            print("边界框将显示3秒...")
            time.sleep(3)
        
        # 测试2: 从坐标列表显示
        print("\n测试2: 从坐标列表显示边界框")
        coords = [
            (500, 100, 120, 30),
            (500, 150, 100, 25),
            (500, 200, 140, 35)
        ]
        
        success = bbox_overlay.ShowBoundingBoxesFromCoords(coords, duration=2.5, box_color='blue', box_width=3)
        print(f"显示结果: {'成功' if success else '失败'}")
        if success:
            print("蓝色边界框将显示2.5秒...")
            time.sleep(2.5)
        
        # 测试3: 自定义单个边界框
        print("\n测试3: 显示自定义边界框")
        success = bbox_overlay.ShowCustomBoundingBox(
            x=650, y=300, width=200, height=80, 
            duration=2.0, box_color='green', box_width=4, alpha=0.9
        )
        print(f"显示结果: {'成功' if success else '失败'}")
        if success:
            print("绿色粗边界框将显示2秒...")
            time.sleep(2)
        
        # 测试4: 永久显示（手动隐藏）
        print("\n测试4: 永久显示边界框")
        success = bbox_overlay.ShowCustomBoundingBox(
            x=200, y=400, width=300, height=60, 
            duration=None, box_color='red', box_width=2
        )
        print(f"显示结果: {'成功' if success else '失败'}")
        if success:
            print(f"永久显示，当前边界框数量: {bbox_overlay.GetActiveBoxCount()}")
            print("等待2秒后手动隐藏...")
            time.sleep(2)
            bbox_overlay.HideBoundingBoxes()
            print(f"隐藏后边界框数量: {bbox_overlay.GetActiveBoxCount()}")
        
        print("\n=== 所有测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
    finally:
        # 确保清理
        bbox_overlay.HideBoundingBoxes()


def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    bbox_overlay = BoundingBoxOverlay()
    
    # 测试空检测结果
    print("测试1: 空检测结果")
    result = bbox_overlay.ShowBoundingBoxes([])
    print(f"结果: {'符合预期' if not result else '不符合预期'}")
    
    # 测试缺少bbox字段的检测结果
    print("测试2: 缺少bbox字段")
    invalid_detections = [{'text': '无bbox字段'}]
    result = bbox_overlay.ShowBoundingBoxes(invalid_detections)
    print(f"结果: {'符合预期' if not result else '不符合预期'}")
    
    # 测试错误坐标格式
    print("测试3: 错误坐标格式")
    invalid_coords = [(100, 100)]  # 缺少width, height
    result = bbox_overlay.ShowBoundingBoxesFromCoords(invalid_coords)
    print(f"结果: {'符合预期' if not result else '不符合预期'}")
    
    print("错误处理测试完成")


def interactive_test():
    """交互式测试"""
    print("\n=== 交互式测试 ===")
    print("这个测试需要用户观察屏幕上的边界框显示效果")
    
    bbox_overlay = BoundingBoxOverlay()
    
    try:
        while True:
            print("\n请选择测试项目:")
            print("1. 显示红色边界框（屏幕左上角）")
            print("2. 显示蓝色边界框（屏幕中央）") 
            print("3. 显示绿色边界框（屏幕右下角）")
            print("4. 显示多个边界框")
            print("5. 隐藏所有边界框")
            print("0. 退出")
            
            choice = input("请输入选择 (0-5): ").strip()
            
            if choice == '1':
                bbox_overlay.ShowCustomBoundingBox(50, 50, 200, 100, box_color='red')
                print("红色边界框已显示")
            elif choice == '2':
                bbox_overlay.ShowCustomBoundingBox(400, 300, 250, 80, box_color='blue')
                print("蓝色边界框已显示")
            elif choice == '3':
                bbox_overlay.ShowCustomBoundingBox(600, 500, 180, 60, box_color='green')
                print("绿色边界框已显示")
            elif choice == '4':
                coords = [
                    (100, 200, 150, 40),
                    (300, 200, 150, 40), 
                    (500, 200, 150, 40)
                ]
                bbox_overlay.ShowBoundingBoxesFromCoords(coords, box_color='purple')
                print("多个紫色边界框已显示")
            elif choice == '5':
                bbox_overlay.HideBoundingBoxes()
                print("所有边界框已隐藏")
            elif choice == '0':
                break
            else:
                print("无效选择")
                
    except KeyboardInterrupt:
        print("\n用户中断测试")
    finally:
        bbox_overlay.HideBoundingBoxes()


if __name__ == "__main__":
    print("边界框覆盖层模块测试程序")
    print("用于测试新提取的BoundingBoxOverlay模块功能")
    
    try:
        test_type = input("\n选择测试类型 (1=基本功能测试, 2=错误处理测试, 3=交互式测试, a=全部): ").strip()
        
        if test_type == '1':
            test_basic_functionality()
        elif test_type == '2':
            test_error_handling()
        elif test_type == '3':
            interactive_test()
        elif test_type.lower() == 'a':
            test_basic_functionality()
            test_error_handling()
            print("\n如需进行交互式测试，请重新运行程序选择选项3")
        else:
            print("默认运行基本功能测试...")
            test_basic_functionality()
            
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试程序执行出错: {e}")