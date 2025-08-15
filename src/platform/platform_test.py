# -*- coding: utf-8 -*-
"""
平台模块测试和验证工具
用于测试和验证平台模块的各项功能
"""

import time
import threading
from typing import Dict, List, Any, Callable
from dataclasses import dataclass

from .platform_manager import PlatformManager
from .interfaces import SystemMetrics, IPlatformException
from .performance_config import GetCurrentConfig, SetPerformanceProfile


@dataclass
class TestResult:
    """测试结果数据结构"""
    TestName: str
    Success: bool
    Duration: float
    Message: str
    Details: Dict[str, Any] = None


class PlatformTester:
    """平台模块测试器"""
    
    def __init__(self):
        self._platform_manager = PlatformManager()
        self._test_results: List[TestResult] = []
        self._test_callbacks: Dict[str, List[Callable]] = {}
    
    #region 基础功能测试
    
    def TestSystemCompatibility(self) -> TestResult:
        """测试系统兼容性"""
        start_time = time.perf_counter()
        
        try:
            compatibility = self._platform_manager._system_manager.CheckSystemCompatibility()
            
            # 检查关键兼容性项目
            critical_items = [
                'windows_supported',
                'python_version_ok', 
                'pynput_available',
                'psutil_available'
            ]
            
            failed_items = [item for item in critical_items if not compatibility.get(item, False)]
            
            success = len(failed_items) == 0
            message = "系统兼容性检查通过" if success else f"兼容性检查失败: {failed_items}"
            
            duration = time.perf_counter() - start_time
            
            return TestResult(
                TestName="系统兼容性",
                Success=success,
                Duration=duration,
                Message=message,
                Details=compatibility
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                TestName="系统兼容性",
                Success=False,
                Duration=duration,
                Message=f"测试异常: {str(e)}"
            )
    
    def TestMouseController(self) -> TestResult:
        """测试鼠标控制器"""
        start_time = time.perf_counter()
        
        try:
            # 获取当前位置
            original_pos = self._platform_manager.GetCursorPosition()
            
            # 测试移动
            test_x, test_y = original_pos[0] + 50, original_pos[1] + 50
            move_success = self._platform_manager.HoverAt(test_x, test_y, smooth=False)
            
            if not move_success:
                raise Exception("鼠标移动失败")
            
            # 验证位置
            new_pos = self._platform_manager.GetCursorPosition()
            position_accurate = abs(new_pos[0] - test_x) <= 5 and abs(new_pos[1] - test_y) <= 5
            
            # 恢复原位置
            self._platform_manager.HoverAt(original_pos[0], original_pos[1], smooth=False)
            
            duration = time.perf_counter() - start_time
            
            return TestResult(
                TestName="鼠标控制器",
                Success=move_success and position_accurate,
                Duration=duration,
                Message="鼠标控制器测试通过" if move_success and position_accurate else "鼠标控制器测试失败",
                Details={
                    'original_position': original_pos,
                    'test_position': (test_x, test_y),
                    'final_position': new_pos,
                    'position_accurate': position_accurate
                }
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                TestName="鼠标控制器",
                Success=False,
                Duration=duration,
                Message=f"测试异常: {str(e)}"
            )
    
    def TestScreenManager(self) -> TestResult:
        """测试屏幕管理器"""
        start_time = time.perf_counter()
        
        try:
            # 获取屏幕信息
            screen_rect = self._platform_manager.GetScreenRect()
            dpi_scale = self._platform_manager.GetScreenDpi()
            
            # 验证屏幕信息
            valid_screen = (screen_rect[2] > 0 and screen_rect[3] > 0)  # 宽高大于0
            valid_dpi = (0.5 <= dpi_scale <= 4.0)  # DPI在合理范围内
            
            # 测试坐标验证
            valid_coords = [
                self._platform_manager.ValidateCoordinates(100, 100),
                self._platform_manager.ValidateCoordinates(screen_rect[2] // 2, screen_rect[3] // 2)
            ]
            invalid_coords = [
                self._platform_manager.ValidateCoordinates(-100, -100),
                self._platform_manager.ValidateCoordinates(screen_rect[2] + 100, screen_rect[3] + 100)
            ]
            
            coordinate_test_pass = all(valid_coords) and not any(invalid_coords)
            
            duration = time.perf_counter() - start_time
            success = valid_screen and valid_dpi and coordinate_test_pass
            
            return TestResult(
                TestName="屏幕管理器",
                Success=success,
                Duration=duration,
                Message="屏幕管理器测试通过" if success else "屏幕管理器测试失败",
                Details={
                    'screen_rect': screen_rect,
                    'dpi_scale': dpi_scale,
                    'valid_screen': valid_screen,
                    'valid_dpi': valid_dpi,
                    'coordinate_test_pass': coordinate_test_pass
                }
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                TestName="屏幕管理器",
                Success=False,
                Duration=duration,
                Message=f"测试异常: {str(e)}"
            )
    
    def TestSystemManager(self) -> TestResult:
        """测试系统管理器"""
        start_time = time.perf_counter()
        
        try:
            # 获取系统指标
            metrics = self._platform_manager.GetSystemMetrics()
            
            # 验证指标有效性
            valid_metrics = (
                0 <= metrics.CpuUsagePercent <= 100 and
                metrics.MemoryUsageMb > 0 and
                metrics.ResponseTimeMs >= 0
            )
            
            # 测试资源监控
            monitoring_test_success = False
            monitoring_callback_called = threading.Event()
            
            def test_callback(test_metrics: SystemMetrics):
                monitoring_callback_called.set()
            
            try:
                self._platform_manager.StartResourceMonitoring(test_callback)
                monitoring_callback_called.wait(timeout=2.0)
                monitoring_test_success = monitoring_callback_called.is_set()
                self._platform_manager.StopResourceMonitoring()
            except:
                monitoring_test_success = False
            
            duration = time.perf_counter() - start_time
            success = valid_metrics and monitoring_test_success
            
            return TestResult(
                TestName="系统管理器",
                Success=success,
                Duration=duration,
                Message="系统管理器测试通过" if success else "系统管理器测试失败",
                Details={
                    'metrics': metrics._asdict(),
                    'valid_metrics': valid_metrics,
                    'monitoring_test_success': monitoring_test_success
                }
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                TestName="系统管理器",
                Success=False,
                Duration=duration,
                Message=f"测试异常: {str(e)}"
            )
    
    #endregion
    
    #region 性能测试
    
    def TestPerformance(self) -> TestResult:
        """测试性能指标"""
        start_time = time.perf_counter()
        
        try:
            performance_results = {}
            
            # 测试鼠标操作性能
            mouse_times = []
            for _ in range(10):
                op_start = time.perf_counter()
                pos = self._platform_manager.GetCursorPosition()
                self._platform_manager.HoverAt(pos[0] + 1, pos[1] + 1, smooth=False)
                op_end = time.perf_counter()
                mouse_times.append((op_end - op_start) * 1000)  # 转换为毫秒
            
            avg_mouse_time = sum(mouse_times) / len(mouse_times)
            performance_results['avg_mouse_operation_ms'] = avg_mouse_time
            
            # 测试系统指标获取性能
            metrics_times = []
            for _ in range(10):
                op_start = time.perf_counter()
                self._platform_manager.GetSystemMetrics()
                op_end = time.perf_counter()
                metrics_times.append((op_end - op_start) * 1000)
            
            avg_metrics_time = sum(metrics_times) / len(metrics_times)
            performance_results['avg_metrics_time_ms'] = avg_metrics_time
            
            # 性能要求检查
            mouse_performance_ok = avg_mouse_time < 30.0  # 鼠标操作 < 30ms
            metrics_performance_ok = avg_metrics_time < 10.0  # 指标获取 < 10ms
            
            duration = time.perf_counter() - start_time
            success = mouse_performance_ok and metrics_performance_ok
            
            return TestResult(
                TestName="性能测试",
                Success=success,
                Duration=duration,
                Message="性能测试通过" if success else "性能测试未达标",
                Details=performance_results
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                TestName="性能测试", 
                Success=False,
                Duration=duration,
                Message=f"测试异常: {str(e)}"
            )
    
    #endregion
    
    #region 集成测试
    
    def RunAllTests(self) -> List[TestResult]:
        """运行所有测试"""
        self._test_results.clear()
        
        test_methods = [
            self.TestSystemCompatibility,
            self.TestMouseController,
            self.TestScreenManager,
            self.TestSystemManager,
            self.TestPerformance
        ]
        
        for test_method in test_methods:
            try:
                result = test_method()
                self._test_results.append(result)
                
                # 调用测试回调
                test_name = result.TestName
                if test_name in self._test_callbacks:
                    for callback in self._test_callbacks[test_name]:
                        try:
                            callback(result)
                        except:
                            pass
                            
            except Exception as e:
                # 如果测试方法本身出错，创建失败结果
                self._test_results.append(TestResult(
                    TestName=test_method.__name__,
                    Success=False,
                    Duration=0.0,
                    Message=f"测试方法异常: {str(e)}"
                ))
        
        return self._test_results.copy()
    
    def GetTestSummary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        if not self._test_results:
            return {'error': '尚未运行测试'}
        
        total_tests = len(self._test_results)
        passed_tests = sum(1 for result in self._test_results if result.Success)
        failed_tests = total_tests - passed_tests
        total_duration = sum(result.Duration for result in self._test_results)
        
        return {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            'total_duration': total_duration,
            'results': [
                {
                    'name': result.TestName,
                    'success': result.Success,
                    'duration': result.Duration,
                    'message': result.Message
                }
                for result in self._test_results
            ]
        }
    
    #endregion
    
    #region 回调管理
    
    def RegisterTestCallback(self, test_name: str, callback: Callable[[TestResult], None]) -> None:
        """注册测试回调"""
        if test_name not in self._test_callbacks:
            self._test_callbacks[test_name] = []
        self._test_callbacks[test_name].append(callback)
    
    def UnregisterTestCallback(self, test_name: str, callback: Callable[[TestResult], None]) -> None:
        """注销测试回调"""
        if test_name in self._test_callbacks:
            try:
                self._test_callbacks[test_name].remove(callback)
            except ValueError:
                pass
    
    #endregion


#region 便捷函数

def QuickTest() -> Dict[str, Any]:
    """快速测试平台功能"""
    tester = PlatformTester()
    tester.RunAllTests()
    return tester.GetTestSummary()


def TestWithProfile(profile_name: str) -> Dict[str, Any]:
    """使用指定性能配置进行测试"""
    original_profile = GetCurrentConfig()
    
    try:
        SetPerformanceProfile(profile_name)
        return QuickTest()
    finally:
        # 恢复原始配置
        try:
            SetPerformanceProfile("default")
        except:
            pass


def BenchmarkPerformance() -> Dict[str, Any]:
    """性能基准测试"""
    profiles = ["low_resource", "default", "high_performance"]
    results = {}
    
    for profile in profiles:
        try:
            results[profile] = TestWithProfile(profile)
        except Exception as e:
            results[profile] = {'error': str(e)}
    
    return results

#endregion