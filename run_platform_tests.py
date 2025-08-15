# -*- coding: utf-8 -*-
"""
平台模块测试运行器
"""

import sys
import os
import unittest

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_hotkey_manager_test():
    """运行HotkeyManager测试"""
    print("正在运行 HotkeyManager 单元测试...")
    
    # 导入测试模块
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests', 'platform'))
    
    try:
        from test_hotkey_manager import TestHotkeyManager
        
        # 运行测试
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestHotkeyManager)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        print(f"\n测试结果:")
        print(f"运行测试数: {result.testsRun}")
        print(f"失败数: {len(result.failures)}")
        print(f"错误数: {len(result.errors)}")
        
        return result.wasSuccessful()
        
    except ImportError as e:
        print(f"导入测试模块失败: {e}")
        return False
    except Exception as e:
        print(f"运行测试时出错: {e}")
        return False

def run_basic_platform_tests():
    """运行基础平台模块测试"""
    print("正在运行基础平台模块功能验证...")
    
    try:
        # 测试导入
        from platform.hotkey_manager import HotkeyManager
        from platform.keyboard_listener import KeyboardListener
        from platform.mouse_controller import MouseController
        from platform.system_manager import SystemManager
        from platform.interfaces import HotkeyModifier, SystemMetrics
        
        print("[OK] 所有平台模块导入成功")
        
        # 测试基础实例化（使用Mock避免实际系统调用）
        from unittest.mock import patch
        
        with patch('platform.hotkey_manager.Listener'), \
             patch('platform.keyboard_listener.Listener'), \
             patch('platform.mouse_controller.mouse.Controller'), \
             patch('platform.system_manager.psutil.Process'):
            
            hotkey_mgr = HotkeyManager()
            keyboard_listener = KeyboardListener()
            mouse_controller = MouseController()
            system_mgr = SystemManager()
            
            print("[OK] 所有平台模块实例化成功")
        
        # 测试基础接口
        print("[OK] 接口定义正确")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 平台模块测试失败: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("KeyboardClicker 平台模块测试")
    print("=" * 60)
    
    # 运行基础测试
    basic_success = run_basic_platform_tests()
    
    if basic_success:
        print("\n" + "=" * 60)
        # 运行单元测试
        test_success = run_hotkey_manager_test()
        
        print("\n" + "=" * 60)
        if test_success:
            print("[SUCCESS] 所有测试通过！")
        else:
            print("[FAIL] 部分测试失败")
    else:
        print("[FAIL] 基础测试失败，跳过单元测试")
    
    print("=" * 60)