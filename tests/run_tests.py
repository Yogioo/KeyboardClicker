# -*- coding: utf-8 -*-
"""
测试运行器
运行所有单元测试并生成报告
"""

import unittest
import sys
import os
import time
from io import StringIO

# 添加项目根目录和src目录到Python路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))


#region 测试结果收集器

class TestResultCollector(unittest.TestResult):
    """自定义测试结果收集器"""
    
    def __init__(self):
        super().__init__()
        self.test_results = []
        self.start_time = None
        self.end_time = None
        
    def startTest(self, test):
        super().startTest(test)
        self.start_time = time.time()
        
    def stopTest(self, test):
        super().stopTest(test)
        self.end_time = time.time()
        
        duration = self.end_time - self.start_time
        status = "PASS"
        error_info = None
        
        # 检查测试状态
        if self.errors and test in [e[0] for e in self.errors]:
            status = "ERROR"
            error_info = next(e[1] for e in self.errors if e[0] == test)
        elif self.failures and test in [f[0] for f in self.failures]:
            status = "FAIL"
            error_info = next(f[1] for f in self.failures if f[0] == test)
        elif self.skipped and test in [s[0] for s in self.skipped]:
            status = "SKIP"
            error_info = next(s[1] for s in self.skipped if s[0] == test)
            
        self.test_results.append({
            'test': test,
            'status': status,
            'duration': duration,
            'error': error_info
        })

#endregion


#region 测试报告生成器

class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self, result: TestResultCollector):
        self.result = result
        
    def generate_console_report(self) -> str:
        """生成控制台报告"""
        output = StringIO()
        
        # 标题
        output.write("=" * 80 + "\n")
        output.write("KeyboardClicker 核心模块测试报告\n")
        output.write("=" * 80 + "\n\n")
        
        # 总览
        total_tests = len(self.result.test_results)
        passed_tests = len([r for r in self.result.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.result.test_results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.result.test_results if r['status'] == 'ERROR'])
        skipped_tests = len([r for r in self.result.test_results if r['status'] == 'SKIP'])
        
        output.write(f"总测试数: {total_tests}\n")
        output.write(f"通过: {passed_tests}\n")
        output.write(f"失败: {failed_tests}\n")
        output.write(f"错误: {error_tests}\n")
        output.write(f"跳过: {skipped_tests}\n")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        output.write(f"成功率: {success_rate:.1f}%\n\n")
        
        # 按模块分组
        modules = {}
        for result in self.result.test_results:
            test_class = result['test'].__class__.__name__
            module_name = result['test'].__class__.__module__.split('.')[-1]
            
            if module_name not in modules:
                modules[module_name] = []
            modules[module_name].append(result)
        
        # 模块详情
        for module_name, module_results in modules.items():
            output.write(f"模块: {module_name}\n")
            output.write("-" * 40 + "\n")
            
            module_passed = len([r for r in module_results if r['status'] == 'PASS'])
            module_total = len(module_results)
            module_rate = (module_passed / module_total * 100) if module_total > 0 else 0
            
            output.write(f"  通过率: {module_rate:.1f}% ({module_passed}/{module_total})\n")
            
            # 失败的测试
            failed_in_module = [r for r in module_results if r['status'] in ['FAIL', 'ERROR']]
            if failed_in_module:
                output.write("  失败的测试:\n")
                for result in failed_in_module:
                    test_name = result['test']._testMethodName
                    output.write(f"    - {test_name} ({result['status']})\n")
            
            output.write("\n")
        
        # 性能统计
        output.write("性能统计\n")
        output.write("-" * 40 + "\n")
        
        durations = [r['duration'] for r in self.result.test_results]
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
            
            output.write(f"平均耗时: {avg_duration:.3f}秒\n")
            output.write(f"最长耗时: {max_duration:.3f}秒\n")
            output.write(f"最短耗时: {min_duration:.3f}秒\n")
            
            # 慢测试
            slow_tests = [r for r in self.result.test_results if r['duration'] > 0.1]
            if slow_tests:
                output.write("\n慢测试 (>0.1秒):\n")
                for result in sorted(slow_tests, key=lambda x: x['duration'], reverse=True):
                    test_name = result['test']._testMethodName
                    output.write(f"  {test_name}: {result['duration']:.3f}秒\n")
        
        output.write("\n" + "=" * 80 + "\n")
        
        return output.getvalue()
    
    def generate_detailed_report(self) -> str:
        """生成详细报告"""
        output = StringIO()
        
        # 详细的失败信息
        failed_tests = [r for r in self.result.test_results if r['status'] in ['FAIL', 'ERROR']]
        
        if failed_tests:
            output.write("失败测试详情\n")
            output.write("=" * 80 + "\n\n")
            
            for result in failed_tests:
                test_name = f"{result['test'].__class__.__name__}.{result['test']._testMethodName}"
                output.write(f"测试: {test_name}\n")
                output.write(f"状态: {result['status']}\n")
                output.write(f"耗时: {result['duration']:.3f}秒\n")
                
                if result['error']:
                    output.write("错误信息:\n")
                    output.write(result['error'])
                    output.write("\n")
                
                output.write("-" * 80 + "\n\n")
        
        return output.getvalue()

#endregion


#region 测试套件构建器

class TestSuiteBuilder:
    """测试套件构建器"""
    
    def __init__(self):
        self.loader = unittest.TestLoader()
    
    def build_core_suite(self) -> unittest.TestSuite:
        """构建核心模块测试套件"""
        suite = unittest.TestSuite()
        
        # 核心模块测试
        core_modules = [
            'tests.core.test_grid_calculator',
            'tests.core.test_input_processor', 
            'tests.core.test_command_executor',
            'tests.core.test_grid_coordinate_system',
            'tests.core.test_integration'
        ]
        
        for module_name in core_modules:
            try:
                module_suite = self.loader.loadTestsFromName(module_name)
                suite.addTest(module_suite)
            except Exception as e:
                print(f"警告: 无法加载测试模块 {module_name}: {e}")
        
        return suite
    
    def build_all_suite(self) -> unittest.TestSuite:
        """构建所有测试套件"""
        suite = unittest.TestSuite()
        
        # 添加核心模块测试
        core_suite = self.build_core_suite()
        suite.addTest(core_suite)
        
        # 这里可以添加其他模块的测试
        # platform_suite = self.build_platform_suite()
        # ui_suite = self.build_ui_suite()
        # suite.addTest(platform_suite)
        # suite.addTest(ui_suite)
        
        return suite

#endregion


#region 测试运行器

class TestRunner:
    """测试运行器"""
    
    def __init__(self, verbosity=2):
        self.verbosity = verbosity
        self.builder = TestSuiteBuilder()
    
    def run_core_tests(self) -> TestResultCollector:
        """运行核心模块测试"""
        print("运行核心模块测试...")
        
        suite = self.builder.build_core_suite()
        result = TestResultCollector()
        
        # 运行测试
        start_time = time.time()
        suite.run(result)
        end_time = time.time()
        
        print(f"测试完成，耗时: {end_time - start_time:.2f}秒")
        
        return result
    
    def run_all_tests(self) -> TestResultCollector:
        """运行所有测试"""
        print("运行所有测试...")
        
        suite = self.builder.build_all_suite()
        result = TestResultCollector()
        
        # 运行测试
        start_time = time.time()
        suite.run(result)
        end_time = time.time()
        
        print(f"所有测试完成，耗时: {end_time - start_time:.2f}秒")
        
        return result
    
    def run_specific_test(self, test_pattern: str) -> TestResultCollector:
        """运行特定测试"""
        print(f"运行匹配模式的测试: {test_pattern}")
        
        suite = self.loader.loadTestsFromName(test_pattern)
        result = TestResultCollector()
        
        start_time = time.time()
        suite.run(result)
        end_time = time.time()
        
        print(f"测试完成，耗时: {end_time - start_time:.2f}秒")
        
        return result

#endregion


#region 主函数

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='KeyboardClicker 测试运行器')
    parser.add_argument('--core', action='store_true', help='仅运行核心模块测试')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    parser.add_argument('--test', type=str, help='运行特定测试')
    parser.add_argument('--report', type=str, help='保存报告到文件')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 默认运行核心测试
    if not any([args.core, args.all, args.test]):
        args.core = True
    
    runner = TestRunner(verbosity=2 if args.verbose else 1)
    
    try:
        # 运行测试
        if args.test:
            result = runner.run_specific_test(args.test)
        elif args.all:
            result = runner.run_all_tests()
        else:
            result = runner.run_core_tests()
        
        # 生成报告
        generator = TestReportGenerator(result)
        console_report = generator.generate_console_report()
        
        # 输出到控制台
        print(console_report)
        
        # 如果有失败，输出详细信息
        if result.failures or result.errors:
            detailed_report = generator.generate_detailed_report()
            print(detailed_report)
        
        # 保存到文件
        if args.report:
            with open(args.report, 'w', encoding='utf-8') as f:
                f.write(console_report)
                if result.failures or result.errors:
                    f.write("\n\n")
                    f.write(generator.generate_detailed_report())
            print(f"报告已保存到: {args.report}")
        
        # 返回退出码
        if result.failures or result.errors:
            return 1
        else:
            return 0
            
    except Exception as e:
        print(f"测试运行出错: {e}")
        return 1


def run_core_tests_simple():
    """简单运行核心测试的函数"""
    runner = TestRunner()
    result = runner.run_core_tests()
    
    generator = TestReportGenerator(result)
    print(generator.generate_console_report())
    
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == '__main__':
    sys.exit(main())

#endregion