# -*- coding: utf-8 -*-
"""
SystemManager 单元测试
测试系统资源管理器的所有功能
"""

import unittest
import threading
import time
import sys
import platform
from unittest.mock import Mock, patch, MagicMock, call
from typing import Dict, Any

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.platform.system_manager import SystemManager
from src.platform.interfaces import SystemMetrics, SystemResourceError


class TestSystemManager(unittest.TestCase):
    """SystemManager 测试类"""
    
    #region 测试初始化和清理
    
    def setUp(self):
        """测试前初始化"""
        with patch('src.platform.system_manager.psutil.Process'):
            self._manager = SystemManager()
        
        # 模拟psutil.Process
        self._mock_process = Mock()
        self._manager._process = self._mock_process
        
        # 测试回调相关
        self._callback_call_count = 0
        self._received_metrics = []
    
    def tearDown(self):
        """测试后清理"""
        try:
            self._manager.StopResourceMonitoring()
        except:
            pass
    
    def _TestCallback(self, metrics: SystemMetrics):
        """测试回调函数"""
        self._callback_call_count += 1
        self._received_metrics.append(metrics)
    
    #endregion
    
    #region 系统指标获取测试
    
    def test_GetSystemMetrics_Success(self):
        """测试成功获取系统指标"""
        # 模拟返回数据
        self._mock_process.cpu_percent.return_value = 5.5
        
        mock_memory_info = Mock()
        mock_memory_info.rss = 50 * 1024 * 1024  # 50MB
        self._mock_process.memory_info.return_value = mock_memory_info
        
        self._mock_process.num_handles.return_value = 150
        
        with patch.object(self._manager, '_MeasureResponseTime', return_value=15.5):
            metrics = self._manager.GetSystemMetrics()
        
        self.assertIsInstance(metrics, SystemMetrics)
        self.assertEqual(metrics.CpuUsagePercent, 5.5)
        self.assertEqual(metrics.MemoryUsageMb, 50.0)
        self.assertEqual(metrics.HandleCount, 150)
        self.assertEqual(metrics.ResponseTimeMs, 15.5)
    
    def test_GetSystemMetrics_NoHandles(self):
        """测试在不支持句柄的系统上获取指标"""
        # 模拟没有num_handles方法的情况
        self._mock_process.cpu_percent.return_value = 3.2
        
        mock_memory_info = Mock()
        mock_memory_info.rss = 30 * 1024 * 1024
        self._mock_process.memory_info.return_value = mock_memory_info
        
        # 删除num_handles属性
        del self._mock_process.num_handles
        
        with patch.object(self._manager, '_MeasureResponseTime', return_value=12.0):
            metrics = self._manager.GetSystemMetrics()
        
        self.assertEqual(metrics.HandleCount, 0)  # 应该返回0
    
    def test_GetSystemMetrics_HandleException(self):
        """测试获取句柄数异常"""
        self._mock_process.cpu_percent.return_value = 4.0
        
        mock_memory_info = Mock()
        mock_memory_info.rss = 40 * 1024 * 1024
        self._mock_process.memory_info.return_value = mock_memory_info
        
        # 模拟num_handles抛出异常
        self._mock_process.num_handles.side_effect = Exception("句柄获取失败")
        
        with patch.object(self._manager, '_MeasureResponseTime', return_value=10.0):
            metrics = self._manager.GetSystemMetrics()
        
        self.assertEqual(metrics.HandleCount, 0)  # 异常时应该返回0
    
    def test_GetSystemMetrics_Exception(self):
        """测试获取系统指标异常"""
        self._mock_process.cpu_percent.side_effect = Exception("CPU获取失败")
        
        with self.assertRaises(SystemResourceError):
            self._manager.GetSystemMetrics()
    
    #endregion
    
    #region 进程优先级测试
    
    @patch('sys.platform', 'win32')
    @patch('src.platform.system_manager.psutil')
    def test_SetProcessPriority_Windows_Normal(self, mock_psutil):
        """测试在Windows上设置正常优先级"""
        mock_psutil.NORMAL_PRIORITY_CLASS = 32
        
        result = self._manager.SetProcessPriority('normal')
        
        self.assertTrue(result)
        self._mock_process.nice.assert_called_once_with(32)
    
    @patch('sys.platform', 'win32')
    @patch('src.platform.system_manager.psutil')
    def test_SetProcessPriority_Windows_High(self, mock_psutil):
        """测试在Windows上设置高优先级"""
        mock_psutil.ABOVE_NORMAL_PRIORITY_CLASS = 128
        
        result = self._manager.SetProcessPriority('high')
        
        self.assertTrue(result)
        self._mock_process.nice.assert_called_once_with(128)
    
    @patch('sys.platform', 'linux')
    @patch('os.nice')
    def test_SetProcessPriority_Linux_Normal(self, mock_os_nice):
        """测试在Linux上设置正常优先级"""
        result = self._manager.SetProcessPriority('normal')
        
        self.assertTrue(result)
        mock_os_nice.assert_called_once_with(0)
    
    @patch('sys.platform', 'linux')
    @patch('os.nice')
    def test_SetProcessPriority_Linux_High(self, mock_os_nice):
        """测试在Linux上设置高优先级"""
        result = self._manager.SetProcessPriority('high')
        
        self.assertTrue(result)
        mock_os_nice.assert_called_once_with(-10)
    
    def test_SetProcessPriority_InvalidPriority(self):
        """测试设置无效优先级"""
        with self.assertRaises(SystemResourceError):
            self._manager.SetProcessPriority('invalid')
    
    def test_SetProcessPriority_Exception(self):
        """测试设置优先级异常"""
        self._mock_process.nice.side_effect = Exception("设置优先级失败")
        
        with self.assertRaises(SystemResourceError):
            self._manager.SetProcessPriority('normal')
    
    #endregion
    
    #region 系统兼容性检查测试
    
    @patch('sys.platform', 'win32')
    @patch('sys.version_info', (3, 8, 0))
    def test_CheckSystemCompatibility_Windows_Success(self):
        """测试Windows系统兼容性检查成功"""
        with patch.object(self._manager, '_CheckWindowsVersion', return_value=True), \
             patch.object(self._manager, '_CheckAdminPrivileges', return_value=True), \
             patch.object(self._manager, '_CheckAccessibilityPermissions', return_value=True), \
             patch.object(self._manager, '_CheckLibraryAvailable', return_value=True), \
             patch('src.platform.system_manager.psutil.virtual_memory') as mock_memory, \
             patch('src.platform.system_manager.psutil.cpu_count', return_value=4):
            
            mock_memory.return_value.available = 200 * 1024 * 1024  # 200MB
            
            compatibility = self._manager.CheckSystemCompatibility()
        
        self.assertTrue(compatibility['windows_supported'])
        self.assertTrue(compatibility['windows_version_ok'])
        self.assertTrue(compatibility['python_version_ok'])
        self.assertTrue(compatibility['admin_privileges'])
        self.assertTrue(compatibility['accessibility_permissions'])
        self.assertTrue(compatibility['pynput_available'])
        self.assertTrue(compatibility['psutil_available'])
        self.assertTrue(compatibility['pyqt6_available'])
        self.assertTrue(compatibility['sufficient_memory'])
        self.assertTrue(compatibility['cpu_cores_ok'])
    
    @patch('sys.platform', 'linux')
    @patch('sys.version_info', (3, 6, 0))
    def test_CheckSystemCompatibility_Linux_OldPython(self):
        """测试Linux系统旧Python版本"""
        with patch.object(self._manager, '_CheckWindowsVersion', return_value=False), \
             patch.object(self._manager, '_CheckAdminPrivileges', return_value=False), \
             patch.object(self._manager, '_CheckAccessibilityPermissions', return_value=True), \
             patch.object(self._manager, '_CheckLibraryAvailable', return_value=False), \
             patch('src.platform.system_manager.psutil.virtual_memory') as mock_memory, \
             patch('src.platform.system_manager.psutil.cpu_count', return_value=1):
            
            mock_memory.return_value.available = 50 * 1024 * 1024  # 50MB，不足
            
            compatibility = self._manager.CheckSystemCompatibility()
        
        self.assertFalse(compatibility['windows_supported'])
        self.assertFalse(compatibility['windows_version_ok'])
        self.assertFalse(compatibility['python_version_ok'])  # Python 3.6 < 3.7
        self.assertFalse(compatibility['admin_privileges'])
        self.assertFalse(compatibility['pynput_available'])
        self.assertFalse(compatibility['sufficient_memory'])
        self.assertTrue(compatibility['cpu_cores_ok'])
    
    def test_CheckSystemCompatibility_Exception(self):
        """测试兼容性检查异常"""
        with patch('sys.platform', side_effect=Exception("系统平台检查失败")):
            compatibility = self._manager.CheckSystemCompatibility()
        
        self.assertIn('error', compatibility)
        self.assertTrue(compatibility['compatibility_check_failed'])
    
    #endregion
    
    #region Windows版本检查测试
    
    @patch('sys.platform', 'win32')
    @patch('src.platform.system_manager.platform.version')
    def test_CheckWindowsVersion_Windows10(self, mock_version):
        """测试Windows 10版本检查"""
        mock_version.return_value = "10.0.19041"
        
        result = self._manager._CheckWindowsVersion()
        self.assertTrue(result)
    
    @patch('sys.platform', 'win32')
    @patch('src.platform.system_manager.platform.version')
    def test_CheckWindowsVersion_Windows11(self, mock_version):
        """测试Windows 11版本检查"""
        mock_version.return_value = "10.0.22000"  # Windows 11仍然报告为10.0
        
        result = self._manager._CheckWindowsVersion()
        self.assertTrue(result)
    
    @patch('sys.platform', 'win32')
    @patch('src.platform.system_manager.platform.version')
    def test_CheckWindowsVersion_OldWindows(self, mock_version):
        """测试旧版Windows"""
        mock_version.return_value = "6.1.7601"  # Windows 7
        
        result = self._manager._CheckWindowsVersion()
        self.assertFalse(result)
    
    @patch('sys.platform', 'linux')
    def test_CheckWindowsVersion_NonWindows(self):
        """测试非Windows系统"""
        result = self._manager._CheckWindowsVersion()
        self.assertFalse(result)
    
    @patch('sys.platform', 'win32')
    @patch('src.platform.system_manager.platform.version')
    def test_CheckWindowsVersion_Exception(self, mock_version):
        """测试版本检查异常"""
        mock_version.side_effect = Exception("版本获取失败")
        
        result = self._manager._CheckWindowsVersion()
        self.assertFalse(result)
    
    #endregion
    
    #region 管理员权限检查测试
    
    @patch('sys.platform', 'win32')
    @patch('ctypes.windll.shell32.IsUserAnAdmin')
    def test_CheckAdminPrivileges_Windows_Admin(self, mock_is_admin):
        """测试Windows管理员权限"""
        mock_is_admin.return_value = 1
        
        result = self._manager._CheckAdminPrivileges()
        self.assertTrue(result)
    
    @patch('sys.platform', 'win32')
    @patch('ctypes.windll.shell32.IsUserAnAdmin')
    def test_CheckAdminPrivileges_Windows_NoAdmin(self, mock_is_admin):
        """测试Windows非管理员权限"""
        mock_is_admin.return_value = 0
        
        result = self._manager._CheckAdminPrivileges()
        self.assertFalse(result)
    
    @patch('sys.platform', 'linux')
    @patch('os.geteuid')
    def test_CheckAdminPrivileges_Linux_Root(self, mock_geteuid):
        """测试Linux root权限"""
        mock_geteuid.return_value = 0
        
        result = self._manager._CheckAdminPrivileges()
        self.assertTrue(result)
    
    @patch('sys.platform', 'linux')
    @patch('os.geteuid')
    def test_CheckAdminPrivileges_Linux_User(self, mock_geteuid):
        """测试Linux普通用户权限"""
        mock_geteuid.return_value = 1000
        
        result = self._manager._CheckAdminPrivileges()
        self.assertFalse(result)
    
    def test_CheckAdminPrivileges_Exception(self):
        """测试权限检查异常"""
        with patch('ctypes.windll.shell32.IsUserAnAdmin', side_effect=Exception("权限检查失败")):
            result = self._manager._CheckAdminPrivileges()
            self.assertFalse(result)
    
    #endregion
    
    #region 辅助功能权限检查测试
    
    @patch('sys.platform', 'win32')
    @patch('src.platform.system_manager.mouse')
    @patch('time.sleep')
    def test_CheckAccessibilityPermissions_Windows_Success(self, mock_sleep, mock_mouse):
        """测试Windows辅助功能权限检查成功"""
        mock_listener = Mock()
        mock_mouse.Listener.return_value = mock_listener
        
        result = self._manager._CheckAccessibilityPermissions()
        
        self.assertTrue(result)
        mock_listener.start.assert_called_once()
        mock_listener.stop.assert_called_once()
    
    @patch('sys.platform', 'win32')
    @patch('src.platform.system_manager.mouse')
    def test_CheckAccessibilityPermissions_Windows_Failed(self, mock_mouse):
        """测试Windows辅助功能权限检查失败"""
        mock_mouse.Listener.side_effect = Exception("权限不足")
        
        result = self._manager._CheckAccessibilityPermissions()
        self.assertFalse(result)
    
    @patch('sys.platform', 'linux')
    def test_CheckAccessibilityPermissions_NonWindows(self):
        """测试非Windows系统权限检查"""
        result = self._manager._CheckAccessibilityPermissions()
        self.assertTrue(result)  # 非Windows系统假设有权限
    
    #endregion
    
    #region 库可用性检查测试
    
    def test_CheckLibraryAvailable_Available(self):
        """测试可用库检查"""
        # 使用已知存在的库
        result = self._manager._CheckLibraryAvailable('sys')
        self.assertTrue(result)
    
    def test_CheckLibraryAvailable_NotAvailable(self):
        """测试不可用库检查"""
        result = self._manager._CheckLibraryAvailable('nonexistent_library_12345')
        self.assertFalse(result)
    
    def test_CheckLibraryAvailable_MockLibrary(self):
        """测试模拟库检查"""
        with patch('builtins.__import__', side_effect=ImportError("库不存在")):
            result = self._manager._CheckLibraryAvailable('test_lib')
            self.assertFalse(result)
    
    #endregion
    
    #region 资源监控测试
    
    def test_MonitorResourceUsage_Start(self):
        """测试开始资源监控"""
        self._manager.MonitorResourceUsage(self._TestCallback)
        
        # 等待监控线程启动
        time.sleep(0.1)
        
        status = self._manager.GetMonitoringStatus()
        self.assertTrue(status['is_monitoring'])
        self.assertTrue(status['has_callback'])
        self.assertTrue(status['thread_alive'])
    
    def test_MonitorResourceUsage_Stop(self):
        """测试停止资源监控"""
        self._manager.MonitorResourceUsage(self._TestCallback)
        time.sleep(0.1)
        
        self._manager.StopResourceMonitoring()
        time.sleep(0.1)
        
        status = self._manager.GetMonitoringStatus()
        self.assertFalse(status['is_monitoring'])
        self.assertFalse(status['has_callback'])
    
    def test_MonitorResourceUsage_Replace(self):
        """测试替换监控回调"""
        # 启动第一个监控
        self._manager.MonitorResourceUsage(self._TestCallback)
        time.sleep(0.1)
        
        # 启动第二个监控（应该停止第一个）
        callback2_call_count = [0]
        def _Callback2(metrics):
            callback2_call_count[0] += 1
        
        self._manager.MonitorResourceUsage(_Callback2)
        time.sleep(0.2)
        
        status = self._manager.GetMonitoringStatus()
        self.assertTrue(status['is_monitoring'])
    
    def test_MonitorResourceUsage_Exception(self):
        """测试监控启动异常"""
        with patch('threading.Thread', side_effect=Exception("线程创建失败")):
            with self.assertRaises(SystemResourceError):
                self._manager.MonitorResourceUsage(self._TestCallback)
    
    @patch.object(SystemManager, 'GetSystemMetrics')
    def test_MonitoringLoop_Callback(self, mock_get_metrics):
        """测试监控循环回调执行"""
        # 模拟系统指标
        test_metrics = SystemMetrics(
            CpuUsagePercent=5.0,
            MemoryUsageMb=50.0,
            HandleCount=100,
            ResponseTimeMs=10.0
        )
        mock_get_metrics.return_value = test_metrics
        
        # 设置较短的监控间隔
        self._manager.SetMonitoringInterval(0.1)
        
        self._manager.MonitorResourceUsage(self._TestCallback)
        time.sleep(0.3)  # 等待几次回调
        self._manager.StopResourceMonitoring()
        
        # 验证回调被调用
        self.assertGreater(self._callback_call_count, 0)
        self.assertGreater(len(self._received_metrics), 0)
        self.assertEqual(self._received_metrics[0].CpuUsagePercent, 5.0)
    
    def test_MonitoringLoop_CallbackException(self):
        """测试监控回调异常处理"""
        def _ErrorCallback(metrics):
            raise ValueError("回调异常")
        
        # 模拟系统指标
        with patch.object(self._manager, 'GetSystemMetrics') as mock_get_metrics:
            test_metrics = SystemMetrics(
                CpuUsagePercent=3.0,
                MemoryUsageMb=40.0,
                HandleCount=80,
                ResponseTimeMs=8.0
            )
            mock_get_metrics.return_value = test_metrics
            
            self._manager.SetMonitoringInterval(0.1)
            self._manager.MonitorResourceUsage(_ErrorCallback)
            time.sleep(0.3)  # 监控应该继续运行，不被异常中断
            
            status = self._manager.GetMonitoringStatus()
            self.assertTrue(status['is_monitoring'])  # 监控应该仍在运行
    
    #endregion
    
    #region 响应时间测量测试
    
    @patch('time.perf_counter')
    @patch('os.getpid')
    def test_MeasureResponseTime(self, mock_getpid, mock_perf_counter):
        """测试响应时间测量"""
        # 模拟时间差
        mock_perf_counter.side_effect = [1.0, 1.015]  # 15ms差异
        mock_getpid.return_value = 1234
        
        response_time = self._manager._MeasureResponseTime()
        
        self.assertEqual(response_time, 15.0)  # 15ms
        mock_getpid.assert_called_once()
    
    def test_MeasureResponseTime_Exception(self):
        """测试响应时间测量异常"""
        with patch('os.getpid', side_effect=Exception("系统调用失败")):
            response_time = self._manager._MeasureResponseTime()
            self.assertEqual(response_time, 0.0)
    
    #endregion
    
    #region 扩展功能测试
    
    @patch('src.platform.system_manager.platform.platform')
    @patch('src.platform.system_manager.platform.architecture')
    @patch('src.platform.system_manager.platform.processor')
    @patch('src.platform.system_manager.platform.python_version')
    @patch('src.platform.system_manager.psutil')
    def test_GetDetailedSystemInfo(self, mock_psutil, mock_python_version, 
                                   mock_processor, mock_architecture, mock_platform):
        """测试获取详细系统信息"""
        # 模拟返回值
        mock_platform.return_value = "Windows-10-10.0.19041-SP0"
        mock_architecture.return_value = ('64bit', 'WindowsPE')
        mock_processor.return_value = "Intel64 Family 6 Model 142 Stepping 10, GenuineIntel"
        mock_python_version.return_value = "3.8.5"
        
        # 模拟内存信息
        mock_memory = Mock()
        mock_memory.total = 16 * 1024**3  # 16GB
        mock_memory.available = 8 * 1024**3  # 8GB
        mock_psutil.virtual_memory.return_value = mock_memory
        
        # 模拟CPU信息
        mock_psutil.cpu_count.return_value = 8
        mock_cpu_freq = Mock()
        mock_cpu_freq._asdict.return_value = {'current': 2400, 'min': 400, 'max': 3400}
        mock_psutil.cpu_freq.return_value = mock_cpu_freq
        
        # 模拟磁盘信息
        mock_disk = Mock()
        mock_disk.total = 1024**4  # 1TB
        mock_disk.free = 512**4   # 512GB
        mock_psutil.disk_usage.return_value = mock_disk
        
        info = self._manager.GetDetailedSystemInfo()
        
        self.assertIn('platform', info)
        self.assertIn('architecture', info)
        self.assertIn('processor', info)
        self.assertIn('python_version', info)
        self.assertIn('total_memory_gb', info)
        self.assertIn('cpu_count', info)
        self.assertEqual(info['cpu_count'], 8)
    
    def test_GetDetailedSystemInfo_Cached(self):
        """测试系统信息缓存"""
        # 第一次调用
        with patch.object(self._manager, '_CollectSystemInfo', return_value={'test': 'data'}) as mock_collect:
            info1 = self._manager.GetDetailedSystemInfo()
            self.assertEqual(mock_collect.call_count, 1)
        
        # 第二次调用应该使用缓存
        info2 = self._manager.GetDetailedSystemInfo()
        self.assertEqual(mock_collect.call_count, 1)  # 不应该再次调用
        self.assertEqual(info1, info2)
    
    def test_GetDetailedSystemInfo_Exception(self):
        """测试获取详细信息异常"""
        with patch.object(self._manager, '_CollectSystemInfo', side_effect=Exception("信息收集失败")):
            info = self._manager.GetDetailedSystemInfo()
            self.assertIn('error', info)
    
    def test_SetMonitoringInterval(self):
        """测试设置监控间隔"""
        self._manager.SetMonitoringInterval(2.0)
        
        status = self._manager.GetMonitoringStatus()
        self.assertEqual(status['monitor_interval'], 2.0)
    
    def test_SetMonitoringInterval_BoundaryValues(self):
        """测试监控间隔边界值"""
        # 测试最小值
        self._manager.SetMonitoringInterval(0.05)
        status = self._manager.GetMonitoringStatus()
        self.assertEqual(status['monitor_interval'], 0.1)  # 应该被限制为最小值
        
        # 测试最大值
        self._manager.SetMonitoringInterval(120)
        status = self._manager.GetMonitoringStatus()
        self.assertEqual(status['monitor_interval'], 60.0)  # 应该被限制为最大值
    
    def test_OptimizeForPerformance(self):
        """测试性能优化"""
        with patch.object(self._manager, 'SetProcessPriority', return_value=True), \
             patch('gc.disable') as mock_gc_disable:
            
            results = self._manager.OptimizeForPerformance()
        
        self.assertTrue(results['priority_set'])
        self.assertTrue(results['gc_disabled'])
        mock_gc_disable.assert_called_once()
    
    def test_OptimizeForPerformance_Exception(self):
        """测试性能优化异常"""
        with patch.object(self._manager, 'SetProcessPriority', side_effect=Exception("优先级设置失败")), \
             patch('gc.disable', side_effect=Exception("GC禁用失败")):
            
            results = self._manager.OptimizeForPerformance()
        
        self.assertFalse(results['priority_set'])
        self.assertFalse(results['gc_disabled'])
    
    def test_RestoreDefaultSettings(self):
        """测试恢复默认设置"""
        with patch.object(self._manager, 'SetProcessPriority', return_value=True), \
             patch('gc.enable') as mock_gc_enable:
            
            results = self._manager.RestoreDefaultSettings()
        
        self.assertTrue(results['priority_restored'])
        self.assertTrue(results['gc_enabled'])
        mock_gc_enable.assert_called_once()
    
    #endregion
    
    #region 线程安全测试
    
    def test_ThreadSafety_ConcurrentMonitoring(self):
        """测试并发监控的线程安全性"""
        import threading
        
        results = []
        
        def _StartMonitoring(index):
            def _Callback(metrics):
                results.append(index)
            
            try:
                self._manager.MonitorResourceUsage(_Callback)
                time.sleep(0.1)
                self._manager.StopResourceMonitoring()
            except Exception:
                pass
        
        # 创建多个线程并发启动监控
        threads = []
        for i in range(5):
            thread = threading.Thread(target=_StartMonitoring, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证没有异常发生
        self.assertFalse(self._manager.GetMonitoringStatus()['is_monitoring'])
    
    def test_ThreadSafety_ConcurrentConfiguration(self):
        """测试并发配置的线程安全性"""
        import threading
        
        def _SetInterval(interval):
            self._manager.SetMonitoringInterval(interval)
        
        # 创建多个线程并发设置配置
        threads = []
        for i in range(10):
            thread = threading.Thread(target=_SetInterval, args=(0.5 + i * 0.1,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证最终状态一致性
        status = self._manager.GetMonitoringStatus()
        self.assertIsInstance(status['monitor_interval'], (int, float))
        self.assertGreaterEqual(status['monitor_interval'], 0.1)
    
    #endregion
    
    #region 资源清理测试
    
    def test_ResourceCleanup_Destructor(self):
        """测试析构函数资源清理"""
        manager = SystemManager()
        
        with patch.object(manager, 'StopResourceMonitoring') as mock_stop:
            manager.__del__()
            mock_stop.assert_called_once()
    
    def test_ResourceCleanup_Exception(self):
        """测试析构函数异常处理"""
        manager = SystemManager()
        
        # 模拟StopResourceMonitoring抛出异常
        with patch.object(manager, 'StopResourceMonitoring', side_effect=Exception("停止失败")):
            try:
                manager.__del__()  # 不应该抛出异常
            except Exception:
                self.fail("析构函数异常没有被正确处理")
    
    #endregion
    
    #region 边界条件测试
    
    def test_MonitoringInterval_EdgeCases(self):
        """测试监控间隔边界情况"""
        edge_cases = [0, -1, 0.09, 60.1, 1000]
        
        for interval in edge_cases:
            self._manager.SetMonitoringInterval(interval)
            status = self._manager.GetMonitoringStatus()
            
            # 验证间隔在有效范围内
            self.assertGreaterEqual(status['monitor_interval'], 0.1)
            self.assertLessEqual(status['monitor_interval'], 60.0)
    
    def test_EmptyCallback(self):
        """测试空回调函数"""
        try:
            self._manager.MonitorResourceUsage(None)
        except Exception:
            self.fail("None回调不应该抛出异常")
    
    #endregion


if __name__ == '__main__':
    unittest.main()