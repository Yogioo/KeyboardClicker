# -*- coding: utf-8 -*-
"""
平台模块使用示例
演示如何使用平台操作模块的各种功能
"""

import time
import sys
from typing import Callable

# 导入平台模块
from . import (
    PlatformManager,
    HotkeyModifier,
    SystemMetrics,
    QuickTest,
    SetPerformanceProfile
)


def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 创建平台管理器
    platform = PlatformManager()
    
    try:
        # 初始化平台
        if not platform.Initialize():
            print("平台初始化失败")
            return
        
        print("平台初始化成功")
        
        # 获取屏幕信息
        screen_rect = platform.GetScreenRect()
        print(f"屏幕尺寸: {screen_rect[2]}x{screen_rect[3]}")
        
        # 获取当前鼠标位置
        cursor_pos = platform.GetCursorPosition()
        print(f"当前鼠标位置: {cursor_pos}")
        
        # 获取系统性能指标
        metrics = platform.GetSystemMetrics()
        print(f"CPU使用率: {metrics.CpuUsagePercent:.1f}%")
        print(f"内存使用: {metrics.MemoryUsageMb:.1f}MB")
        
        # 测试鼠标移动
        print("测试鼠标移动...")
        original_pos = platform.GetCursorPosition()
        test_x, test_y = original_pos[0] + 100, original_pos[1] + 100
        
        if platform.HoverAt(test_x, test_y, smooth=True):
            print("鼠标移动成功")
            time.sleep(1)
            # 恢复原位置
            platform.HoverAt(original_pos[0], original_pos[1], smooth=True)
        else:
            print("鼠标移动失败")
        
    finally:
        # 清理资源
        platform.Cleanup()
        print("平台资源已清理")


def example_hotkey_usage():
    """热键使用示例"""
    print("\n=== 热键使用示例 ===")
    
    platform = PlatformManager()
    
    def on_activation():
        print("激活热键被按下! (Alt+G)")
        # 在实际应用中，这里会激活网格系统
    
    def on_exit():
        print("退出热键被按下! (Esc)")
        # 在实际应用中，这里会退出网格模式
    
    try:
        platform.Initialize()
        
        # 注册热键
        print("注册热键: Alt+G (激活), Esc (退出)")
        
        if platform.RegisterActivationHotkey(on_activation):
            print("激活热键注册成功")
        else:
            print("激活热键注册失败")
        
        if platform.RegisterExitHotkey(on_exit):
            print("退出热键注册成功")
        else:
            print("退出热键注册失败")
        
        print("热键已激活，请按 Alt+G 或 Esc 测试 (10秒后自动退出)")
        time.sleep(10)
        
    finally:
        platform.Cleanup()
        print("热键已注销")


def example_keyboard_listening():
    """键盘监听示例"""
    print("\n=== 键盘监听示例 ===")
    
    platform = PlatformManager()
    received_keys = []
    
    def on_key_press(key: str):
        print(f"按键: {key}")
        received_keys.append(key)
        
        # 如果按下了退出键，停止监听
        if key == 'escape':
            platform.StopKeyboardListening()
    
    try:
        platform.Initialize()
        
        print("开始键盘监听 (只监听九宫格按键: QWEASDZXC)")
        print("按下 Esc 键退出监听")
        
        if platform.StartKeyboardListening(on_key_press):
            print("键盘监听已启动")
            
            # 等待监听结束
            while platform.IsKeyboardListening():
                time.sleep(0.1)
            
            print(f"监听结束，共接收到 {len(received_keys)} 个按键")
        else:
            print("键盘监听启动失败")
    
    finally:
        platform.Cleanup()


def example_resource_monitoring():
    """资源监控示例"""
    print("\n=== 资源监控示例 ===")
    
    platform = PlatformManager()
    metrics_count = 0
    
    def on_metrics_update(metrics: SystemMetrics):
        nonlocal metrics_count
        metrics_count += 1
        print(f"[{metrics_count}] CPU: {metrics.CpuUsagePercent:.1f}%, "
              f"内存: {metrics.MemoryUsageMb:.1f}MB, "
              f"响应时间: {metrics.ResponseTimeMs:.2f}ms")
    
    try:
        platform.Initialize()
        
        print("开始资源监控 (5秒)")
        platform.StartResourceMonitoring(on_metrics_update)
        
        time.sleep(5)
        
        platform.StopResourceMonitoring()
        print(f"资源监控结束，共收集 {metrics_count} 次数据")
    
    finally:
        platform.Cleanup()


def example_performance_profiles():
    """性能配置示例"""
    print("\n=== 性能配置示例 ===")
    
    profiles = ["low_resource", "default", "high_performance"]
    
    for profile_name in profiles:
        print(f"\n测试性能配置: {profile_name}")
        
        try:
            # 设置性能配置
            SetPerformanceProfile(profile_name)
            
            # 运行快速测试
            start_time = time.perf_counter()
            test_results = QuickTest()
            end_time = time.perf_counter()
            
            print(f"测试耗时: {(end_time - start_time):.2f}秒")
            print(f"成功率: {test_results.get('success_rate', 0):.1f}%")
            print(f"通过测试: {test_results.get('passed', 0)}/{test_results.get('total_tests', 0)}")
            
        except Exception as e:
            print(f"测试失败: {str(e)}")


def example_error_handling():
    """错误处理示例"""
    print("\n=== 错误处理示例 ===")
    
    platform = PlatformManager()
    
    try:
        platform.Initialize()
        
        # 测试无效坐标
        print("测试无效坐标处理...")
        try:
            result = platform.ClickAt(-1000, -1000)
            print(f"无效坐标点击结果: {result}")
        except Exception as e:
            print(f"捕获到预期异常: {type(e).__name__}: {str(e)}")
        
        # 测试大坐标值
        print("测试大坐标值处理...")
        try:
            result = platform.HoverAt(99999, 99999)
            print(f"大坐标移动结果: {result}")
        except Exception as e:
            print(f"捕获到异常: {type(e).__name__}: {str(e)}")
        
        print("错误处理测试完成")
    
    finally:
        platform.Cleanup()


def main():
    """主函数 - 运行所有示例"""
    print("KeyboardClicker 平台模块使用示例")
    print("=" * 50)
    
    # 检查系统要求
    try:
        from . import CheckSystemRequirements
        requirements = CheckSystemRequirements()
        
        print("系统要求检查:")
        critical_items = ['windows_supported', 'python_version_ok', 'pynput_available']
        
        for item in critical_items:
            status = "✓" if requirements.get(item, False) else "✗"
            print(f"  {status} {item}")
        
        if not all(requirements.get(item, False) for item in critical_items):
            print("\n警告: 系统要求检查失败，某些功能可能无法正常工作")
            return
        
    except Exception as e:
        print(f"系统检查失败: {str(e)}")
        return
    
    print("\n开始运行示例...")
    
    try:
        # 运行基础示例
        example_basic_usage()
        
        # 运行性能配置示例
        example_performance_profiles()
        
        # 运行错误处理示例
        example_error_handling()
        
        # 注意: 热键和键盘监听示例需要用户交互，在自动化测试中跳过
        user_input = input("\n是否运行交互式示例 (热键和键盘监听)? (y/N): ")
        if user_input.lower() == 'y':
            example_hotkey_usage()
            example_keyboard_listening()
            example_resource_monitoring()
        
        print("\n所有示例运行完成!")
        
    except KeyboardInterrupt:
        print("\n用户中断，退出示例")
    except Exception as e:
        print(f"\n示例运行出错: {str(e)}")


if __name__ == "__main__":
    main()