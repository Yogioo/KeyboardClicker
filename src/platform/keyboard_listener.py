# -*- coding: utf-8 -*-
"""
全局键盘监听器实现
专门用于监听九宫格按键输入和命令后缀
"""

import threading
import time
from typing import Callable, Tuple, Set, Optional
from pynput import keyboard
from pynput.keyboard import Key, Listener

from .interfaces import IKeyboardListener, IPlatformException


class KeyboardInputError(IPlatformException):
    """键盘输入异常"""
    pass


class KeyboardListener(IKeyboardListener):
    """全局键盘监听器实现"""
    
    def __init__(self):
        #region 私有属性初始化
        self._listener: Optional[Listener] = None
        self._is_listening = False
        self._key_handler: Optional[Callable[[str], None]] = None
        self._allowed_keys: Set[str] = set()
        self._lock = threading.RLock()
        self._last_input_time = 0
        self._debounce_interval = 0.05  # 防抖间隔50ms
        
        # 默认九宫格按键
        self._SetDefaultAllowedKeys()
        #endregion
    
    #region 公共方法实现
    
    def StartListening(self) -> bool:
        """开始全局键盘监听"""
        try:
            with self._lock:
                if self._is_listening:
                    return True
                
                self._listener = Listener(
                    on_press=self._OnKeyPress,
                    suppress=False  # 不抑制按键，让其他应用正常响应
                )
                
                self._listener.start()
                self._is_listening = True
                return True
                
        except Exception as e:
            raise KeyboardInputError(f"启动键盘监听失败: {str(e)}")
    
    def StopListening(self) -> None:
        """停止键盘监听"""
        with self._lock:
            if self._listener and self._listener.running:
                self._listener.stop()
                self._listener = None
            self._is_listening = False
    
    def SetKeyFilter(self, allowed_keys: Tuple[str, ...]) -> None:
        """设置允许的按键过滤器"""
        with self._lock:
            self._allowed_keys = {key.lower() for key in allowed_keys}
    
    def RegisterKeyHandler(self, handler: Callable[[str], None]) -> None:
        """注册按键处理器"""
        with self._lock:
            self._key_handler = handler
    
    def IsListening(self) -> bool:
        """检查是否正在监听"""
        return self._is_listening
    
    #endregion
    
    #region 私有方法实现
    
    def _SetDefaultAllowedKeys(self) -> None:
        """设置默认允许的按键"""
        # 九宫格按键映射
        grid_keys = ['q', 'w', 'e', 'a', 's', 'd', 'z', 'x', 'c']
        # 命令后缀按键
        command_keys = ['r', 'h']
        # 控制按键
        control_keys = ['escape', 'enter', 'backspace']
        
        self._allowed_keys = set(grid_keys + command_keys + control_keys)
    
    def _OnKeyPress(self, key) -> None:
        """按键按下事件处理"""
        try:
            with self._lock:
                # 防抖处理
                current_time = time.time()
                if current_time - self._last_input_time < self._debounce_interval:
                    return
                
                # 获取按键字符串
                key_str = self._GetKeyString(key)
                if not key_str:
                    return
                
                # 检查是否为允许的按键
                if not self._IsAllowedKey(key_str):
                    return
                
                # 更新最后输入时间
                self._last_input_time = current_time
                
                # 调用按键处理器
                if self._key_handler:
                    try:
                        # 异步执行处理器，避免阻塞监听器
                        threading.Thread(
                            target=self._SafeExecuteHandler,
                            args=(key_str,),
                            daemon=True
                        ).start()
                    except Exception:
                        # 忽略处理器执行异常
                        pass
                        
        except Exception:
            # 忽略监听器内部异常，避免影响系统稳定性
            pass
    
    def _GetKeyString(self, key) -> Optional[str]:
        """获取按键的字符串表示"""
        try:
            if hasattr(key, 'char') and key.char:
                return key.char.lower()
            elif hasattr(key, 'name'):
                # 处理特殊按键
                special_keys = {
                    'esc': 'escape',
                    'enter': 'return',
                    'space': ' ',
                    'backspace': 'backspace'
                }
                key_name = key.name.lower()
                return special_keys.get(key_name, key_name)
            else:
                # 处理其他类型的按键
                key_str = str(key).replace('Key.', '').lower()
                return key_str if key_str else None
        except:
            return None
    
    def _IsAllowedKey(self, key_str: str) -> bool:
        """检查是否为允许的按键"""
        return key_str in self._allowed_keys
    
    def _SafeExecuteHandler(self, key_str: str) -> None:
        """安全执行按键处理器"""
        try:
            if self._key_handler:
                self._key_handler(key_str)
        except Exception:
            # 忽略处理器异常，避免影响系统稳定性
            pass
    
    #endregion
    
    #region 高级功能
    
    def AddAllowedKey(self, key: str) -> None:
        """添加允许的按键"""
        with self._lock:
            self._allowed_keys.add(key.lower())
    
    def RemoveAllowedKey(self, key: str) -> None:
        """移除允许的按键"""
        with self._lock:
            self._allowed_keys.discard(key.lower())
    
    def GetAllowedKeys(self) -> Tuple[str, ...]:
        """获取当前允许的按键列表"""
        with self._lock:
            return tuple(sorted(self._allowed_keys))
    
    def ResetToDefaultKeys(self) -> None:
        """重置为默认按键"""
        with self._lock:
            self._SetDefaultAllowedKeys()
    
    def SetDebounceInterval(self, interval_ms: float) -> None:
        """设置防抖间隔"""
        with self._lock:
            self._debounce_interval = max(0.01, interval_ms / 1000.0)  # 最小10ms
    
    #endregion
    
    #region 状态管理
    
    def GetStatus(self) -> dict:
        """获取监听器状态信息"""
        with self._lock:
            return {
                'is_listening': self._is_listening,
                'allowed_keys_count': len(self._allowed_keys),
                'has_handler': self._key_handler is not None,
                'debounce_interval_ms': self._debounce_interval * 1000,
                'last_input_time': self._last_input_time
            }
    
    #endregion
    
    #region 资源清理
    
    def __del__(self):
        """析构函数，确保资源清理"""
        try:
            self.StopListening()
        except:
            pass
    
    #endregion