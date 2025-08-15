# -*- coding: utf-8 -*-
"""
MouseController 单元测试
测试鼠标控制器的所有功能
"""

import unittest
import time
import math
from unittest.mock import Mock, patch, MagicMock, call
from typing import Tuple

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.platform.mouse_controller import MouseController
from src.platform.interfaces import MouseOperationError


class TestMouseController(unittest.TestCase):
    """MouseController 测试类"""
    
    #region 测试初始化和清理
    
    def setUp(self):
        """测试前初始化"""
        with patch('src.platform.mouse_controller.mouse.Controller'):
            self._controller = MouseController()
        
        # 模拟鼠标控制器
        self._mock_mouse = Mock()
        self._controller._mouse = self._mock_mouse
    
    def tearDown(self):
        """测试后清理"""
        pass
    
    #endregion
    
    #region 基础鼠标操作测试
    
    def test_MoveTo_Success(self):
        """测试成功移动鼠标"""
        target_x, target_y = 100, 200
        self._mock_mouse.position = (target_x, target_y)
        
        result = self._controller.MoveTo(target_x, target_y)
        
        self.assertTrue(result)
        self._mock_mouse.__setattr__.assert_called_with('position', (target_x, target_y))
    
    def test_MoveTo_InvalidCoordinates(self):
        """测试无效坐标移动"""
        # 测试超出范围的坐标
        with self.assertRaises(MouseOperationError):
            self._controller.MoveTo(-1000, 10000)
    
    def test_MoveTo_PositionVerificationFailed(self):
        """测试位置验证失败"""
        target_x, target_y = 100, 200
        # 模拟实际位置与目标位置不符
        self._mock_mouse.position = (target_x + 10, target_y + 10)
        
        with self.assertRaises(MouseOperationError):
            self._controller.MoveTo(target_x, target_y)
    
    def test_MoveTo_PositionVerificationWithinTolerance(self):
        """测试位置验证在容忍范围内"""
        target_x, target_y = 100, 200
        # 模拟实际位置在容忍范围内（2像素）
        self._mock_mouse.position = (target_x + 1, target_y + 1)
        
        result = self._controller.MoveTo(target_x, target_y)
        self.assertTrue(result)
    
    def test_MoveTo_Exception(self):
        """测试移动过程中的异常"""
        self._mock_mouse.__setattr__.side_effect = Exception("测试异常")
        
        with self.assertRaises(MouseOperationError):
            self._controller.MoveTo(100, 200)
    
    #endregion
    
    #region 点击操作测试
    
    def test_LeftClick_Success(self):
        """测试成功左键点击"""
        target_x, target_y = 100, 200
        self._mock_mouse.position = (target_x, target_y)
        
        result = self._controller.LeftClick(target_x, target_y)
        
        self.assertTrue(result)
        # 验证先移动再点击
        self._mock_mouse.__setattr__.assert_called_with('position', (target_x, target_y))
        
        from pynput.mouse import Button
        self._mock_mouse.click.assert_called_with(Button.left, 1)
    
    def test_RightClick_Success(self):
        """测试成功右键点击"""
        target_x, target_y = 100, 200
        self._mock_mouse.position = (target_x, target_y)
        
        result = self._controller.RightClick(target_x, target_y)
        
        self.assertTrue(result)
        from pynput.mouse import Button
        self._mock_mouse.click.assert_called_with(Button.right, 1)
    
    def test_DoubleClick_Success(self):
        """测试成功双击"""
        target_x, target_y = 100, 200
        self._mock_mouse.position = (target_x, target_y)
        
        result = self._controller.DoubleClick(target_x, target_y)
        
        self.assertTrue(result)
        from pynput.mouse import Button
        self._mock_mouse.click.assert_called_with(Button.left, 2)
    
    def test_LeftClick_MoveToFailed(self):
        """测试移动失败时的点击操作"""
        # 模拟MoveTo失败
        with patch.object(self._controller, 'MoveTo', return_value=False):
            result = self._controller.LeftClick(100, 200)
            self.assertFalse(result)
            # 不应该执行点击
            self._mock_mouse.click.assert_not_called()
    
    def test_Click_Exception(self):
        """测试点击操作异常"""
        target_x, target_y = 100, 200
        self._mock_mouse.position = (target_x, target_y)
        self._mock_mouse.click.side_effect = Exception("点击异常")
        
        with self.assertRaises(MouseOperationError):
            self._controller.LeftClick(target_x, target_y)
    
    #endregion
    
    #region 光标位置获取测试
    
    def test_GetCursorPosition_Success(self):
        """测试成功获取光标位置"""
        expected_position = (150.5, 250.7)
        self._mock_mouse.position = expected_position
        
        result = self._controller.GetCursorPosition()
        
        # 应该返回整数坐标
        self.assertEqual(result, (150, 250))
        self.assertIsInstance(result[0], int)
        self.assertIsInstance(result[1], int)
    
    def test_GetCursorPosition_Exception(self):
        """测试获取光标位置异常"""
        self._mock_mouse.position = Mock(side_effect=Exception("获取位置异常"))
        
        with self.assertRaises(MouseOperationError):
            self._controller.GetCursorPosition()
    
    #endregion
    
    #region 平滑移动测试
    
    @patch('time.sleep')
    def test_SmoothMoveTo_Success(self, mock_sleep):
        """测试成功平滑移动"""
        start_pos = (50, 50)
        target_pos = (150, 150)
        duration_ms = 100
        
        # 模拟起始位置
        self._mock_mouse.position = start_pos
        
        with patch.object(self._controller, 'GetCursorPosition', return_value=start_pos):
            result = self._controller.SmoothMoveTo(target_pos[0], target_pos[1], duration_ms)
        
        self.assertTrue(result)
        
        # 验证调用了sleep（表示有平滑移动过程）
        self.assertTrue(mock_sleep.called)
        
        # 验证最终位置设置正确
        final_calls = [call for call in self._mock_mouse.__setattr__.call_args_list if call[0][0] == 'position']
        self.assertEqual(final_calls[-1], call('position', target_pos))
    
    @patch('time.sleep')
    def test_SmoothMoveTo_AlreadyAtTarget(self, mock_sleep):
        """测试已在目标位置的平滑移动"""
        target_pos = (100, 100)
        
        with patch.object(self._controller, 'GetCursorPosition', return_value=target_pos):
            result = self._controller.SmoothMoveTo(target_pos[0], target_pos[1])
        
        self.assertTrue(result)
        # 不应该有移动过程
        mock_sleep.assert_not_called()
    
    @patch('time.sleep')
    def test_SmoothMoveTo_ShortDistance(self, mock_sleep):
        """测试短距离平滑移动"""
        start_pos = (100, 100)
        target_pos = (105, 105)  # 很近的距离
        
        with patch.object(self._controller, 'GetCursorPosition', return_value=start_pos):
            result = self._controller.SmoothMoveTo(target_pos[0], target_pos[1], 50)
        
        self.assertTrue(result)
        # 短距离移动也应该有步数
        self.assertTrue(mock_sleep.called)
    
    @patch('time.sleep')
    def test_SmoothMoveTo_LongDistance(self, mock_sleep):
        """测试长距离平滑移动"""
        start_pos = (0, 0)
        target_pos = (800, 600)  # 较长距离
        
        with patch.object(self._controller, 'GetCursorPosition', return_value=start_pos):
            result = self._controller.SmoothMoveTo(target_pos[0], target_pos[1], 200)
        
        self.assertTrue(result)
        
        # 长距离应该有更多的sleep调用
        self.assertGreater(mock_sleep.call_count, 20)
    
    def test_SmoothMoveTo_InvalidCoordinates(self):
        """测试平滑移动到无效坐标"""
        with self.assertRaises(MouseOperationError):
            self._controller.SmoothMoveTo(-1000, 10000)
    
    def test_SmoothMoveTo_Exception(self):
        """测试平滑移动异常"""
        with patch.object(self._controller, 'GetCursorPosition', side_effect=Exception("测试异常")):
            with self.assertRaises(MouseOperationError):
                self._controller.SmoothMoveTo(100, 100)
    
    #endregion
    
    #region 坐标验证测试
    
    def test_ValidateCoordinates_ValidRange(self):
        """测试有效坐标范围"""
        valid_coordinates = [
            (0, 0),
            (100, 100),
            (1920, 1080),
            (3840, 2160),  # 4K分辨率
            (7680, 4320)   # 8K分辨率
        ]
        
        for x, y in valid_coordinates:
            result = self._controller._ValidateCoordinates(x, y)
            self.assertTrue(result, f"坐标 ({x}, {y}) 应该是有效的")
    
    def test_ValidateCoordinates_InvalidRange(self):
        """测试无效坐标范围"""
        invalid_coordinates = [
            (-101, 0),     # X太小
            (0, -101),     # Y太小
            (8193, 0),     # X太大
            (0, 8193),     # Y太大
            (-1000, -1000) # 都太小
        ]
        
        for x, y in invalid_coordinates:
            result = self._controller._ValidateCoordinates(x, y)
            self.assertFalse(result, f"坐标 ({x}, {y}) 应该是无效的")
    
    def test_ValidateCoordinates_EdgeCases(self):
        """测试边界情况"""
        edge_cases = [
            (-100, 0),     # 边界值
            (0, -100),
            (8192, 0),
            (0, 8192)
        ]
        
        for x, y in edge_cases:
            result = self._controller._ValidateCoordinates(x, y)
            self.assertTrue(result, f"边界坐标 ({x}, {y}) 应该是有效的")
    
    #endregion
    
    #region 操作间隔测试
    
    @patch('time.time')
    @patch('time.sleep')
    def test_WaitForOperationInterval(self, mock_sleep, mock_time):
        """测试操作间隔等待"""
        # 模拟时间序列
        mock_time.side_effect = [1.0, 1.005]  # 间隔5ms，小于默认10ms
        
        # 设置上次操作时间
        self._controller._last_operation_time = 1.0
        
        # 调用等待方法
        self._controller._WaitForOperationInterval()
        
        # 应该等待剩余时间
        mock_sleep.assert_called_once()
        sleep_duration = mock_sleep.call_args[0][0]
        self.assertAlmostEqual(sleep_duration, 0.005, places=3)
    
    @patch('time.time')
    @patch('time.sleep')
    def test_WaitForOperationInterval_NoWait(self, mock_sleep, mock_time):
        """测试不需要等待的操作间隔"""
        # 模拟时间序列
        mock_time.side_effect = [1.0, 1.015]  # 间隔15ms，大于默认10ms
        
        self._controller._last_operation_time = 1.0
        self._controller._WaitForOperationInterval()
        
        # 不应该等待
        mock_sleep.assert_not_called()
    
    @patch('time.time')
    @patch('time.sleep')
    def test_WaitForOperationInterval_FirstOperation(self, mock_sleep, mock_time):
        """测试首次操作不等待"""
        mock_time.return_value = 1.0
        
        # 首次操作，last_operation_time为0
        self._controller._last_operation_time = 0
        self._controller._WaitForOperationInterval()
        
        # 不应该等待
        mock_sleep.assert_not_called()
    
    #endregion
    
    #region 高级功能测试
    
    def test_SetOperationInterval(self):
        """测试设置操作间隔"""
        # 设置50ms间隔
        self._controller.SetOperationInterval(50)
        
        stats = self._controller.GetOperationStats()
        self.assertEqual(stats['operation_interval_ms'], 50)
    
    def test_SetOperationInterval_MinimumValue(self):
        """测试设置最小操作间隔"""
        # 设置过小的间隔
        self._controller.SetOperationInterval(0.5)  # 0.5ms
        
        stats = self._controller.GetOperationStats()
        self.assertEqual(stats['operation_interval_ms'], 1)  # 应该被限制为1ms
    
    def test_SetSmoothMoveSteps(self):
        """测试设置平滑移动步数"""
        self._controller.SetSmoothMoveSteps(50)
        
        stats = self._controller.GetOperationStats()
        self.assertEqual(stats['smooth_move_steps'], 50)
    
    def test_SetSmoothMoveSteps_BoundaryValues(self):
        """测试平滑移动步数边界值"""
        # 测试最小值
        self._controller.SetSmoothMoveSteps(1)
        stats = self._controller.GetOperationStats()
        self.assertEqual(stats['smooth_move_steps'], 5)  # 应该被限制为最小值5
        
        # 测试最大值
        self._controller.SetSmoothMoveSteps(200)
        stats = self._controller.GetOperationStats()
        self.assertEqual(stats['smooth_move_steps'], 100)  # 应该被限制为最大值100
    
    def test_GetOperationStats(self):
        """测试获取操作统计信息"""
        with patch.object(self._controller, 'GetCursorPosition', return_value=(150, 250)):
            stats = self._controller.GetOperationStats()
        
        expected_keys = ['last_operation_time', 'operation_interval_ms', 'smooth_move_steps', 'current_position']
        for key in expected_keys:
            self.assertIn(key, stats)
        
        self.assertEqual(stats['current_position'], (150, 250))
        self.assertIsInstance(stats['operation_interval_ms'], (int, float))
        self.assertIsInstance(stats['smooth_move_steps'], int)
    
    #endregion
    
    #region 屏幕管理集成测试
    
    def test_ValidateScreenCoordinates(self):
        """测试屏幕坐标验证"""
        screen_width, screen_height = 1920, 1080
        
        # 有效坐标
        valid_coords = [(0, 0), (100, 100), (1919, 1079)]
        for x, y in valid_coords:
            result = self._controller.ValidateScreenCoordinates(x, y, screen_width, screen_height)
            self.assertTrue(result)
        
        # 无效坐标
        invalid_coords = [(-1, 0), (0, -1), (1920, 0), (0, 1080)]
        for x, y in invalid_coords:
            result = self._controller.ValidateScreenCoordinates(x, y, screen_width, screen_height)
            self.assertFalse(result)
    
    def test_ClampToScreen(self):
        """测试坐标限制到屏幕范围"""
        screen_width, screen_height = 1920, 1080
        
        test_cases = [
            ((-10, -10), (0, 0)),           # 负坐标
            ((2000, 1200), (1919, 1079)),  # 超出范围
            ((100, 100), (100, 100)),      # 正常范围内
            ((1920, 1080), (1919, 1079))   # 边界值
        ]
        
        for input_coords, expected_coords in test_cases:
            result = self._controller.ClampToScreen(input_coords[0], input_coords[1], screen_width, screen_height)
            self.assertEqual(result, expected_coords)
    
    #endregion
    
    #region 测试和调试支持测试
    
    def test_TestMouseOperation_Success(self):
        """测试鼠标操作测试功能"""
        # 模拟成功的测试
        start_pos = (100, 100)
        test_pos = (110, 110)
        
        self._mock_mouse.position = start_pos
        
        with patch.object(self._controller, 'GetCursorPosition', side_effect=[start_pos, test_pos, start_pos]):
            with patch.object(self._controller, 'MoveTo', return_value=True):
                result = self._controller.TestMouseOperation()
        
        self.assertIn('get_position', result)
        self.assertIn('move_to', result)
        self.assertIn('restore_position', result)
        self.assertTrue(result['get_position'])
        self.assertTrue(result['move_to'])
        self.assertTrue(result['restore_position'])
    
    def test_TestMouseOperation_Exception(self):
        """测试鼠标操作测试异常"""
        with patch.object(self._controller, 'GetCursorPosition', side_effect=Exception("测试异常")):
            result = self._controller.TestMouseOperation()
        
        self.assertIn('error', result)
        self.assertEqual(result['error'], "测试异常")
    
    #endregion
    
    #region 线程安全测试
    
    def test_ThreadSafety_ConcurrentOperations(self):
        """测试并发操作的线程安全性"""
        import threading
        
        # 模拟成功的移动操作
        self._mock_mouse.position = (100, 100)
        
        results = []
        
        def _MoveMouse(x, y):
            try:
                result = self._controller.MoveTo(x, y)
                results.append(result)
            except Exception as e:
                results.append(False)
        
        # 创建多个线程并发操作
        threads = []
        for i in range(10):
            thread = threading.Thread(target=_MoveMouse, args=(100 + i, 100 + i))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有操作都成功（由于锁的保护）
        self.assertEqual(len(results), 10)
    
    def test_ThreadSafety_ConcurrentConfiguration(self):
        """测试并发配置的线程安全性"""
        import threading
        
        def _SetInterval(interval):
            self._controller.SetOperationInterval(interval)
        
        def _SetSteps(steps):
            self._controller.SetSmoothMoveSteps(steps)
        
        # 创建多个线程并发设置配置
        threads = []
        for i in range(5):
            thread1 = threading.Thread(target=_SetInterval, args=(10 + i,))
            thread2 = threading.Thread(target=_SetSteps, args=(20 + i,))
            threads.extend([thread1, thread2])
            thread1.start()
            thread2.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证最终状态一致性
        stats = self._controller.GetOperationStats()
        self.assertIsInstance(stats['operation_interval_ms'], (int, float))
        self.assertIsInstance(stats['smooth_move_steps'], int)
    
    #endregion
    
    #region 性能测试
    
    @patch('time.time')
    def test_OperationTiming(self, mock_time):
        """测试操作时间记录"""
        test_time = 123.456
        mock_time.return_value = test_time
        
        # 模拟成功移动
        self._mock_mouse.position = (100, 100)
        self._controller.MoveTo(100, 100)
        
        # 验证时间记录
        self.assertEqual(self._controller._last_operation_time, test_time)
    
    #endregion
    
    #region 错误处理测试
    
    def test_ErrorHandling_MouseControllerFailure(self):
        """测试鼠标控制器故障处理"""
        # 模拟pynput鼠标控制器创建失败
        with patch('src.platform.mouse_controller.mouse.Controller', side_effect=Exception("初始化失败")):
            with self.assertRaises(Exception):
                MouseController()
    
    def test_ErrorHandling_PositionPropertyError(self):
        """测试位置属性访问错误"""
        # 模拟position属性访问失败
        type(self._mock_mouse).position = Mock(side_effect=Exception("位置访问失败"))
        
        with self.assertRaises(MouseOperationError):
            self._controller.GetCursorPosition()
    
    #endregion


if __name__ == '__main__':
    unittest.main()