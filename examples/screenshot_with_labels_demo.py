#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图与标签结合功能演示脚本
展示如何在截图的同时显示标签
"""

import sys
import os
import signal
import time
from contextlib import contextmanager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.screenshot import ScreenshotTool
from src.utils.screen_labeler import ScreenLabeler

# 全局中断标志
_interrupted = False

@contextmanager
def keyboard_interrupt_handler():
    """键盘中断处理上下文管理器"""
    global _interrupted
    _interrupted = False
    
    def signal_handler(signum, frame):
        global _interrupted
        _interrupted = True
        print("\n[中断] 检测到键盘中断，正在安全退出...")
        
    old_handler = signal.signal(signal.SIGINT, signal_handler)
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, old_handler)

def demo_screenshot_with_labels():
    """演示截图与标签结合功能"""
    print("=== 截图与标签结合演示 ===")
    print("提示: 按 Ctrl+C 可以随时安全退出")
    
    # 创建工具实例
    screenshot_tool = ScreenshotTool()
    labeler = ScreenLabeler()
    
    # 设置回调
    screenshot_tool.set_screenshot_callback(lambda msg: print(f"[截图] {msg}"))
    screenshot_tool.set_error_callback(lambda msg: print(f"[错误] {msg}"))
    labeler.SetCallback(lambda msg: print(f"[标签] {msg}"))
    labeler.SetErrorCallback(lambda msg: print(f"[错误] {msg}"))
    
    with keyboard_interrupt_handler():
        try:
            print("\n1. 显示测试标签并截图")
            print("将显示6个测试标签，持续3秒，同时进行截图...")
            
            if _interrupted:
                return
                
            # 显示标签
            labeler.ShowTestLabels(count=6, duration=3.0)
            
            # 等待0.5秒让标签完全显示
            time.sleep(0.5)
            
            if _interrupted:
                return
                
            # 截图
            screenshot_path = screenshot_tool.capture_and_save_full_screen("labeled_screen.png")
            print(f"带标签的截图已保存: {screenshot_path}")
            
            # 等待标签消失
            time.sleep(3)
            
            if _interrupted:
                return
                
            print("\n2. 自定义元素标签与区域截图")
            
            # 创建自定义元素
            custom_elements = [
                {'center_x': 200, 'center_y': 150, 'text': '区域1', 'type': 'button'},
                {'center_x': 400, 'center_y': 200, 'text': '区域2', 'type': 'button'},
                {'center_x': 600, 'center_y': 250, 'text': '区域3', 'type': 'text'},
                {'center_x': 300, 'center_y': 350, 'text': '区域4', 'type': 'text'},
            ]
            
            print("显示4个自定义标签并截图相关区域...")
            
            # 显示自定义标签
            success = labeler.ShowLabels(custom_elements, duration=4.0)
            
            if success and not _interrupted:
                # 等待标签显示
                time.sleep(0.5)
                
                # 截图包含所有标签的区域
                region_screenshot = screenshot_tool.capture_and_save_region(
                    100, 100, 600, 300, "labeled_regions.png"
                )
                print(f"标签区域截图已保存: {region_screenshot}")
                
                # 等待标签消失
                time.sleep(4)
            
            if _interrupted:
                return
                
            print("\n3. 快速标签切换演示")
            print("将快速显示不同位置的标签并截图...")
            
            positions = [
                (100, 100), (300, 150), (500, 200), (200, 300), (400, 350)
            ]
            
            for i, (x, y) in enumerate(positions):
                if _interrupted:
                    break
                    
                # 创建单个标签元素
                element = [{'center_x': x, 'center_y': y, 'text': f'快速{i+1}', 'type': 'button'}]
                
                print(f"位置 {i+1}: ({x}, {y})")
                
                # 显示标签
                labeler.ShowLabels(element, duration=1.0)
                time.sleep(0.2)  # 让标签显示
                
                # 截图该区域
                screenshot_path = screenshot_tool.capture_and_save_region(
                    x-50, y-50, 100, 100, f"quick_label_{i+1}.png"
                )
                print(f"  截图已保存: {screenshot_path}")
                
                time.sleep(0.8)  # 等待标签消失
                
            print("\n=== 演示完成 ===")
            print("生成的截图文件:")
            screenshots = screenshot_tool.get_all_screenshots()
            for path in screenshots[-8:]:  # 显示最新的8个截图
                info = screenshot_tool.get_screenshot_info(path)
                if info:
                    print(f"  - {info['filename']} ({info['width']}x{info['height']})")
                    
        except KeyboardInterrupt:
            print("\n[中断] 演示被用户中断")
        except Exception as e:
            print(f"演示过程中发生错误: {e}")
        finally:
            # 确保清理标签
            try:
                labeler.HideLabels()
            except:
                pass

def interactive_screenshot_labels():
    """交互式截图标签演示"""
    print("\n=== 交互式截图标签演示 ===")
    print("提示: 在任何输入提示处，按 Ctrl+C 可以安全退出")
    
    screenshot_tool = ScreenshotTool()
    labeler = ScreenLabeler()
    
    # 设置回调
    screenshot_tool.set_screenshot_callback(lambda msg: print(f"[截图] {msg}"))
    labeler.SetCallback(lambda msg: print(f"[标签] {msg}"))
    
    with keyboard_interrupt_handler():
        while not _interrupted:
            try:
                print("\n请选择操作:")
                print("1. 显示测试标签并截图")
                print("2. 自定义位置标签并截图")
                print("3. 快速连续标签截图")
                print("4. 仅截图（无标签）")
                print("0. 退出")
                
                choice = input("请输入选择 (0-4): ").strip()
                
                if _interrupted:
                    break
                    
                if choice == '1':
                    count = int(input("输入标签数量 (1-20): ") or "6")
                    duration = float(input("输入显示时长 (秒): ") or "3.0")
                    
                    print(f"显示{count}个标签，持续{duration}秒...")
                    labeler.ShowTestLabels(count=count, duration=duration)
                    time.sleep(0.5)
                    
                    path = screenshot_tool.capture_and_save_full_screen()
                    print(f"截图已保存: {path}")
                    
                elif choice == '2':
                    x = int(input("输入X坐标: ") or "300")
                    y = int(input("输入Y坐标: ") or "200")
                    text = input("输入标签文本: ") or "自定义"
                    
                    element = [{'center_x': x, 'center_y': y, 'text': text, 'type': 'button'}]
                    labeler.ShowLabels(element, duration=2.0)
                    time.sleep(0.5)
                    
                    path = screenshot_tool.capture_and_save_region(x-100, y-100, 200, 200)
                    print(f"区域截图已保存: {path}")
                    
                elif choice == '3':
                    print("快速连续标签截图（5次）...")
                    for i in range(5):
                        if _interrupted:
                            break
                        x, y = 100 + i*100, 100 + i*50
                        element = [{'center_x': x, 'center_y': y, 'text': f'快{i+1}', 'type': 'text'}]
                        
                        labeler.ShowLabels(element, duration=0.8)
                        time.sleep(0.2)
                        path = screenshot_tool.capture_and_save_region(x-30, y-30, 60, 60, f"fast_{i+1}.png")
                        print(f"  {i+1}/5 完成")
                        
                elif choice == '4':
                    path = screenshot_tool.capture_and_save_full_screen()
                    print(f"截图已保存: {path}")
                    
                elif choice == '0':
                    print("退出演示")
                    break
                    
                else:
                    print("无效选择，请重新输入")
                    
            except KeyboardInterrupt:
                print("\n[中断] 演示被用户中断")
                break
            except ValueError:
                print("输入无效，请重新输入")
            except Exception as e:
                print(f"操作失败: {e}")
                
        if _interrupted:
            print("\n[中断] 交互式演示已安全退出")

if __name__ == "__main__":
    print("截图与标签结合演示程序")
    print("确保已安装所需依赖并且标签功能正常工作")
    print("提示: 按 Ctrl+C 可以随时安全退出")
    
    try:
        demo_type = input("\n选择演示类型 (1=自动演示, 2=交互式演示): ").strip()
        
        if demo_type == '1':
            demo_screenshot_with_labels()
        elif demo_type == '2':
            interactive_screenshot_labels()
        else:
            print("默认运行自动演示...")
            demo_screenshot_with_labels()
            
    except KeyboardInterrupt:
        print("\n[中断] 程序已安全退出")
    except Exception as e:
        print(f"\n程序执行出错: {e}")