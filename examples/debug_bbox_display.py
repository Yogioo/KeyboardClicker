#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试边界框显示问题
"""

import sys
import os
import time
import tkinter as tk
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.bounding_box_overlay import BoundingBoxOverlay


def test_basic_tkinter():
    """测试基本的tkinter窗口显示"""
    print("=== 测试基本tkinter窗口 ===")
    
    try:
        # 创建一个简单的测试窗口
        root = tk.Tk()
        root.title("测试窗口")
        root.geometry("300x200+100+100")
        root.configure(bg='red')
        
        print("创建了红色测试窗口，应该能看到...")
        print("窗口将显示3秒")
        
        # 强制更新和显示
        root.update()
        root.deiconify()  # 确保窗口显示
        root.lift()       # 提升到前台
        root.focus_force() # 强制获取焦点
        
        # 等待3秒
        start_time = time.time()
        while time.time() - start_time < 3:
            root.update()
            time.sleep(0.1)
        
        root.destroy()
        print("基本tkinter测试完成")
        return True
        
    except Exception as e:
        print(f"基本tkinter测试失败: {e}")
        return False


def test_transparent_window():
    """测试透明窗口"""
    print("\n=== 测试透明窗口 ===")
    
    try:
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        # 创建透明窗口
        window = tk.Toplevel(root)
        window.overrideredirect(True)
        window.attributes('-topmost', True)
        window.geometry("200x100+200+200")
        
        # 尝试设置透明度
        try:
            window.attributes('-alpha', 0.8)
            print("透明度设置成功")
        except:
            print("透明度设置失败")
        
        # 创建红色背景
        window.configure(bg='red')
        
        print("创建了透明红色窗口，应该能看到...")
        print("窗口将显示3秒")
        
        # 强制显示
        window.update()
        window.deiconify()
        window.lift()
        
        # 等待3秒
        start_time = time.time()
        while time.time() - start_time < 3:
            root.update()
            time.sleep(0.1)
        
        root.destroy()
        print("透明窗口测试完成")
        return True
        
    except Exception as e:
        print(f"透明窗口测试失败: {e}")
        return False


def test_canvas_rectangle():
    """测试画布矩形绘制"""
    print("\n=== 测试画布矩形 ===")
    
    try:
        root = tk.Tk()
        root.withdraw()
        
        window = tk.Toplevel(root)
        window.overrideredirect(True)
        window.attributes('-topmost', True)
        window.geometry("200x100+300+300")
        
        # 创建画布
        canvas = tk.Canvas(window, width=200, height=100, bg='black')
        canvas.pack()
        
        # 绘制红色矩形
        canvas.create_rectangle(10, 10, 190, 90, outline='red', width=3, fill='')
        
        print("创建了带红色矩形的窗口...")
        print("窗口将显示3秒")
        
        # 强制显示
        window.update()
        window.deiconify()
        window.lift()
        
        # 等待3秒
        start_time = time.time()
        while time.time() - start_time < 3:
            root.update()
            time.sleep(0.1)
        
        root.destroy()
        print("画布矩形测试完成")
        return True
        
    except Exception as e:
        print(f"画布矩形测试失败: {e}")
        return False


def test_simplified_bbox():
    """测试简化版边界框"""
    print("\n=== 测试简化版边界框 ===")
    
    try:
        root = tk.Tk()
        root.withdraw()
        
        # 创建简单的边界框窗口
        bbox_window = tk.Toplevel(root)
        bbox_window.overrideredirect(True)
        bbox_window.attributes('-topmost', True)
        bbox_window.geometry("150x80+400+150")
        
        # 设置红色背景，看是否能看到
        bbox_window.configure(bg='red')
        
        print("创建了简化版边界框窗口（红色背景）...")
        print("如果能看到红色矩形，说明窗口显示正常")
        print("窗口将显示5秒")
        
        # 强制显示和更新
        bbox_window.update()
        bbox_window.deiconify()
        bbox_window.lift()
        bbox_window.focus_force()
        
        # 持续更新5秒
        start_time = time.time()
        while time.time() - start_time < 5:
            root.update()
            bbox_window.update()
            time.sleep(0.1)
        
        root.destroy()
        print("简化版边界框测试完成")
        return True
        
    except Exception as e:
        print(f"简化版边界框测试失败: {e}")
        return False


def test_bbox_overlay_with_debug():
    """测试BoundingBoxOverlay模块并输出调试信息"""
    print("\n=== 测试BoundingBoxOverlay模块（调试版） ===")
    
    bbox_overlay = BoundingBoxOverlay()
    
    # 设置调试回调
    def debug_info(msg):
        print(f"[调试-INFO] {msg}")
    
    def debug_error(msg):
        print(f"[调试-ERROR] {msg}")
    
    bbox_overlay.SetInfoCallback(debug_info)
    bbox_overlay.SetErrorCallback(debug_error)
    
    try:
        # 创建测试检测结果
        detections = [
            {'bbox': (500, 100, 150, 60), 'text': '测试区域1'},
        ]
        
        print("尝试显示边界框...")
        success = bbox_overlay.ShowBoundingBoxes(detections, duration=None)
        
        if success:
            print(f"边界框创建成功！活跃窗口数: {bbox_overlay.GetActiveBoxCount()}")
            print("请检查屏幕上是否有红色边界框出现")
            print("按Enter继续...")
            input()
        else:
            print("边界框创建失败")
        
        return success
        
    except Exception as e:
        print(f"BoundingBoxOverlay测试失败: {e}")
        return False
    finally:
        bbox_overlay.HideBoundingBoxes()


def test_with_manual_mainloop():
    """测试手动mainloop"""
    print("\n=== 测试手动mainloop ===")
    
    try:
        root = tk.Tk()
        root.withdraw()
        
        window = tk.Toplevel(root)
        window.overrideredirect(True)
        window.attributes('-topmost', True)
        window.geometry("200x100+100+100")
        window.configure(bg='green')
        
        print("创建绿色窗口，使用mainloop显示...")
        print("窗口应该会一直显示，按Ctrl+C退出")
        
        window.update()
        window.deiconify()
        window.lift()
        
        # 使用mainloop
        try:
            root.mainloop()
        except KeyboardInterrupt:
            print("用户中断")
        
        return True
        
    except Exception as e:
        print(f"mainloop测试失败: {e}")
        return False


if __name__ == "__main__":
    print("边界框显示问题诊断程序")
    print("这个程序将逐步测试各种显示方式，帮助找出问题所在")
    
    try:
        # 逐步测试
        tests = [
            ("基本tkinter窗口", test_basic_tkinter),
            ("透明窗口", test_transparent_window), 
            ("画布矩形", test_canvas_rectangle),
            ("简化版边界框", test_simplified_bbox),
            ("BoundingBoxOverlay模块", test_bbox_overlay_with_debug)
        ]
        
        for test_name, test_func in tests:
            print(f"\n{'='*50}")
            print(f"开始测试: {test_name}")
            print('='*50)
            
            result = test_func()
            print(f"测试结果: {'通过' if result else '失败'}")
            
            if not result:
                print("测试失败，可能需要检查这个环节")
                break
            
            # 询问是否继续
            continue_test = input(f"\n{test_name} 测试完成，是否继续下一个测试？(y/n): ").strip().lower()
            if continue_test != 'y':
                break
        
        print("\n=== 诊断建议 ===")
        print("如果所有测试都通过但仍然看不到边界框，可能的原因：")
        print("1. 窗口被其他程序遮挡")
        print("2. 窗口显示在屏幕可视区域之外")
        print("3. Windows系统的透明度设置问题")
        print("4. 需要管理员权限才能在其他窗口上方显示")
        
        # 最后测试手动mainloop
        final_test = input("\n是否进行最终测试（手动mainloop）？(y/n): ").strip().lower()
        if final_test == 'y':
            test_with_manual_mainloop()
        
    except KeyboardInterrupt:
        print("\n诊断被用户中断")
    except Exception as e:
        print(f"\n诊断过程中发生错误: {e}")