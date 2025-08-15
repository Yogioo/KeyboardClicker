# -*- coding: utf-8 -*-
"""
KeyboardListener 单元测试
测试全局键盘监听器的所有功能
"""

import unittest
import threading
import time
from unittest.mock import Mock, patch, MagicMock, call
from typing import Set, List

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.platform.keyboard_listener import KeyboardListener, KeyboardInputError
from src.platform.interfaces import IPlatformException


class TestKeyboardListener(unittest.TestCase):
    """KeyboardListener 测试类"""
    
    #region 测试初始化和清理
    
    def setUp(self):
        """测试前初始化"""
        self._listener = KeyboardListener()
        self._received_keys: List[str] = []
        self._handler_call_count = 0
    
    def tearDown(self):
        """测试后清理"""
        try:
            self._listener.StopListening()
        except:
            pass
    
    def _TestKeyHandler(self, key: str):
        """测试按键处理器"""
        self._received_keys.append(key)
        self._handler_call_count += 1
    
    def _ErrorKeyHandler(self, key: str):
        """会抛出异常的按键处理器"""
        raise ValueError(f"测试异常: {key}")
    
    #endregion
    
    #region 监听控制测试
    
    @patch('src.platform.keyboard_listener.Listener')
    def test_StartListening_Success(self, mock_listener_class):
        """测试成功启动监听"""
        mock_listener = Mock()
        mock_listener.running = False
        mock_listener_class.return_value = mock_listener
        
        result = self._listener.StartListening()
        
        self.assertTrue(result)
        self.assertTrue(self._listener.IsListening())
        mock_listener_class.assert_called_once()
        mock_listener.start.assert_called_once()
    
    @patch('src.platform.keyboard_listener.Listener')
    def test_StartListening_AlreadyListening(self, mock_listener_class):
        """测试重复启动监听"""
        mock_listener = Mock()
        mock_listener.running = False
        mock_listener_class.return_value = mock_listener
        
        # 第一次启动
        result1 = self._listener.StartListening()
        self.assertTrue(result1)
        
        # 第二次启动（应该直接返回True）
        result2 = self._listener.StartListening()
        self.assertTrue(result2)
        
        # 验证只创建了一次监听器
        self.assertEqual(mock_listener_class.call_count, 1)
    
    @patch('src.platform.keyboard_listener.Listener')
    def test_StartListening_Exception(self, mock_listener_class):
        """测试启动监听异常"""
        mock_listener_class.side_effect = Exception("测试异常")
        
        with self.assertRaises(KeyboardInputError):
            self._listener.StartListening()
    
    @patch('src.platform.keyboard_listener.Listener')
    def test_StopListening_Success(self, mock_listener_class):
        """测试成功停止监听"""
        mock_listener = Mock()
        mock_listener.running = True
        mock_listener_class.return_value = mock_listener
        
        # 启动监听
        self._listener.StartListening()
        self.assertTrue(self._listener.IsListening())
        
        # 停止监听
        self._listener.StopListening()
        self.assertFalse(self._listener.IsListening())
        mock_listener.stop.assert_called_once()
    
    def test_StopListening_NotListening(self):
        """测试停止未启动的监听"""
        # 直接停止监听（没有启动过）
        try:
            self._listener.StopListening()
            self.assertFalse(self._listener.IsListening())
        except Exception:
            self.fail("停止未启动的监听不应该抛出异常")
    
    def test_IsListening_InitialState(self):
        """测试初始监听状态"""
        self.assertFalse(self._listener.IsListening())
    
    #endregion
    
    #region 按键过滤测试
    
    def test_SetKeyFilter_BasicKeys(self):
        """测试设置基本按键过滤器"""
        test_keys = ('q', 'w', 'e', 'r')
        self._listener.SetKeyFilter(test_keys)
        
        allowed_keys = self._listener.GetAllowedKeys()
        for key in test_keys:
            self.assertIn(key.lower(), allowed_keys)
    
    def test_SetKeyFilter_CaseInsensitive(self):
        """测试按键过滤器大小写不敏感"""
        test_keys = ('Q', 'W', 'E', 'R')
        self._listener.SetKeyFilter(test_keys)
        
        allowed_keys = self._listener.GetAllowedKeys()
        for key in test_keys:
            self.assertIn(key.lower(), allowed_keys)
    
    def test_DefaultAllowedKeys(self):
        """测试默认允许的按键"""
        allowed_keys = self._listener.GetAllowedKeys()
        
        # 九宫格按键
        grid_keys = ['q', 'w', 'e', 'a', 's', 'd', 'z', 'x', 'c']
        for key in grid_keys:
            self.assertIn(key, allowed_keys)
        
        # 命令后缀按键
        command_keys = ['r', 'h']
        for key in command_keys:
            self.assertIn(key, allowed_keys)
        
        # 控制按键
        control_keys = ['escape', 'enter', 'backspace']
        for key in control_keys:
            self.assertIn(key, allowed_keys)
    
    def test_AddAllowedKey(self):
        """测试添加允许的按键"""
        original_keys = set(self._listener.GetAllowedKeys())
        
        self._listener.AddAllowedKey('F1')
        new_keys = set(self._listener.GetAllowedKeys())
        
        self.assertIn('f1', new_keys)
        self.assertEqual(len(new_keys), len(original_keys) + 1)
    
    def test_RemoveAllowedKey(self):
        """测试移除允许的按键"""
        original_keys = set(self._listener.GetAllowedKeys())
        
        # 移除一个存在的按键
        self._listener.RemoveAllowedKey('q')
        new_keys = set(self._listener.GetAllowedKeys())
        
        self.assertNotIn('q', new_keys)
        self.assertEqual(len(new_keys), len(original_keys) - 1)
    
    def test_RemoveAllowedKey_NotExists(self):
        """测试移除不存在的按键"""
        original_keys = set(self._listener.GetAllowedKeys())
        
        # 移除不存在的按键
        self._listener.RemoveAllowedKey('nonexistent')
        new_keys = set(self._listener.GetAllowedKeys())
        
        self.assertEqual(new_keys, original_keys)
    
    def test_ResetToDefaultKeys(self):
        """测试重置为默认按键"""
        # 修改允许的按键
        self._listener.SetKeyFilter(('x', 'y', 'z'))
        modified_keys = set(self._listener.GetAllowedKeys())
        
        # 重置为默认
        self._listener.ResetToDefaultKeys()
        default_keys = set(self._listener.GetAllowedKeys())
        
        self.assertNotEqual(modified_keys, default_keys)
        self.assertIn('q', default_keys)  # 默认九宫格按键应该存在
    
    #endregion
    
    #region 按键处理器测试
    
    def test_RegisterKeyHandler_Basic(self):
        """测试注册按键处理器"""
        self._listener.RegisterKeyHandler(self._TestKeyHandler)
        
        # 模拟按键处理
        self._listener._SafeExecuteHandler('q')
        
        self.assertEqual(len(self._received_keys), 1)
        self.assertEqual(self._received_keys[0], 'q')
        self.assertEqual(self._handler_call_count, 1)
    
    def test_RegisterKeyHandler_Replace(self):
        """测试替换按键处理器"""
        # 注册第一个处理器
        self._listener.RegisterKeyHandler(self._TestKeyHandler)
        self._listener._SafeExecuteHandler('q')
        self.assertEqual(self._handler_call_count, 1)
        
        # 注册第二个处理器
        handler2_call_count = [0]
        def _Handler2(key):
            handler2_call_count[0] += 1
        
        self._listener.RegisterKeyHandler(_Handler2)
        self._listener._SafeExecuteHandler('w')
        
        # 验证只有第二个处理器被调用
        self.assertEqual(self._handler_call_count, 1)  # 没有增加
        self.assertEqual(handler2_call_count[0], 1)
    
    def test_RegisterKeyHandler_None(self):
        """测试注册None处理器"""
        self._listener.RegisterKeyHandler(None)
        
        # 执行处理器不应该出错
        try:
            self._listener._SafeExecuteHandler('q')
        except Exception:
            self.fail("处理None处理器不应该抛出异常")
    
    def test_SafeExecuteHandler_Exception(self):
        """测试处理器异常安全执行"""
        self._listener.RegisterKeyHandler(self._ErrorKeyHandler)
        
        # 异常应该被捕获
        try:
            self._listener._SafeExecuteHandler('q')
        except ValueError:
            self.fail("处理器异常没有被正确捕获")
    
    #endregion
    
    #region 按键字符串转换测试
    
    def test_GetKeyString_CharacterKey(self):
        """测试字符按键转换"""
        key_mock = Mock()
        key_mock.char = 'q'
        
        result = self._listener._GetKeyString(key_mock)
        self.assertEqual(result, 'q')
    
    def test_GetKeyString_UppercaseCharacter(self):
        """测试大写字符按键转换"""
        key_mock = Mock()
        key_mock.char = 'Q'
        
        result = self._listener._GetKeyString(key_mock)
        self.assertEqual(result, 'q')  # 应该转换为小写
    
    def test_GetKeyString_SpecialKeys(self):
        """测试特殊按键转换"""
        test_cases = [
            ('esc', 'escape'),
            ('enter', 'return'),
            ('space', ' '),
            ('backspace', 'backspace')
        ]
        
        for input_name, expected_output in test_cases:
            key_mock = Mock()
            key_mock.char = None
            key_mock.name = input_name
            
            result = self._listener._GetKeyString(key_mock)
            self.assertEqual(result, expected_output)
    
    def test_GetKeyString_OtherSpecialKey(self):
        """测试其他特殊按键转换"""
        key_mock = Mock()
        key_mock.char = None
        key_mock.name = 'f1'
        
        result = self._listener._GetKeyString(key_mock)
        self.assertEqual(result, 'f1')
    
    def test_GetKeyString_NoCharNoName(self):
        """测试没有char和name属性的按键"""
        key_mock = Mock()
        key_mock.char = None
        del key_mock.name
        
        # 模拟str(key)的返回值
        key_mock.__str__ = Mock(return_value='Key.tab')
        
        result = self._listener._GetKeyString(key_mock)
        self.assertEqual(result, 'tab')
    
    def test_GetKeyString_Exception(self):
        """测试按键转换异常处理"""
        key_mock = Mock()
        key_mock.char = None
        # 模拟访问name属性时抛出异常
        type(key_mock).name = Mock(side_effect=Exception("测试异常"))
        
        result = self._listener._GetKeyString(key_mock)
        self.assertIsNone(result)
    
    #endregion
    
    #region 按键过滤测试
    
    def test_IsAllowedKey_AllowedKeys(self):
        """测试允许的按键"""
        allowed_keys = ['q', 'w', 'e', 'escape']
        self._listener.SetKeyFilter(tuple(allowed_keys))
        
        for key in allowed_keys:
            self.assertTrue(self._listener._IsAllowedKey(key))
    
    def test_IsAllowedKey_DisallowedKeys(self):
        """测试不允许的按键"""
        self._listener.SetKeyFilter(('q', 'w', 'e'))
        
        disallowed_keys = ['f1', 'tab', 'space']
        for key in disallowed_keys:
            self.assertFalse(self._listener._IsAllowedKey(key))
    
    def test_IsAllowedKey_CaseInsensitive(self):
        """测试按键过滤大小写不敏感"""
        self._listener.SetKeyFilter(('Q', 'W', 'E'))
        
        # 小写形式应该也被允许
        for key in ['q', 'w', 'e']:
            self.assertTrue(self._listener._IsAllowedKey(key))
    
    #endregion
    
    #region 按键事件处理测试
    
    @patch('time.time')
    def test_OnKeyPress_AllowedKey(self, mock_time):
        """测试允许按键的处理"""
        mock_time.return_value = 1.0
        
        self._listener.RegisterKeyHandler(self._TestKeyHandler)
        
        # 模拟按键事件
        key_mock = Mock()
        key_mock.char = 'q'
        
        with patch.object(self._listener, '_SafeExecuteHandler') as mock_execute:
            self._listener._OnKeyPress(key_mock)
            # 由于使用了线程，需要稍等一下
            time.sleep(0.1)
            mock_execute.assert_called()
    
    @patch('time.time')
    def test_OnKeyPress_DisallowedKey(self, mock_time):
        """测试不允许按键的处理"""
        mock_time.return_value = 1.0
        
        self._listener.RegisterKeyHandler(self._TestKeyHandler)
        self._listener.SetKeyFilter(('q', 'w', 'e'))  # 只允许这些按键
        
        # 模拟不允许的按键
        key_mock = Mock()
        key_mock.char = 'f'  # 不在允许列表中
        
        with patch.object(self._listener, '_SafeExecuteHandler') as mock_execute:
            self._listener._OnKeyPress(key_mock)
            time.sleep(0.1)
            mock_execute.assert_not_called()
    
    @patch('time.time')
    def test_OnKeyPress_Debounce(self, mock_time):
        """测试按键防抖处理"""
        # 模拟快速连续按键
        mock_time.side_effect = [1.0, 1.03, 1.08]  # 第二次30ms，第三次80ms
        
        self._listener.RegisterKeyHandler(self._TestKeyHandler)
        
        key_mock = Mock()
        key_mock.char = 'q'
        
        with patch.object(self._listener, '_SafeExecuteHandler') as mock_execute:
            # 第一次按键
            self._listener._OnKeyPress(key_mock)
            
            # 第二次按键（在防抖间隔内）
            self._listener._OnKeyPress(key_mock)
            
            # 第三次按键（超过防抖间隔）
            self._listener._OnKeyPress(key_mock)
            
            time.sleep(0.1)
            
            # 应该只执行了2次（第一次和第三次）
            self.assertEqual(mock_execute.call_count, 2)
    
    def test_OnKeyPress_NoHandler(self):
        """测试没有注册处理器时的按键处理"""
        key_mock = Mock()
        key_mock.char = 'q'
        
        # 没有注册处理器，不应该抛出异常
        try:
            self._listener._OnKeyPress(key_mock)
        except Exception:
            self.fail("没有处理器时按键处理不应该抛出异常")
    
    def test_OnKeyPress_InvalidKey(self):
        """测试无效按键处理"""
        key_mock = Mock()
        key_mock.char = None
        # 模拟_GetKeyString返回None
        with patch.object(self._listener, '_GetKeyString', return_value=None):
            try:
                self._listener._OnKeyPress(key_mock)
            except Exception:
                self.fail("无效按键处理不应该抛出异常")
    
    def test_OnKeyPress_Exception(self):
        """测试按键处理异常安全性"""
        # 模拟在处理过程中抛出异常
        with patch.object(self._listener, '_GetKeyString', side_effect=Exception("测试异常")):
            key_mock = Mock()
            try:
                self._listener._OnKeyPress(key_mock)
            except Exception:
                self.fail("按键处理异常没有被正确捕获")
    
    #endregion
    
    #region 防抖配置测试
    
    def test_SetDebounceInterval_Valid(self):
        """测试设置有效的防抖间隔"""
        self._listener.SetDebounceInterval(100)  # 100ms
        
        status = self._listener.GetStatus()
        self.assertEqual(status['debounce_interval_ms'], 100)
    
    def test_SetDebounceInterval_TooSmall(self):
        """测试设置过小的防抖间隔"""
        self._listener.SetDebounceInterval(5)  # 5ms，小于最小值10ms
        
        status = self._listener.GetStatus()
        self.assertEqual(status['debounce_interval_ms'], 10)  # 应该被限制为最小值
    
    def test_SetDebounceInterval_Zero(self):
        """测试设置零防抖间隔"""
        self._listener.SetDebounceInterval(0)
        
        status = self._listener.GetStatus()
        self.assertEqual(status['debounce_interval_ms'], 10)  # 应该被限制为最小值
    
    #endregion
    
    #region 状态获取测试
    
    def test_GetStatus_InitialState(self):
        """测试初始状态"""
        status = self._listener.GetStatus()
        
        self.assertFalse(status['is_listening'])
        self.assertFalse(status['has_handler'])
        self.assertGreater(status['allowed_keys_count'], 0)
        self.assertEqual(status['debounce_interval_ms'], 50)  # 默认50ms
        self.assertEqual(status['last_input_time'], 0)
    
    @patch('src.platform.keyboard_listener.Listener')
    def test_GetStatus_Listening(self, mock_listener_class):
        """测试监听状态"""
        mock_listener = Mock()
        mock_listener.running = False
        mock_listener_class.return_value = mock_listener
        
        self._listener.StartListening()
        self._listener.RegisterKeyHandler(self._TestKeyHandler)
        
        status = self._listener.GetStatus()
        
        self.assertTrue(status['is_listening'])
        self.assertTrue(status['has_handler'])
    
    def test_GetStatus_AfterKeyInput(self):
        """测试按键输入后的状态"""
        with patch('time.time', return_value=123.456):
            key_mock = Mock()
            key_mock.char = 'q'
            self._listener._OnKeyPress(key_mock)
            
            status = self._listener.GetStatus()
            self.assertEqual(status['last_input_time'], 123.456)
    
    #endregion
    
    #region 线程安全测试
    
    def test_ThreadSafety_ConcurrentKeyFilter(self):
        """测试并发按键过滤设置的线程安全性"""
        def _SetFilter(keys):
            self._listener.SetKeyFilter(keys)
        
        # 创建多个线程并发设置过滤器
        threads = []
        for i in range(10):
            keys = tuple([f'key{j}' for j in range(i, i+3)])
            thread = threading.Thread(target=_SetFilter, args=(keys,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证最终状态一致性
        allowed_keys = self._listener.GetAllowedKeys()
        self.assertIsInstance(allowed_keys, tuple)
        self.assertGreater(len(allowed_keys), 0)
    
    def test_ThreadSafety_ConcurrentHandlerRegistration(self):
        """测试并发处理器注册的线程安全性"""
        call_counts = [0] * 10
        
        def _CreateHandler(index):
            def _Handler(key):
                call_counts[index] += 1
            return _Handler
        
        def _RegisterHandler(index):
            handler = _CreateHandler(index)
            self._listener.RegisterKeyHandler(handler)
        
        # 创建多个线程并发注册处理器
        threads = []
        for i in range(10):
            thread = threading.Thread(target=_RegisterHandler, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证最终状态一致性
        status = self._listener.GetStatus()
        self.assertTrue(status['has_handler'])
    
    #endregion
    
    #region 资源清理测试
    
    def test_ResourceCleanup_Destructor(self):
        """测试析构函数资源清理"""
        listener = KeyboardListener()
        
        with patch.object(listener, 'StopListening') as mock_stop:
            listener.__del__()
            mock_stop.assert_called_once()
    
    def test_ResourceCleanup_Exception(self):
        """测试析构函数异常处理"""
        listener = KeyboardListener()
        
        # 模拟StopListening抛出异常
        with patch.object(listener, 'StopListening', side_effect=Exception("测试异常")):
            try:
                listener.__del__()  # 不应该抛出异常
            except Exception:
                self.fail("析构函数异常没有被正确处理")
    
    #endregion
    
    #region 边界条件测试
    
    def test_EmptyKeyFilter(self):
        """测试空按键过滤器"""
        self._listener.SetKeyFilter(())
        
        allowed_keys = self._listener.GetAllowedKeys()
        self.assertEqual(len(allowed_keys), 0)
        
        # 所有按键都应该被过滤
        self.assertFalse(self._listener._IsAllowedKey('q'))
        self.assertFalse(self._listener._IsAllowedKey('escape'))
    
    def test_LargeKeyFilter(self):
        """测试大量按键过滤器"""
        large_filter = tuple([f'key{i}' for i in range(1000)])
        self._listener.SetKeyFilter(large_filter)
        
        allowed_keys = self._listener.GetAllowedKeys()
        self.assertEqual(len(allowed_keys), 1000)
    
    def test_DuplicateKeysInFilter(self):
        """测试过滤器中的重复按键"""
        duplicate_filter = ('q', 'w', 'q', 'e', 'w')
        self._listener.SetKeyFilter(duplicate_filter)
        
        allowed_keys = self._listener.GetAllowedKeys()
        # Set会自动去重
        self.assertEqual(len(allowed_keys), 3)  # q, w, e
        self.assertIn('q', allowed_keys)
        self.assertIn('w', allowed_keys)
        self.assertIn('e', allowed_keys)
    
    def test_SpecialCharactersInFilter(self):
        """测试过滤器中的特殊字符"""
        special_filter = (' ', '\t', '\n', '!', '@', '#')
        self._listener.SetKeyFilter(special_filter)
        
        allowed_keys = self._listener.GetAllowedKeys()
        for char in special_filter:
            self.assertIn(char, allowed_keys)
    
    #endregion


if __name__ == '__main__':
    unittest.main()