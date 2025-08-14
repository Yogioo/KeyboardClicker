#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多屏幕功能测试脚本
用于验证多屏幕支持是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.clicker import ClickerTool
import time

def test_screen_detection():
    """测试屏幕检测功能"""
    print("=== 多屏幕功能测试 ===")
    
    # 创建点击工具实例
    clicker = ClickerTool()
    
    # 获取屏幕信息
    screen_info = clicker.get_screen_info()
    print(f"检测到的屏幕信息:")
    print(f"  总宽度: {screen_info['total_width']}px")
    print(f"  总高度: {screen_info['total_height']}px")
    print(f"  屏幕边界: {screen_info['bounds']}")
    print(f"  估算屏幕数量: {screen_info['screen_count']}")
    
    # 测试当前鼠标位置
    print("\n=== 鼠标位置测试 ===")
    try:
        x, y = clicker.get_current_mouse_position()
        print(f"当前鼠标位置: ({x}, {y})")
        
        # 验证坐标有效性
        is_valid = clicker.validate_coordinates(x, y)
        print(f"坐标有效性: {'有效' if is_valid else '无效'}")
        
    except Exception as e:
        print(f"获取鼠标位置失败: {e}")
    
    # 测试不同坐标的有效性
    print("\n=== 坐标验证测试 ===")
    test_coords = [
        (0, 0),
        (100, 100),
        (1920, 0),  # 可能在第二个屏幕
        (3840, 0),  # 可能在第三个屏幕
        (-100, 100),  # 负坐标
        (screen_info['total_width'] - 1, screen_info['total_height'] - 1),  # 边界坐标
        (screen_info['total_width'], screen_info['total_height']),  # 超出边界
    ]
    
    for x, y in test_coords:
        is_valid = clicker.validate_coordinates(x, y)
        status = "✓ 有效" if is_valid else "✗ 无效"
        print(f"  坐标 ({x:5d}, {y:5d}): {status}")
    
    # 测试屏幕信息刷新
    print("\n=== 屏幕信息刷新测试 ===")
    print("刷新前的屏幕信息:")
    print(f"  总尺寸: {clicker.total_width}x{clicker.total_height}")
    
    clicker.refresh_screen_info()
    print("刷新后的屏幕信息:")
    print(f"  总尺寸: {clicker.total_width}x{clicker.total_height}")
    
    print("\n=== 测试完成 ===")
    print("如果您使用多屏幕环境，请验证:")
    print("1. 总宽度应该大于单个屏幕宽度")
    print("2. 屏幕数量估算应该正确")
    print("3. 鼠标在不同屏幕上的坐标都应该被正确识别")
    
if __name__ == "__main__":
    test_screen_detection()
    input("\n按回车键退出...")