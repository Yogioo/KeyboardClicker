#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图功能演示脚本
展示如何使用ScreenshotTool类的各种功能
"""

import sys
import os
import signal
import threading
from contextlib import contextmanager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.screenshot import ScreenshotTool
import time

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

def countdown_with_interrupt(seconds, message=""):
    """可中断的倒计时"""
    global _interrupted
    for i in range(seconds, 0, -1):
        if _interrupted:
            print("\n操作已取消")
            return False
        print(f"{message}{i}秒...", end='\r')
        time.sleep(1)
    print(f"{message}开始执行！")
    return True

def demo_screenshot_tool():
    """演示截图工具的各种功能"""
    print("=== 截图工具演示（优化版）===")
    print("提示: 任何时候按 Ctrl+C 可以安全退出")
    
    # 创建截图工具实例
    screenshot_tool = ScreenshotTool()
    
    # 设置回调函数
    def on_screenshot(message):
        print(f"[截图] {message}")
        
    def on_error(message):
        print(f"[错误] {message}")
        
    screenshot_tool.set_screenshot_callback(on_screenshot)
    screenshot_tool.set_error_callback(on_error)
    
    with keyboard_interrupt_handler():
        try:
            # 1. 获取屏幕尺寸
            print("\n1. 获取屏幕尺寸")
            width, height = screenshot_tool.get_screen_size()
            print(f"屏幕尺寸: {width} x {height}")
            
            if _interrupted:
                return
            
            # 2. 全屏截图并保存
            print("\n2. 全屏截图")
            if countdown_with_interrupt(2, "全屏截图倒计时: "):
                full_screenshot_path = screenshot_tool.capture_and_save_full_screen()
                print(f"全屏截图已保存到: {full_screenshot_path}")
            
            if _interrupted:
                return
                
            # 3. 区域截图（屏幕左上角 400x300 区域）
            print("\n3. 区域截图")
            if countdown_with_interrupt(1, "区域截图倒计时: "):
                region_screenshot_path = screenshot_tool.capture_and_save_region(
                    0, 0, 400, 300, "region_demo.png"
                )
                print(f"区域截图已保存到: {region_screenshot_path}")
            
            if _interrupted:
                return
                
            # 4. 获取所有截图文件
            print("\n4. 获取所有截图文件")
            all_screenshots = screenshot_tool.get_all_screenshots()
            print(f"找到 {len(all_screenshots)} 个截图文件:")
            for i, screenshot_path in enumerate(all_screenshots[:5], 1):  # 只显示前5个
                if _interrupted:
                    return
                info = screenshot_tool.get_screenshot_info(screenshot_path)
                if info:
                    print(f"  {i}. {info['filename']} - {info['width']}x{info['height']} - {info['size_bytes']} bytes")
            
            if _interrupted:
                return
                
            # 5. 演示自定义保存路径
            print("\n5. 自定义保存路径")
            custom_path = "assets/screenshots"
            screenshot_tool.set_default_save_path(custom_path)
            
            custom_screenshot_path = screenshot_tool.capture_and_save_region(
                100, 100, 200, 200, "custom_location.png"
            )
            print(f"自定义路径截图已保存到: {custom_screenshot_path}")
            
            print("\n=== 演示完成 ===")
            print(f"默认截图保存目录: {screenshot_tool.get_default_save_path()}")
            print("你可以查看生成的截图文件！")
            
        except KeyboardInterrupt:
            print("\n[中断] 演示被用户中断")
        except Exception as e:
            print(f"演示过程中发生错误: {e}")

def interactive_demo():
    """交互式演示（优化版）"""
    print("\n=== 交互式截图演示（优化版）===")
    print("提示: 在任何输入提示处，按 Ctrl+C 可以安全退出")
    
    screenshot_tool = ScreenshotTool()
    
    # 设置回调
    screenshot_tool.set_screenshot_callback(lambda msg: print(f"[截图] {msg}"))
    screenshot_tool.set_error_callback(lambda msg: print(f"[错误] {msg}"))
    
    with keyboard_interrupt_handler():
        while not _interrupted:
            try:
                print("\n请选择操作:")
                print("1. 即时全屏截图（无延迟）")
                print("2. 即时区域截图（屏幕中心 300x300）")
                print("3. 查看所有截图")
                print("4. 获取屏幕尺寸")
                print("5. 快速连续截图测试")
                print("0. 退出")
                
                choice = input("请输入选择 (0-5): ").strip()
                
                if _interrupted:
                    break
                    
                if choice == '1':
                    print("正在进行全屏截图...")
                    path = screenshot_tool.capture_and_save_full_screen()
                    print(f"截图已保存: {path}")
                    
                elif choice == '2':
                    width, height = screenshot_tool.get_screen_size()
                    x = (width - 300) // 2
                    y = (height - 300) // 2
                    print(f"正在截取屏幕中心区域 ({x}, {y}, 300, 300)...")
                    path = screenshot_tool.capture_and_save_region(x, y, 300, 300)
                    print(f"区域截图已保存: {path}")
                    
                elif choice == '3':
                    screenshots = screenshot_tool.get_all_screenshots()
                    if screenshots:
                        print(f"\n找到 {len(screenshots)} 个截图:")
                        for i, path in enumerate(screenshots[:10], 1):
                            if _interrupted:
                                break
                            info = screenshot_tool.get_screenshot_info(path)
                            if info:
                                print(f"  {i}. {info['filename']} - {info['width']}x{info['height']} ({info['size_bytes']} bytes)")
                    else:
                        print("没有找到截图文件")
                        
                elif choice == '4':
                    width, height = screenshot_tool.get_screen_size()
                    print(f"屏幕尺寸: {width} x {height}")
                    
                elif choice == '5':
                    print("快速连续截图测试（5张，间隔0.5秒）")
                    print("开始测试...")
                    start_time = time.time()
                    for i in range(5):
                        if _interrupted:
                            break
                        print(f"截图 {i+1}/5", end=' ')
                        path = screenshot_tool.capture_and_save_region(100 + i*50, 100 + i*50, 200, 200, f"speed_test_{i+1}.png")
                        print("✓")
                        if i < 4:  # 最后一张不等待
                            time.sleep(0.5)
                    end_time = time.time()
                    if not _interrupted:
                        print(f"测试完成！总耗时: {end_time - start_time:.2f}秒")
                    
                elif choice == '0':
                    print("退出演示")
                    break
                    
                else:
                    print("无效选择，请重新输入")
                    
            except KeyboardInterrupt:
                print("\n[中断] 演示被用户中断")
                break
            except Exception as e:
                print(f"操作失败: {e}")
                
        if _interrupted:
            print("\n[中断] 交互式演示已安全退出")

if __name__ == "__main__":
    print("截图工具演示程序（优化版）")
    print("请确保已安装所需依赖: pip install -r requirements.txt")
    print("提示: 按 Ctrl+C 可以随时安全退出")
    
    try:
        demo_type = input("\n选择演示类型 (1=自动演示, 2=交互式演示): ").strip()
        
        if demo_type == '1':
            demo_screenshot_tool()
        elif demo_type == '2':
            interactive_demo()
        else:
            print("默认运行自动演示...")
            demo_screenshot_tool()
            
    except KeyboardInterrupt:
        print("\n[中断] 程序已安全退出")
    except Exception as e:
        print(f"\n程序执行出错: {e}")