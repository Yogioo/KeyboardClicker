# -*- coding: utf-8 -*-
"""
平台模块测试套件
运行所有平台模块的单元测试和集成测试
"""

import unittest
import sys
import os

# 添加src路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# 导入所有测试模块
from test_hotkey_manager import TestHotkeyManager
from test_keyboard_listener import TestKeyboardListener
from test_mouse_controller import TestMouseController
from test_system_manager import TestSystemManager
from test_integration import TestPlatformIntegration


def create_test_suite():
    """创建完整的测试套件"""
    suite = unittest.TestSuite()
    
    # 添加单元测试
    suite.addTest(unittest.makeSuite(TestHotkeyManager))
    suite.addTest(unittest.makeSuite(TestKeyboardListener))
    suite.addTest(unittest.makeSuite(TestMouseController))
    suite.addTest(unittest.makeSuite(TestSystemManager))
    
    # 添加集成测试
    suite.addTest(unittest.makeSuite(TestPlatformIntegration))
    
    return suite


def run_tests(verbosity=2):
    """运行所有测试"""
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result


def run_specific_module(module_name, verbosity=2):
    """运行特定模块的测试"""
    module_map = {
        'hotkey': TestHotkeyManager,
        'keyboard': TestKeyboardListener,
        'mouse': TestMouseController,
        'system': TestSystemManager,
        'integration': TestPlatformIntegration
    }
    
    if module_name not in module_map:
        print(f"未知的测试模块: {module_name}")
        print(f"可用模块: {', '.join(module_map.keys())}")
        return None
    
    suite = unittest.makeSuite(module_map[module_name])
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result


def generate_test_report(result):
    """生成测试报告"""
    print("\n" + "="*60)
    print("平台模块测试报告")
    print("="*60)
    
    print(f"测试运行总数: {result.testsRun}")
    print(f"测试成功数: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"测试失败数: {len(result.failures)}")
    print(f"测试错误数: {len(result.errors)}")
    print(f"跳过测试数: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('\\n')[-2] if traceback else '未知错误'}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\\n')[-2] if traceback else '未知错误'}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n总体成功率: {success_rate:.1f}%")
    
    print("="*60)
    
    return success_rate >= 95.0  # 95%以上成功率认为通过


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='运行平台模块测试套件')
    parser.add_argument('--module', '-m', 
                       choices=['hotkey', 'keyboard', 'mouse', 'system', 'integration'],
                       help='运行特定模块的测试')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='详细输出')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='静默模式')
    
    args = parser.parse_args()
    
    # 确定详细程度
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 1
    
    # 运行测试
    if args.module:
        result = run_specific_module(args.module, verbosity)
    else:
        result = run_tests(verbosity)
    
    if result:
        # 生成报告
        success = generate_test_report(result)
        
        # 设置退出代码
        sys.exit(0 if success else 1)
    else:
        sys.exit(1)