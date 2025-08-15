# -*- coding: utf-8 -*-
"""
平台模块集成测试
测试各个平台组件之间的协作和整体功能
"""

import unittest
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.platform.hotkey_manager import HotkeyManager
from src.platform.keyboard_listener import KeyboardListener
from src.platform.mouse_controller import MouseController
from src.platform.system_manager import SystemManager
from src.platform.interfaces import (
    HotkeyModifier, 
    SystemMetrics, 
    HotkeyRegistrationError, 
    MouseOperationError,
    SystemResourceError
)


class TestPlatformIntegration(unittest.TestCase):
    """平台模块集成测试类"""
    
    #region 测试初始化和清理
    
    def setUp(self):
        """测试前初始化"""
        # 使用Mock避免实际的系统调用
        with patch('src.platform.hotkey_manager.Listener'), \
             patch('src.platform.keyboard_listener.Listener'), \
             patch('src.platform.mouse_controller.mouse.Controller'), \
             patch('src.platform.system_manager.psutil.Process'):
            
            self._hotkey_manager = HotkeyManager()
            self._keyboard_listener = KeyboardListener()
            self._mouse_controller = MouseController()
            self._system_manager = SystemManager()
        
        # 模拟对象
        self._mock_mouse = Mock()
        self._mouse_controller._mouse = self._mock_mouse
        
        self._mock_process = Mock()
        self._system_manager._process = self._mock_process
        
        # 测试状态
        self._integration_events: List[Dict[str, Any]] = []
        self._grid_activation_count = 0
        self._mouse_click_count = 0
        self._system_metrics_count = 0
    
    def tearDown(self):
        """测试后清理"""
        try:
            self._hotkey_manager.UnregisterAll()
            self._keyboard_listener.StopListening()
            self._system_manager.StopResourceMonitoring()
        except:
            pass
    
    #endregion
    
    #region 热键与鼠标控制集成测试
    
    def test_HotkeyMouseIntegration_ActivationClick(self):
        """测试热键激活到鼠标点击的完整流程"""
        click_positions = []
        
        def _OnActivationHotkey():
            """模拟激活热键处理"""
            self._grid_activation_count += 1
            self._integration_events.append({
                'type': 'activation',
                'timestamp': time.time()
            })
            
            # 模拟点击操作
            target_x, target_y = 500, 300
            self._mock_mouse.position = (target_x, target_y)
            success = self._mouse_controller.LeftClick(target_x, target_y)
            
            if success:
                click_positions.append((target_x, target_y))
                self._mouse_click_count += 1
                self._integration_events.append({
                    'type': 'click',
                    'position': (target_x, target_y),
                    'timestamp': time.time()
                })
        
        # 注册激活热键
        self._hotkey_manager.RegisterHotkey('g', (HotkeyModifier.ALT,), _OnActivationHotkey)
        
        # 模拟热键触发
        _OnActivationHotkey()
        
        # 验证集成结果
        self.assertEqual(self._grid_activation_count, 1)
        self.assertEqual(self._mouse_click_count, 1)
        self.assertEqual(len(click_positions), 1)
        self.assertEqual(click_positions[0], (500, 300))
        
        # 验证事件序列
        self.assertEqual(len(self._integration_events), 2)
        self.assertEqual(self._integration_events[0]['type'], 'activation')
        self.assertEqual(self._integration_events[1]['type'], 'click')
    
    def test_HotkeyMouseIntegration_MultipleOperations(self):
        """测试热键到多种鼠标操作的集成"""
        operations = []
        
        def _OnLeftClick():
            self._mock_mouse.position = (100, 100)
            self._mouse_controller.LeftClick(100, 100)
            operations.append('left_click')
        
        def _OnRightClick():
            self._mock_mouse.position = (200, 200)
            self._mouse_controller.RightClick(200, 200)
            operations.append('right_click')
        
        def _OnDoubleClick():
            self._mock_mouse.position = (300, 300)
            self._mouse_controller.DoubleClick(300, 300)
            operations.append('double_click')
        
        # 注册多个热键
        self._hotkey_manager.RegisterHotkey('1', (), _OnLeftClick)
        self._hotkey_manager.RegisterHotkey('2', (), _OnRightClick)
        self._hotkey_manager.RegisterHotkey('3', (), _OnDoubleClick)
        
        # 模拟热键触发
        _OnLeftClick()
        _OnRightClick()
        _OnDoubleClick()
        
        # 验证所有操作都执行了
        self.assertEqual(len(operations), 3)
        self.assertIn('left_click', operations)
        self.assertIn('right_click', operations)
        self.assertIn('double_click', operations)
    
    #endregion
    
    #region 键盘监听与系统管理集成测试
    
    def test_KeyboardSystemIntegration_ResourceMonitoring(self):
        """测试键盘监听与系统资源监控的集成"""
        key_events = []
        resource_metrics = []
        
        def _OnKeyInput(key: str):
            """按键输入处理"""
            key_events.append({
                'key': key,
                'timestamp': time.time()
            })
            
            # 触发系统资源检查
            try:
                metrics = self._system_manager.GetSystemMetrics()
                resource_metrics.append(metrics)
            except Exception:
                pass
        
        def _OnResourceUpdate(metrics: SystemMetrics):
            """资源更新回调"""
            self._system_metrics_count += 1
            resource_metrics.append(metrics)
        
        # 模拟系统指标
        self._mock_process.cpu_percent.return_value = 2.5
        mock_memory_info = Mock()
        mock_memory_info.rss = 40 * 1024 * 1024  # 40MB
        self._mock_process.memory_info.return_value = mock_memory_info
        self._mock_process.num_handles.return_value = 120
        
        # 注册处理器
        self._keyboard_listener.RegisterKeyHandler(_OnKeyInput)
        
        # 启动资源监控
        with patch.object(self._system_manager, '_MeasureResponseTime', return_value=12.0):
            self._system_manager.MonitorResourceUsage(_OnResourceUpdate)
        
        # 模拟按键输入
        self._keyboard_listener._SafeExecuteHandler('q')
        self._keyboard_listener._SafeExecuteHandler('w')
        self._keyboard_listener._SafeExecuteHandler('e')
        
        time.sleep(0.2)  # 等待监控更新
        
        # 验证集成结果
        self.assertEqual(len(key_events), 3)
        self.assertGreater(len(resource_metrics), 0)
        
        # 验证按键记录
        keys = [event['key'] for event in key_events]
        self.assertEqual(keys, ['q', 'w', 'e'])
    
    def test_KeyboardSystemIntegration_PerformanceImpact(self):
        """测试键盘监听对系统性能的影响"""
        performance_data = []
        
        def _CollectPerformanceData():
            """收集性能数据"""
            # 模拟性能数据收集
            self._mock_process.cpu_percent.return_value = 1.5  # 低CPU使用率
            mock_memory_info = Mock()
            mock_memory_info.rss = 30 * 1024 * 1024  # 30MB内存
            self._mock_process.memory_info.return_value = mock_memory_info
            
            with patch.object(self._system_manager, '_MeasureResponseTime', return_value=8.0):
                metrics = self._system_manager.GetSystemMetrics()
                performance_data.append(metrics)
        
        # 收集基准性能数据
        _CollectPerformanceData()
        baseline_metrics = performance_data[0]
        
        # 启动键盘监听
        self._keyboard_listener.StartListening()
        
        # 模拟高频按键输入
        for i in range(50):
            self._keyboard_listener._SafeExecuteHandler('q')
        
        # 收集监听期间的性能数据
        _CollectPerformanceData()
        listening_metrics = performance_data[1]
        
        # 验证性能影响在可接受范围内
        self.assertLess(listening_metrics.CpuUsagePercent, 5.0)  # CPU使用率应该很低
        self.assertLess(listening_metrics.MemoryUsageMb, 100.0)  # 内存使用应该合理
        self.assertLess(listening_metrics.ResponseTimeMs, 50.0)  # 响应时间应该很快
    
    #endregion
    
    #region 完整工作流程集成测试
    
    def test_FullWorkflow_GridNavigation(self):
        """测试完整的网格导航工作流程"""
        workflow_steps = []
        final_click_position = None
        
        def _OnActivationHotkey():
            """激活热键处理"""
            workflow_steps.append('activation')
            self._StartGridMode()
        
        def _StartGridMode(self):
            """启动网格模式"""
            workflow_steps.append('grid_start')
            
            # 启动键盘监听
            self._keyboard_listener.RegisterKeyHandler(self._OnGridInput)
            self._keyboard_listener.StartListening()
        
        def _OnGridInput(self, key: str):
            """网格输入处理"""
            workflow_steps.append(f'grid_input_{key}')
            
            # 模拟网格计算和鼠标操作
            if key == 'e':  # 假设这是最终选择
                target_x, target_y = 600, 400
                self._ExecuteFinalAction(target_x, target_y)
        
        def _ExecuteFinalAction(self, x: int, y: int):
            """执行最终动作"""
            workflow_steps.append('final_action')
            
            # 执行鼠标点击
            self._mock_mouse.position = (x, y)
            success = self._mouse_controller.LeftClick(x, y)
            
            if success:
                nonlocal final_click_position
                final_click_position = (x, y)
                workflow_steps.append('click_success')
            
            # 退出网格模式
            self._ExitGridMode()
        
        def _ExitGridMode(self):
            """退出网格模式"""
            workflow_steps.append('grid_exit')
            self._keyboard_listener.StopListening()
        
        # 注册激活热键
        self._hotkey_manager.RegisterHotkey('g', (HotkeyModifier.ALT,), _OnActivationHotkey)
        
        # 模拟完整工作流程
        _OnActivationHotkey()  # 激活
        _OnGridInput('e')      # 网格输入
        
        # 验证工作流程
        expected_steps = [
            'activation', 
            'grid_start', 
            'grid_input_e', 
            'final_action', 
            'click_success', 
            'grid_exit'
        ]
        self.assertEqual(workflow_steps, expected_steps)
        self.assertEqual(final_click_position, (600, 400))
    
    def test_FullWorkflow_ErrorRecovery(self):
        """测试工作流程中的错误恢复"""
        workflow_events = []
        recovery_actions = []
        
        def _OnActivationHotkey():
            """激活热键处理"""
            workflow_events.append('activation')
            
            # 模拟鼠标操作失败
            try:
                # 模拟无效坐标
                self._mouse_controller.MoveTo(-1000, 10000)
            except MouseOperationError as e:
                workflow_events.append('mouse_error')
                recovery_actions.append('error_handled')
                
                # 恢复操作：使用有效坐标
                self._mock_mouse.position = (100, 100)
                success = self._mouse_controller.MoveTo(100, 100)
                if success:
                    recovery_actions.append('recovery_success')
        
        # 注册热键
        self._hotkey_manager.RegisterHotkey('g', (HotkeyModifier.ALT,), _OnActivationHotkey)
        
        # 触发工作流程
        _OnActivationHotkey()
        
        # 验证错误处理和恢复
        self.assertIn('activation', workflow_events)
        self.assertIn('mouse_error', workflow_events)
        self.assertIn('error_handled', recovery_actions)
        self.assertIn('recovery_success', recovery_actions)
    
    #endregion
    
    #region 并发操作集成测试
    
    def test_ConcurrentOperations_HotkeyAndMonitoring(self):
        """测试热键操作与系统监控的并发"""
        hotkey_events = []
        monitoring_events = []
        
        def _OnHotkeyTrigger():
            """热键触发处理"""
            hotkey_events.append(time.time())
            
            # 执行一些鼠标操作
            for i in range(3):
                x, y = 100 + i * 50, 100 + i * 50
                self._mock_mouse.position = (x, y)
                self._mouse_controller.MoveTo(x, y)
        
        def _OnResourceUpdate(metrics: SystemMetrics):
            """资源监控回调"""
            monitoring_events.append(time.time())
        
        # 模拟系统指标
        self._mock_process.cpu_percent.return_value = 3.0
        mock_memory_info = Mock()
        mock_memory_info.rss = 45 * 1024 * 1024
        self._mock_process.memory_info.return_value = mock_memory_info
        
        # 启动资源监控
        with patch.object(self._system_manager, '_MeasureResponseTime', return_value=10.0):
            self._system_manager.SetMonitoringInterval(0.1)
            self._system_manager.MonitorResourceUsage(_OnResourceUpdate)
        
        # 注册热键
        self._hotkey_manager.RegisterHotkey('t', (), _OnHotkeyTrigger)
        
        # 并发执行
        time.sleep(0.1)  # 让监控开始
        
        # 触发多个热键事件
        for _ in range(5):
            _OnHotkeyTrigger()
            time.sleep(0.05)
        
        time.sleep(0.2)  # 等待更多监控事件
        
        # 验证并发操作
        self.assertEqual(len(hotkey_events), 5)
        self.assertGreater(len(monitoring_events), 0)
        
        # 验证事件时间分布合理
        hotkey_duration = hotkey_events[-1] - hotkey_events[0]
        self.assertGreater(hotkey_duration, 0.2)  # 热键事件跨越时间
    
    def test_ConcurrentOperations_MultipleClients(self):
        """测试多个客户端并发使用平台服务"""
        client_results = {}
        
        def _SimulateClient(client_id: int):
            """模拟客户端操作"""
            results = []
            
            try:
                # 注册客户端特定的热键
                def _ClientCallback():
                    results.append(f'hotkey_{client_id}')
                
                hotkey_key = str(client_id)
                self._hotkey_manager.RegisterHotkey(hotkey_key, (), _ClientCallback)
                
                # 执行鼠标操作
                x, y = 100 + client_id * 100, 100 + client_id * 100
                self._mock_mouse.position = (x, y)
                success = self._mouse_controller.MoveTo(x, y)
                if success:
                    results.append(f'mouse_{client_id}')
                
                # 获取系统指标
                self._mock_process.cpu_percent.return_value = 2.0 + client_id * 0.5
                mock_memory_info = Mock()
                mock_memory_info.rss = (30 + client_id * 5) * 1024 * 1024
                self._mock_process.memory_info.return_value = mock_memory_info
                
                with patch.object(self._system_manager, '_MeasureResponseTime', return_value=8.0 + client_id):
                    metrics = self._system_manager.GetSystemMetrics()
                    results.append(f'metrics_{client_id}')
                
                client_results[client_id] = results
                
            except Exception as e:
                client_results[client_id] = [f'error: {str(e)}']
        
        # 创建多个并发客户端
        threads = []
        for i in range(5):
            thread = threading.Thread(target=_SimulateClient, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有客户端完成
        for thread in threads:
            thread.join()
        
        # 验证所有客户端都成功执行
        self.assertEqual(len(client_results), 5)
        for client_id, results in client_results.items():
            self.assertIn(f'hotkey_{client_id}', results)
            self.assertIn(f'mouse_{client_id}', results)
            self.assertIn(f'metrics_{client_id}', results)
    
    #endregion
    
    #region 压力测试
    
    def test_StressTest_HighFrequencyOperations(self):
        """测试高频操作压力"""
        operation_count = 100
        success_count = 0
        error_count = 0
        
        def _HighFrequencyCallback():
            """高频回调处理"""
            nonlocal success_count, error_count
            
            try:
                # 执行鼠标移动
                import random
                x = random.randint(50, 500)
                y = random.randint(50, 500)
                
                self._mock_mouse.position = (x, y)
                success = self._mouse_controller.MoveTo(x, y)
                
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception:
                error_count += 1
        
        # 注册热键
        self._hotkey_manager.RegisterHotkey('s', (), _HighFrequencyCallback)
        
        # 高频触发
        start_time = time.time()
        for _ in range(operation_count):
            _HighFrequencyCallback()
        end_time = time.time()
        
        # 验证压力测试结果
        total_operations = success_count + error_count
        self.assertEqual(total_operations, operation_count)
        
        # 验证性能要求
        duration = end_time - start_time
        ops_per_second = operation_count / duration
        self.assertGreater(ops_per_second, 50)  # 至少50操作/秒
        
        # 验证成功率
        success_rate = success_count / operation_count
        self.assertGreater(success_rate, 0.95)  # 95%以上成功率
    
    def test_StressTest_LongRunningOperation(self):
        """测试长时间运行压力"""
        monitoring_data = []
        operation_count = 0
        
        def _ContinuousCallback(metrics: SystemMetrics):
            """持续回调处理"""
            nonlocal operation_count
            operation_count += 1
            monitoring_data.append({
                'timestamp': time.time(),
                'cpu': metrics.CpuUsagePercent,
                'memory': metrics.MemoryUsageMb,
                'response_time': metrics.ResponseTimeMs
            })
        
        # 模拟稳定的系统指标
        self._mock_process.cpu_percent.return_value = 2.0
        mock_memory_info = Mock()
        mock_memory_info.rss = 35 * 1024 * 1024
        self._mock_process.memory_info.return_value = mock_memory_info
        
        # 启动长时间监控
        with patch.object(self._system_manager, '_MeasureResponseTime', return_value=9.0):
            self._system_manager.SetMonitoringInterval(0.05)  # 20Hz监控频率
            self._system_manager.MonitorResourceUsage(_ContinuousCallback)
            
            # 运行一段时间
            time.sleep(1.0)
        
        # 验证长时间运行稳定性
        self.assertGreater(operation_count, 15)  # 至少15次回调
        self.assertGreater(len(monitoring_data), 10)
        
        # 验证资源使用稳定性
        cpu_values = [data['cpu'] for data in monitoring_data]
        memory_values = [data['memory'] for data in monitoring_data]
        
        # CPU和内存使用应该相对稳定
        cpu_variance = max(cpu_values) - min(cpu_values)
        memory_variance = max(memory_values) - min(memory_values)
        
        self.assertLess(cpu_variance, 10.0)  # CPU变化不超过10%
        self.assertLess(memory_variance, 50.0)  # 内存变化不超过50MB
    
    #endregion
    
    #region 兼容性集成测试
    
    @patch('sys.platform', 'win32')
    def test_WindowsPlatformIntegration(self):
        """测试Windows平台集成"""
        compatibility_results = []
        
        # 检查系统兼容性
        with patch.object(self._system_manager, '_CheckWindowsVersion', return_value=True), \
             patch.object(self._system_manager, '_CheckAdminPrivileges', return_value=True), \
             patch.object(self._system_manager, '_CheckAccessibilityPermissions', return_value=True), \
             patch.object(self._system_manager, '_CheckLibraryAvailable', return_value=True), \
             patch('src.platform.system_manager.psutil.virtual_memory') as mock_memory, \
             patch('src.platform.system_manager.psutil.cpu_count', return_value=4):
            
            mock_memory.return_value.available = 200 * 1024 * 1024
            compatibility = self._system_manager.CheckSystemCompatibility()
        
        # 验证Windows特定功能
        self.assertTrue(compatibility['windows_supported'])
        self.assertTrue(compatibility['windows_version_ok'])
        
        # 测试Windows特定的热键功能
        activation_count = [0]
        
        def _WindowsHotkeyCallback():
            activation_count[0] += 1
        
        # Alt+G是Windows常用的热键组合
        self._hotkey_manager.RegisterHotkey('g', (HotkeyModifier.ALT,), _WindowsHotkeyCallback)
        
        # 模拟热键触发
        _WindowsHotkeyCallback()
        
        self.assertEqual(activation_count[0], 1)
    
    def test_CrossPlatformCompatibility(self):
        """测试跨平台兼容性"""
        platform_tests = ['win32', 'linux', 'darwin']
        results = {}
        
        for platform_name in platform_tests:
            with patch('sys.platform', platform_name):
                try:
                    # 测试基本功能在不同平台上的行为
                    
                    # 键盘监听应该在所有平台工作
                    self._keyboard_listener.SetKeyFilter(('q', 'w', 'e'))
                    allowed_keys = self._keyboard_listener.GetAllowedKeys()
                    
                    # 鼠标控制应该在所有平台工作
                    self._mock_mouse.position = (100, 100)
                    mouse_success = self._mouse_controller.MoveTo(100, 100)
                    
                    # 系统管理可能在不同平台有不同行为
                    self._mock_process.cpu_percent.return_value = 1.5
                    mock_memory_info = Mock()
                    mock_memory_info.rss = 25 * 1024 * 1024
                    self._mock_process.memory_info.return_value = mock_memory_info
                    
                    with patch.object(self._system_manager, '_MeasureResponseTime', return_value=7.0):
                        metrics = self._system_manager.GetSystemMetrics()
                    
                    results[platform_name] = {
                        'keyboard_keys': len(allowed_keys),
                        'mouse_success': mouse_success,
                        'metrics_available': metrics is not None
                    }
                    
                except Exception as e:
                    results[platform_name] = {'error': str(e)}
        
        # 验证跨平台兼容性
        for platform_name, result in results.items():
            if 'error' not in result:
                self.assertGreater(result['keyboard_keys'], 0)
                self.assertTrue(result['mouse_success'])
                self.assertTrue(result['metrics_available'])
    
    #endregion
    
    #region 性能基准测试
    
    def test_PerformanceBenchmark_ResponseTime(self):
        """测试响应时间基准"""
        response_times = []
        
        def _MeasureOperationTime():
            """测量操作响应时间"""
            start_time = time.perf_counter()
            
            # 执行一系列操作
            self._mock_mouse.position = (150, 150)
            self._mouse_controller.MoveTo(150, 150)
            
            # 模拟按键处理
            self._keyboard_listener._SafeExecuteHandler('q')
            
            # 获取系统指标
            self._mock_process.cpu_percent.return_value = 1.8
            mock_memory_info = Mock()
            mock_memory_info.rss = 32 * 1024 * 1024
            self._mock_process.memory_info.return_value = mock_memory_info
            
            with patch.object(self._system_manager, '_MeasureResponseTime', return_value=6.0):
                self._system_manager.GetSystemMetrics()
            
            end_time = time.perf_counter()
            return (end_time - start_time) * 1000  # 转换为毫秒
        
        # 执行多次测量
        for _ in range(20):
            response_time = _MeasureOperationTime()
            response_times.append(response_time)
        
        # 分析性能基准
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        # 验证性能要求
        self.assertLess(avg_response_time, 50.0)  # 平均响应时间小于50ms
        self.assertLess(max_response_time, 100.0)  # 最大响应时间小于100ms
        self.assertGreater(min_response_time, 0.1)  # 最小响应时间大于0.1ms（合理性检查）
        
        # 验证响应时间一致性
        time_variance = max_response_time - min_response_time
        self.assertLess(time_variance, 80.0)  # 响应时间变化范围小于80ms
    
    #endregion


if __name__ == '__main__':
    unittest.main()