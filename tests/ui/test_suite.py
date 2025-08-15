#region UI Test Suite
"""
UI模块测试套件
运行所有UI相关测试并生成报告
"""

import pytest
import sys
import os
from pathlib import Path

# 添加源代码路径
sys.path.insert(0, r'D:\GitProj\KeyboardClicker\src')

def run_ui_tests(verbose=True, coverage=False):
    """
    运行UI模块所有测试
    
    Args:
        verbose: 是否详细输出
        coverage: 是否生成覆盖率报告
    
    Returns:
        int: 测试结果代码
    """
    
    # 获取当前目录
    current_dir = Path(__file__).parent
    
    # 测试参数
    args = [
        str(current_dir),  # 测试目录
        '-v' if verbose else '-q',  # 详细程度
        '--tb=short',  # 简短的错误追踪
        '--durations=10',  # 显示最慢的10个测试
    ]
    
    if coverage:
        args.extend([
            '--cov=ui',  # 覆盖率检查ui模块
            '--cov-report=html:htmlcov_ui',  # HTML报告
            '--cov-report=term-missing',  # 终端显示缺失行
            '--cov-fail-under=90',  # 覆盖率要求90%以上
        ])
    
    # 运行测试
    return pytest.main(args)


def run_specific_test(test_name, verbose=True):
    """
    运行特定测试
    
    Args:
        test_name: 测试名称 (overlay_window, grid_renderer, path_indicator, event_handler, integration)
        verbose: 是否详细输出
    
    Returns:
        int: 测试结果代码
    """
    
    current_dir = Path(__file__).parent
    test_file_map = {
        'overlay_window': 'test_overlay_window.py',
        'grid_renderer': 'test_grid_renderer.py', 
        'path_indicator': 'test_path_indicator.py',
        'event_handler': 'test_event_handler.py',
        'integration': 'test_integration.py'
    }
    
    if test_name not in test_file_map:
        print(f"未知的测试名称: {test_name}")
        print(f"可用的测试: {', '.join(test_file_map.keys())}")
        return 1
    
    test_file = current_dir / test_file_map[test_name]
    
    args = [
        str(test_file),
        '-v' if verbose else '-q',
        '--tb=short'
    ]
    
    return pytest.main(args)


def generate_test_report():
    """
    生成测试报告
    
    Returns:
        int: 测试结果代码
    """
    
    current_dir = Path(__file__).parent
    report_file = current_dir.parent.parent / 'ui_test_report.html'
    
    args = [
        str(current_dir),
        '--html=' + str(report_file),
        '--self-contained-html',
        '--cov=ui',
        '--cov-report=html:htmlcov_ui',
        '-v'
    ]
    
    result = pytest.main(args)
    
    if result == 0:
        print(f"\n测试报告已生成: {report_file}")
        print(f"覆盖率报告: {current_dir.parent.parent / 'htmlcov_ui' / 'index.html'}")
    
    return result


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='UI模块测试套件')
    parser.add_argument('--test', choices=['overlay_window', 'grid_renderer', 'path_indicator', 'event_handler', 'integration'], 
                       help='运行特定测试')
    parser.add_argument('--coverage', action='store_true', help='生成覆盖率报告')
    parser.add_argument('--report', action='store_true', help='生成HTML测试报告')
    parser.add_argument('--quiet', action='store_true', help='安静模式')
    
    args = parser.parse_args()
    
    verbose = not args.quiet
    
    if args.report:
        # 生成完整报告
        exit_code = generate_test_report()
    elif args.test:
        # 运行特定测试
        exit_code = run_specific_test(args.test, verbose)
    else:
        # 运行所有测试
        exit_code = run_ui_tests(verbose, args.coverage)
    
    sys.exit(exit_code)

#endregion