#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标签显示功能测试脚本
简单测试ScreenLabeler的标签生成和显示功能
"""

import sys
import time
from pathlib import Path

# 添加父目录到路径中，以便导入模块
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.screen_labeler import ScreenLabeler


def test_label_generation():
    """测试标签生成功能"""
    print("=== 标签生成测试 ===")
    
    labeler = ScreenLabeler()
    
    # 测试生成不同数量的标签
    test_counts = [1, 5, 26, 27, 52, 100, 702]  # 702 = 26*26 + 26
    
    for count in test_counts:
        labels = labeler.TestLabelGeneration(count)
        if labels:
            print(f"\n生成{count}个标签:")
            if count <= 10:
                # 小数量全部显示
                print(f"  {', '.join(labels)}")
            else:
                # 大数量显示首尾
                print(f"  前5个: {', '.join(labels[:5])}")
                print(f"  后5个: {', '.join(labels[-5:])}")


def test_screen_display():
    """测试屏幕显示功能"""
    print("\n=== 屏幕显示测试 ===")
    
    labeler = ScreenLabeler()
    
    # 设置回调
    def on_success(msg):
        print(f"[成功] {msg}")
    
    def on_error(msg):
        print(f"[错误] {msg}")
    
    labeler.SetCallback(on_success)
    labeler.SetErrorCallback(on_error)
    
    print("将显示6个测试标签，持续3秒...")
    print("标签将以3x2网格形式显示在屏幕左上角")
    
    try:
        labeler.ShowTestLabels(count=6, duration=3.0)
        time.sleep(4)  # 等待显示完成
        print("测试完成")
        
    except KeyboardInterrupt:
        print("\n用户中断")
        labeler.HideLabels()


def test_custom_elements():
    """测试自定义元素标签显示"""
    print("\n=== 自定义元素测试 ===")
    
    labeler = ScreenLabeler()
    
    # 设置回调
    labeler.SetCallback(lambda msg: print(f"[标签] {msg}"))
    labeler.SetErrorCallback(lambda msg: print(f"[错误] {msg}"))
    
    # 创建自定义元素
    custom_elements = [
        {'center_x': 200, 'center_y': 100, 'text': '标题', 'type': 'text'},
        {'center_x': 300, 'center_y': 150, 'text': '按钮1', 'type': 'button'},
        {'center_x': 400, 'center_y': 200, 'text': '按钮2', 'type': 'button'},
        {'center_x': 500, 'center_y': 250, 'text': '链接', 'type': 'text'},
    ]
    
    print("将为4个自定义元素显示标签...")
    print("标签映射:")
    for i, elem in enumerate(custom_elements):
        label = chr(ord('A') + i)
        print(f"  {label}: {elem['type']} '{elem['text']}' 位置:({elem['center_x']}, {elem['center_y']})")
    
    try:
        success = labeler.ShowLabels(custom_elements, duration=4.0)
        if success:
            print("\n标签显示4秒后自动消失...")
            time.sleep(5)
            print("自定义元素测试完成")
        else:
            print("标签显示失败")
            
    except KeyboardInterrupt:
        print("\n用户中断")
        labeler.HideLabels()


def main():
    """主测试函数"""
    print("ScreenLabeler 标签显示功能测试")
    print("=" * 40)
    
    print("\n注意事项:")
    print("1. 确保已安装所有依赖包")
    print("2. 标签将显示在屏幕上方，请注意观察")
    print("3. 可以按 Ctrl+C 提前结束测试")
    
    input("\n按 Enter 键开始测试...")
    
    try:
        # 运行测试
        test_label_generation()
        
        input("\n按 Enter 键继续屏幕显示测试...")
        test_screen_display()
        
        input("\n按 Enter 键继续自定义元素测试...")
        test_custom_elements()
        
        print("\n" + "=" * 40)
        print("所有测试完成！")
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")


if __name__ == "__main__":
    main()