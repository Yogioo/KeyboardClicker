#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速视觉识别演示程序
展示基于计算机视觉的快速UI元素识别功能
替代慢速OCR，实现2-5秒快速识别
"""

import sys
import os
import signal
import time
from contextlib import contextmanager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.fast_label_integrator import FastLabelIntegrator

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
    if message:
        print(f"{message}开始执行！")
    return True

def demo_fast_recognition():
    """演示快速识别功能"""
    print("=== 快速视觉识别演示 ===")
    print("🚀 功能: 截图 => 快速识别可点击元素 => 显示标签")
    print("✨ 特点: 无需OCR，基于计算机视觉，2-5秒快速完成")
    print("💡 提示: 按 Ctrl+C 可以随时安全退出")
    
    integrator = FastLabelIntegrator()
    
    with keyboard_interrupt_handler():
        try:
            print("\n=== 演示1: 全屏快速识别 ===")
            print("将识别所有可点击元素：按钮、链接、图标、文字区域等")
            if countdown_with_interrupt(3, "全屏识别倒计时: "):
                if not _interrupted:
                    start_time = time.time()
                    success = integrator.analyze_and_label(duration=5.0)
                    elapsed_time = time.time() - start_time
                    
                    if success:
                        print(f"\n⚡ 识别完成！总耗时: {elapsed_time:.2f} 秒")
                        print("标签将显示5秒...")
                        time.sleep(5)
            
            if _interrupted:
                return
                
            print("\n=== 演示2: 屏幕中心区域识别 ===")
            print("只识别屏幕中心区域，提升识别速度")
            if countdown_with_interrupt(2, "区域识别倒计时: "):
                if not _interrupted:
                    # 分析屏幕中心600x400区域
                    screen_width, screen_height = integrator._screenshot_tool.get_screen_size()
                    x = (screen_width - 600) // 2
                    y = (screen_height - 400) // 2
                    region = (x, y, 600, 400)
                    
                    start_time = time.time()
                    success = integrator.analyze_and_label(region=region, duration=0)
                    elapsed_time = time.time() - start_time
                    
                    if success:
                        print(f"\n⚡ 区域识别完成！耗时: {elapsed_time:.2f} 秒")
                        print("标签永久显示，按Enter继续...")
                        input()
            
            if _interrupted:
                return
                
            print("\n=== 演示3: 特定类型元素识别 ===")
            print("只识别按钮和图标，忽略其他类型")
            # 左上角区域，只识别按钮和图标
            region = (50, 50, 500, 300)
            include_types = ['button', 'icon']
            
            start_time = time.time()
            success = integrator.analyze_and_label(
                region=region, 
                duration=3.0,
                include_types=include_types
            )
            elapsed_time = time.time() - start_time
            
            if success:
                print(f"\n⚡ 特定类型识别完成！耗时: {elapsed_time:.2f} 秒")
                print("只显示按钮和图标标签，显示3秒...")
                time.sleep(3)
            
            # 清理标签
            integrator.hide_all()
            
            # 显示统计信息
            print("\n=== 识别统计信息 ===")
            stats = integrator.get_statistics()
            if 'error' not in stats:
                print(f"总识别元素: {stats['total_elements']}")
                print(f"平均置信度: {stats['overall_average_confidence']:.2f}")
                print(f"识别方法: {stats['recognition_method']}")
                print("各类型分布:", end=" ")
                for elem_type, count in stats['type_counts'].items():
                    print(f"{elem_type}:{count}", end=" ")
                print()
            
            print("\n✅ === 演示完成 ===")
            print("🎯 快速视觉识别系统成功替代了慢速OCR！")
            
        except KeyboardInterrupt:
            print("\n[中断] 演示被用户中断")
        except Exception as e:
            print(f"演示过程中发生错误: {e}")
        finally:
            # 确保清理
            try:
                integrator.hide_all()
            except:
                pass

def interactive_demo():
    """交互式快速识别演示"""
    print("\n=== 交互式快速识别演示 ===")
    print("💡 提示: 在任何输入提示处，按 Ctrl+C 可以安全退出")
    
    integrator = FastLabelIntegrator()
    
    with keyboard_interrupt_handler():
        while not _interrupted:
            try:
                print("\n请选择操作:")
                print("1. 全屏快速识别")
                print("2. 屏幕中心区域识别")
                print("3. 自定义区域识别")
                print("4. 特定类型元素识别")
                print("5. 仅识别（不显示标签）")
                print("6. 为当前结果显示标签")
                print("7. 显示当前结果的边界框")
                print("8. 查看识别统计信息")
                print("9. 清空缓存")
                print("10. 隐藏所有显示")
                print("0. 退出")
                
                choice = input("请输入选择 (0-10): ").strip()
                
                if _interrupted:
                    break
                    
                if choice == '1':
                    duration = input("标签显示时长（秒，空=永久）: ").strip()
                    duration = float(duration) if duration else None
                    print("⚡ 进行全屏快速识别...")
                    start_time = time.time()
                    success = integrator.analyze_and_label(duration=duration)
                    elapsed_time = time.time() - start_time
                    if success:
                        print(f"✅ 识别完成！耗时: {elapsed_time:.2f} 秒")
                    
                elif choice == '2':
                    width = int(input("区域宽度（默认600）: ") or "600")
                    height = int(input("区域高度（默认400）: ") or "400")
                    
                    screen_width, screen_height = integrator._screenshot_tool.get_screen_size()
                    x = (screen_width - width) // 2
                    y = (screen_height - height) // 2
                    region = (x, y, width, height)
                    
                    print(f"⚡ 识别屏幕中心区域 {region}...")
                    start_time = time.time()
                    success = integrator.analyze_and_label(region=region)
                    elapsed_time = time.time() - start_time
                    if success:
                        print(f"✅ 区域识别完成！耗时: {elapsed_time:.2f} 秒")
                    
                elif choice == '3':
                    x = int(input("区域X坐标: ") or "100")
                    y = int(input("区域Y坐标: ") or "100")
                    width = int(input("区域宽度: ") or "400")
                    height = int(input("区域高度: ") or "300")
                    max_labels = int(input("最大标签数（默认50）: ") or "50")
                    
                    region = (x, y, width, height)
                    print(f"⚡ 识别自定义区域 {region}...")
                    start_time = time.time()
                    success = integrator.analyze_and_label(region=region, max_labels=max_labels)
                    elapsed_time = time.time() - start_time
                    if success:
                        print(f"✅ 自定义区域识别完成！耗时: {elapsed_time:.2f} 秒")
                    
                elif choice == '4':
                    print("可选类型: button, link, input, icon, text")
                    types_input = input("请输入要识别的类型（用逗号分隔）: ").strip()
                    if types_input:
                        include_types = [t.strip() for t in types_input.split(',')]
                        print(f"⚡ 只识别 {include_types} 类型的元素...")
                        start_time = time.time()
                        success = integrator.analyze_and_label(include_types=include_types)
                        elapsed_time = time.time() - start_time
                        if success:
                            print(f"✅ 特定类型识别完成！耗时: {elapsed_time:.2f} 秒")
                    else:
                        print("未输入类型，跳过")
                    
                elif choice == '5':
                    region_choice = input("区域类型（1=全屏，2=自定义）: ").strip()
                    if region_choice == '2':
                        x = int(input("X坐标: ") or "0")
                        y = int(input("Y坐标: ") or "0")
                        width = int(input("宽度: ") or "600")
                        height = int(input("高度: ") or "400")
                        region = (x, y, width, height)
                    else:
                        region = None
                    
                    print("⚡ 执行快速识别...")
                    start_time = time.time()
                    success = integrator.capture_and_recognize(region=region)
                    elapsed_time = time.time() - start_time
                    if success:
                        detections = integrator.get_current_detections()
                        print(f"✅ 识别完成！发现 {len(detections)} 个元素，耗时: {elapsed_time:.2f} 秒")
                        print("使用选项6显示标签")
                    
                elif choice == '6':
                    max_labels = int(input("最大标签数（默认50）: ") or "50")
                    duration = input("显示时长（秒，空=永久）: ").strip()
                    duration = float(duration) if duration else None
                    
                    success = integrator.show_labels(max_labels=max_labels, duration=duration)
                    if success:
                        print("✅ 标签显示完成")
                    
                elif choice == '7':
                    duration = input("边界框显示时长（秒，空=永久）: ").strip()
                    duration = float(duration) if duration else None
                    color = input("边界框颜色（默认red）: ").strip() or "red"
                    
                    success = integrator.show_bounding_boxes(duration=duration, box_color=color)
                    if success:
                        print("✅ 边界框显示完成")
                    
                elif choice == '8':
                    stats = integrator.get_statistics()
                    if 'error' not in stats:
                        print(f"\n📊 === 识别统计信息 ===")
                        print(f"总元素数: {stats['total_elements']}")
                        print(f"平均置信度: {stats['overall_average_confidence']:.3f}")
                        print(f"已显示标签: {stats['labels_displayed']}")
                        print(f"识别方法: {stats['recognition_method']}")
                        print("\n各类型分布:")
                        for elem_type, count in stats['type_counts'].items():
                            avg_conf = stats['average_confidences'][elem_type]
                            print(f"  {elem_type}: {count} 个（平均置信度: {avg_conf:.3f}）")
                    else:
                        print(f"获取统计信息失败: {stats['error']}")
                    
                elif choice == '9':
                    integrator.clear_cache()
                    print("✅ 缓存已清空")
                    
                elif choice == '10':
                    integrator.hide_all()
                    print("✅ 所有显示已隐藏")
                    
                elif choice == '0':
                    print("退出演示")
                    break
                    
                else:
                    print("❌ 无效选择，请重新输入")
                    
            except KeyboardInterrupt:
                print("\n[中断] 演示被用户中断")
                break
            except ValueError:
                print("❌ 输入格式错误，请重新输入")
            except Exception as e:
                print(f"❌ 操作失败: {e}")
                
        if _interrupted:
            print("\n[中断] 交互式演示已安全退出")
        
        # 清理
        try:
            integrator.hide_all()
        except:
            pass

def performance_comparison_demo():
    """性能对比演示（与OCR对比）"""
    print("\n=== 性能对比演示 ===")
    print("🏁 对比快速视觉识别与传统OCR的性能差异")
    
    integrator = FastLabelIntegrator()
    
    print("\n测试场景: 屏幕中心800x600区域识别")
    
    # 准备测试区域
    screen_width, screen_height = integrator._screenshot_tool.get_screen_size()
    x = (screen_width - 800) // 2
    y = (screen_height - 600) // 2
    region = (x, y, 800, 600)
    
    try:
        # 快速视觉识别测试
        print("\n🚀 测试1: 快速视觉识别")
        print("正在进行快速识别...")
        
        start_time = time.time()
        success = integrator.capture_and_recognize(region=region)
        fast_time = time.time() - start_time
        
        if success:
            detections = integrator.get_current_detections()
            print(f"✅ 快速识别完成")
            print(f"⏱️  耗时: {fast_time:.2f} 秒")
            print(f"🎯 发现元素: {len(detections)} 个")
            
            # 显示结果3秒
            integrator.show_labels(max_labels=20, duration=3.0)
            print("结果显示3秒...")
            time.sleep(3)
        
        # 模拟OCR时间（基于实际测试）
        print(f"\n📊 === 性能对比结果 ===")
        print(f"🚀 快速视觉识别: {fast_time:.2f} 秒")
        print(f"🐌 传统OCR（估算）: 60-180 秒")
        
        if fast_time > 0:
            speed_improvement = 120 / fast_time  # 使用中位数120秒作为OCR基准
            print(f"⚡ 性能提升: {speed_improvement:.1f} 倍")
            print(f"💡 时间节省: {120 - fast_time:.1f} 秒")
        
        print(f"\n🎯 === 总结 ===")
        print(f"✅ 快速视觉识别成功实现了目标：")
        print(f"   • 识别时间从 1-3分钟 降低到 {fast_time:.1f} 秒")
        print(f"   • 性能提升超过 {speed_improvement:.0f} 倍")
        print(f"   • 专注可点击元素，更符合实际需求")
        print(f"   • 无需OCR，降低了系统复杂度")
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
    finally:
        try:
            integrator.hide_all()
        except:
            pass

if __name__ == "__main__":
    print("🚀 快速视觉识别演示程序")
    print("✨ 基于计算机视觉技术，快速识别可点击UI元素")
    print("⚡ 性能目标：2-5秒完成识别（相比OCR提升20-90倍）")
    print("🎯 专注键盘代替鼠标的实际需求")
    print("💡 依赖：FastVisualRecognizer + ScreenLabeler + BoundingBoxOverlay")
    print("提示: 按 Ctrl+C 可以随时安全退出")
    
    try:
        demo_type = input("\n选择演示类型 (1=自动演示, 2=交互式演示, 3=性能对比): ").strip()
        
        if demo_type == '1':
            demo_fast_recognition()
        elif demo_type == '2':
            interactive_demo()
        elif demo_type == '3':
            performance_comparison_demo()
        else:
            print("默认运行自动演示...")
            demo_fast_recognition()
            
    except KeyboardInterrupt:
        print("\n[中断] 程序已安全退出")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        print("\n💡 可能的解决方案:")
        print("1. 确保已安装opencv-python")
        print("2. 检查requirements.txt中的依赖是否已安装")
        print("3. 确保系统支持图形界面显示")
        print("4. 检查屏幕截图权限")