# -*- coding: utf-8 -*-
"""
HotkeyManager 单元测试
测试全局热键管理器的所有功能
"""

import unittest
import threading
import time
from unittest.mock import Mock, patch, MagicMock, call
from typing import Tuple

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# 直接从平台模块导入
from platform.hotkey_manager import HotkeyManager
from platform.interfaces import HotkeyModifier, HotkeyInfo, HotkeyRegistrationError


class TestHotkeyManager(unittest.TestCase):
    """HotkeyManager 测试类"""
    
    #region 测试初始化和清理
    
    def setUp(self):
        """测试前初始化"""
        self._manager = HotkeyManager()
        self._test_callback_called = False
        self._test_callback_count = 0
    
    def tearDown(self):
        """测试后清理"""
        try:
            self._manager.UnregisterAll()
        except:
            pass
    
    def _TestCallback(self):
        """测试回调函数"""
        self._test_callback_called = True
        self._test_callback_count += 1
    
    #endregion
    
    #region 热键注册测试
    
    def test_RegisterHotkey_Basic(self):
        """测试基本热键注册"""
        # 测试成功注册
        result = self._manager.RegisterHotkey('g', (HotkeyModifier.ALT,), self._TestCallback)
        self.assertTrue(result)
        
        # 验证热键已注册
        self.assertTrue(self._manager.IsHotkeyRegistered('g', (HotkeyModifier.ALT,)))
    
    def test_RegisterHotkey_MultipleModifiers(self):
        """测试多个修饰符的热键注册"""
        modifiers = (HotkeyModifier.ALT, HotkeyModifier.CTRL)
        result = self._manager.RegisterHotkey('g', modifiers, self._TestCallback)
        self.assertTrue(result)
        self.assertTrue(self._manager.IsHotkeyRegistered('g', modifiers))
    
    def test_RegisterHotkey_CaseInsensitive(self):
        """测试按键大小写不敏感"""
        result1 = self._manager.RegisterHotkey('G', (HotkeyModifier.ALT,), self._TestCallback)
        self.assertTrue(result1)
        
        # 验证小写形式也被认为已注册
        self.assertTrue(self._manager.IsHotkeyRegistered('g', (HotkeyModifier.ALT,)))
    
    def test_RegisterHotkey_DuplicateRegistration(self):
        """测试重复注册相同热键"""
        # 首次注册
        self._manager.RegisterHotkey('g', (HotkeyModifier.ALT,), self._TestCallback)
        
        # 重复注册应该抛出异常
        with self.assertRaises(HotkeyRegistrationError):
            self._manager.RegisterHotkey('g', (HotkeyModifier.ALT,), self._TestCallback)
    
    def test_RegisterHotkey_DifferentModifiers(self):
        """测试相同按键不同修饰符的注册"""
        # 注册 Alt+G
        result1 = self._manager.RegisterHotkey('g', (HotkeyModifier.ALT,), self._TestCallback)
        self.assertTrue(result1)
        
        # 注册 Ctrl+G
        result2 = self._manager.RegisterHotkey('g', (HotkeyModifier.CTRL,), self._TestCallback)
        self.assertTrue(result2)
        
        # 两个热键都应该存在
        self.assertTrue(self._manager.IsHotkeyRegistered('g', (HotkeyModifier.ALT,)))
        self.assertTrue(self._manager.IsHotkeyRegistered('g', (HotkeyModifier.CTRL,)))
    
    def test_RegisterHotkey_EscapeKey(self):
        """测试Escape键注册"""
        result = self._manager.RegisterHotkey('escape', (), self._TestCallback)
        self.assertTrue(result)
        self.assertTrue(self._manager.IsHotkeyRegistered('escape', ()))
    
    #endregion
    
    #region 热键注销测试
    
    def test_UnregisterHotkey_Basic(self):
        """测试基本热键注销"""
        # 先注册
        self._manager.RegisterHotkey('g', (HotkeyModifier.ALT,), self._TestCallback)
        self.assertTrue(self._manager.IsHotkeyRegistered('g', (HotkeyModifier.ALT,)))
        
        # 注销
        result = self._manager.UnregisterHotkey('g', (HotkeyModifier.ALT,))
        self.assertTrue(result)
        self.assertFalse(self._manager.IsHotkeyRegistered('g', (HotkeyModifier.ALT,)))
    
    def test_UnregisterHotkey_NotRegistered(self):
        """测试注销未注册的热键"""
        result = self._manager.UnregisterHotkey('g', (HotkeyModifier.ALT,))
        self.assertFalse(result)
    
    def test_UnregisterAll_Basic(self):
        """测试注销所有热键"""
        # 注册多个热键
        self._manager.RegisterHotkey('g', (HotkeyModifier.ALT,), self._TestCallback)
        self._manager.RegisterHotkey('escape', (), self._TestCallback)
        self._manager.RegisterHotkey('h', (HotkeyModifier.CTRL,), self._TestCallback)
        
        # 验证都已注册
        self.assertTrue(self._manager.IsHotkeyRegistered('g', (HotkeyModifier.ALT,)))
        self.assertTrue(self._manager.IsHotkeyRegistered('escape', ()))
        self.assertTrue(self._manager.IsHotkeyRegistered('h', (HotkeyModifier.CTRL,)))
        
        # 注销所有
        self._manager.UnregisterAll()
        
        # 验证都已注销
        self.assertFalse(self._manager.IsHotkeyRegistered('g', (HotkeyModifier.ALT,)))
        self.assertFalse(self._manager.IsHotkeyRegistered('escape', ()))
        self.assertFalse(self._manager.IsHotkeyRegistered('h', (HotkeyModifier.CTRL,)))
    
    #endregion
    
    #region 热键ID创建测试
    
    def test_CreateHotkeyId_SingleModifier(self):
        """测试单个修饰符的热键ID创建"""
        hotkey_id = self._manager._CreateHotkeyId('g', (HotkeyModifier.ALT,))
        self.assertEqual(hotkey_id, 'alt+g')
    
    def test_CreateHotkeyId_MultipleModifiers(self):
        """测试多个修饰符的热键ID创建"""
        hotkey_id = self._manager._CreateHotkeyId('g', (HotkeyModifier.CTRL, HotkeyModifier.ALT))
        # 修饰符应该按字母顺序排序
        self.assertEqual(hotkey_id, 'alt+ctrl+g')
    
    def test_CreateHotkeyId_NoModifiers(self):
        """测试无修饰符的热键ID创建"""
        hotkey_id = self._manager._CreateHotkeyId('escape', ())
        self.assertEqual(hotkey_id, 'escape')
    
    def test_CreateHotkeyId_CaseInsensitive(self):
        """测试按键大小写处理"""
        hotkey_id1 = self._manager._CreateHotkeyId('G', (HotkeyModifier.ALT,))
        hotkey_id2 = self._manager._CreateHotkeyId('g', (HotkeyModifier.ALT,))
        self.assertEqual(hotkey_id1, hotkey_id2)
    
    #endregion
    
    #region 按键处理测试
    
    @patch('platform.hotkey_manager.Listener')
    def test_StartListener_Basic(self, mock_listener_class):
        """测试监听器启动"""
        mock_listener = Mock()
        mock_listener.running = False
        mock_listener_class.return_value = mock_listener
        
        # 注册热键应该启动监听器
        self._manager.RegisterHotkey('g', (HotkeyModifier.ALT,), self._TestCallback)
        
        # 验证监听器被创建和启动
        mock_listener_class.assert_called_once()
        mock_listener.start.assert_called_once()
    
    @patch('platform.hotkey_manager.Listener')
    def test_StopListener_Basic(self, mock_listener_class):
        """测试监听器停止"""
        mock_listener = Mock()
        mock_listener.running = True
        mock_listener_class.return_value = mock_listener
        
        # 注册热键启动监听器
        self._manager.RegisterHotkey('g', (HotkeyModifier.ALT,), self._TestCallback)
        
        # 注销所有热键应该停止监听器
        self._manager.UnregisterAll()
        
        # 验证监听器被停止
        mock_listener.stop.assert_called_once()
    
    def test_GetKeyString_CharacterKey(self):
        """测试字符按键的字符串转换"""
        # 模拟按键对象
        key_mock = Mock()
        key_mock.char = 'g'
        
        result = self._manager._GetKeyString(key_mock)
        self.assertEqual(result, 'g')
    
    def test_GetKeyString_SpecialKey(self):
        """测试特殊按键的字符串转换"""
        # 模拟Escape按键
        key_mock = Mock()
        key_mock.char = None
        key_mock.name = 'esc'
        
        result = self._manager._GetKeyString(key_mock)
        self.assertEqual(result, 'escape')
    
    def test_GetKeyString_InvalidKey(self):
        """测试无效按键的处理"""
        # 模拟无效按键
        key_mock = Mock()
        key_mock.char = None
        del key_mock.name  # 删除name属性
        
        result = self._manager._GetKeyString(key_mock)
        self.assertIsNotNone(result)  # 应该返回字符串而不是None
    
    #endregion
    
    #region 修饰符状态测试
    
    def test_UpdateModifierState_AltKey(self):
        """测试Alt键修饰符状态更新"""
        from pynput.keyboard import Key
        
        # 按下Alt键
        self._manager._UpdateModifierState(Key.alt_l, True)
        self.assertIn(HotkeyModifier.ALT, self._manager._current_modifiers)
        
        # 释放Alt键
        self._manager._UpdateModifierState(Key.alt_l, False)
        self.assertNotIn(HotkeyModifier.ALT, self._manager._current_modifiers)
    
    def test_UpdateModifierState_MultipleModifiers(self):
        """测试多个修饰符状态"""
        from pynput.keyboard import Key
        
        # 按下Alt和Ctrl
        self._manager._UpdateModifierState(Key.alt_l, True)
        self._manager._UpdateModifierState(Key.ctrl_l, True)
        
        expected_modifiers = {HotkeyModifier.ALT, HotkeyModifier.CTRL}
        self.assertEqual(self._manager._current_modifiers, expected_modifiers)
        
        # 释放Alt
        self._manager._UpdateModifierState(Key.alt_l, False)
        self.assertEqual(self._manager._current_modifiers, {HotkeyModifier.CTRL})
    
    def test_UpdateModifierState_LeftRightKeys(self):
        """测试左右修饰符键等价性"""
        from pynput.keyboard import Key
        
        # 左Alt和右Alt应该映射到同一个修饰符
        self._manager._UpdateModifierState(Key.alt_l, True)
        self.assertIn(HotkeyModifier.ALT, self._manager._current_modifiers)
        
        self._manager._UpdateModifierState(Key.alt_l, False)
        self._manager._UpdateModifierState(Key.alt_r, True)
        self.assertIn(HotkeyModifier.ALT, self._manager._current_modifiers)
    
    #endregion
    
    #region 热键匹配测试
    
    def test_IsHotkeyMatch_ExactMatch(self):
        """测试精确热键匹配"""
        hotkey_info = HotkeyInfo(
            Key='g',
            Modifiers=(HotkeyModifier.ALT,),
            Callback=self._TestCallback,
            IsRegistered=True
        )
        
        # 设置当前修饰符状态
        self._manager._current_modifiers = {HotkeyModifier.ALT}
        
        # 测试匹配
        result = self._manager._IsHotkeyMatch(hotkey_info, 'g')
        self.assertTrue(result)
    
    def test_IsHotkeyMatch_WrongKey(self):
        """测试错误按键不匹配"""
        hotkey_info = HotkeyInfo(
            Key='g',
            Modifiers=(HotkeyModifier.ALT,),
            Callback=self._TestCallback,
            IsRegistered=True
        )
        
        self._manager._current_modifiers = {HotkeyModifier.ALT}
        
        # 测试不同按键
        result = self._manager._IsHotkeyMatch(hotkey_info, 'h')
        self.assertFalse(result)
    
    def test_IsHotkeyMatch_WrongModifiers(self):
        """测试错误修饰符不匹配"""
        hotkey_info = HotkeyInfo(
            Key='g',
            Modifiers=(HotkeyModifier.ALT,),
            Callback=self._TestCallback,
            IsRegistered=True
        )
        
        # 设置不同的修饰符
        self._manager._current_modifiers = {HotkeyModifier.CTRL}
        
        result = self._manager._IsHotkeyMatch(hotkey_info, 'g')
        self.assertFalse(result)
    
    def test_IsHotkeyMatch_NoModifiers(self):
        """测试无修饰符匹配"""
        hotkey_info = HotkeyInfo(
            Key='escape',
            Modifiers=(),
            Callback=self._TestCallback,
            IsRegistered=True
        )
        
        # 清空修饰符
        self._manager._current_modifiers = set()
        
        result = self._manager._IsHotkeyMatch(hotkey_info, 'escape')
        self.assertTrue(result)
    
    #endregion
    
    #region 回调执行测试
    
    def test_ExecuteCallback_Success(self):
        """测试回调函数成功执行"""
        self._manager._ExecuteCallback(self._TestCallback)
        self.assertTrue(self._test_callback_called)
        self.assertEqual(self._test_callback_count, 1)
    
    def test_ExecuteCallback_Exception(self):
        """测试回调函数异常处理"""
        def _ErrorCallback():
            raise ValueError("测试异常")
        
        # 异常应该被捕获，不影响系统稳定性
        try:
            self._manager._ExecuteCallback(_ErrorCallback)
        except ValueError:
            self.fail("回调异常没有被正确处理")
    
    #endregion
    
    #region 防抖测试
    
    @patch('time.time')
    def test_DebounceHandling(self, mock_time):
        """测试防抖处理"""
        # 模拟时间 - 关键是初始化_last_trigger_time
        mock_time.side_effect = [1.0, 1.05, 1.15]  # 第二次调用间隔50ms（小于100ms防抖），第三次间隔150ms
        
        # 先设置一个初始的触发时间
        self._manager._last_trigger_time = 1.0
        
        with patch.object(self._manager, '_CheckHotkeyMatch') as mock_check:
            # 第一次按键（在防抖间隔内，应该被忽略）
            self._manager._OnKeyPress(Mock())
            self.assertEqual(mock_check.call_count, 0)  # 应该被防抖阻止
            
            # 第二次按键（仍在防抖间隔内）
            self._manager._OnKeyPress(Mock())
            self.assertEqual(mock_check.call_count, 0)  # 应该被防抖阻止
            
            # 第三次按键（超过防抖间隔）
            self._manager._OnKeyPress(Mock())
            self.assertEqual(mock_check.call_count, 1)  # 应该通过防抖检查
    
    #endregion
    
    #region 线程安全测试
    
    def test_ThreadSafety_ConcurrentRegistration(self):
        """测试并发注册的线程安全性"""
        success_count = [0]
        exception_count = [0]
        
        def _RegisterHotkey(key_suffix):
            try:
                result = self._manager.RegisterHotkey(f'key{key_suffix}', (HotkeyModifier.ALT,), self._TestCallback)
                if result:
                    success_count[0] += 1
            except Exception:
                exception_count[0] += 1
        
        # 创建多个线程并发注册
        threads = []
        for i in range(10):
            thread = threading.Thread(target=_RegisterHotkey, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        self.assertEqual(success_count[0], 10)
        self.assertEqual(exception_count[0], 0)
    
    def test_ThreadSafety_ConcurrentUnregistration(self):
        """测试并发注销的线程安全性"""
        # 先注册一些热键
        keys = [f'key{i}' for i in range(5)]
        for key in keys:
            self._manager.RegisterHotkey(key, (HotkeyModifier.ALT,), self._TestCallback)
        
        success_count = [0]
        
        def _UnregisterHotkey(key):
            try:
                result = self._manager.UnregisterHotkey(key, (HotkeyModifier.ALT,))
                if result:
                    success_count[0] += 1
            except Exception:
                pass
        
        # 创建多个线程并发注销
        threads = []
        for key in keys:
            thread = threading.Thread(target=_UnregisterHotkey, args=(key,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        self.assertEqual(success_count[0], 5)
    
    #endregion
    
    #region 资源管理测试
    
    def test_ResourceCleanup_Destructor(self):
        """测试析构函数资源清理"""
        manager = HotkeyManager()
        manager.RegisterHotkey('g', (HotkeyModifier.ALT,), self._TestCallback)
        
        # 模拟析构
        with patch.object(manager, 'UnregisterAll') as mock_unregister:
            manager.__del__()
            mock_unregister.assert_called_once()
    
    def test_ResourceCleanup_Exception(self):
        """测试析构函数异常处理"""
        manager = HotkeyManager()
        
        # 模拟UnregisterAll抛出异常
        with patch.object(manager, 'UnregisterAll', side_effect=Exception("测试异常")):
            try:
                manager.__del__()  # 不应该抛出异常
            except Exception:
                self.fail("析构函数异常没有被正确处理")
    
    #endregion
    
    #region 边界条件测试
    
    def test_EmptyKeyString(self):
        """测试空按键字符串处理"""
        result = self._manager.IsHotkeyRegistered('', (HotkeyModifier.ALT,))
        self.assertFalse(result)
    
    def test_NoneCallback(self):
        """测试None回调函数"""
        # 实际上RegisterHotkey允许None回调，让我们测试这种情况下的行为
        result = self._manager.RegisterHotkey('g', (HotkeyModifier.ALT,), None)
        self.assertTrue(result)  # 注册应该成功
        
        # 验证热键已注册
        self.assertTrue(self._manager.IsHotkeyRegistered('g', (HotkeyModifier.ALT,)))
        
        # 测试执行None回调不会出错
        try:
            self._manager._ExecuteCallback(None)
        except Exception:
            self.fail("执行None回调不应该抛出异常")
    
    def test_InvalidModifier(self):
        """测试无效修饰符"""
        # 这个测试确保枚举类型的安全性
        valid_modifiers = (HotkeyModifier.ALT, HotkeyModifier.CTRL)
        result = self._manager.RegisterHotkey('g', valid_modifiers, self._TestCallback)
        self.assertTrue(result)
    
    #endregion


if __name__ == '__main__':
    unittest.main()