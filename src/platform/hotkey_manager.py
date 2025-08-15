# -*- coding: utf-8 -*-
"""
全局热键管理器实现
使用pynput库实现Windows全局热键注册和管理
"""

import threading
import time
from typing import Callable, Dict, Tuple, Optional
from pynput import keyboard
from pynput.keyboard import Key, Listener

from .interfaces import (
    IHotkeyManager, 
    HotkeyModifier, 
    HotkeyInfo, 
    HotkeyRegistrationError
)


class HotkeyManager(IHotkeyManager):
    """全局热键管理器实现"""
    
    def __init__(self):
        #region 私有属性初始化
        self._hotkeys: Dict[str, HotkeyInfo] = {}
        self._listener: Optional[Listener] = None
        self._is_running = False
        self._current_modifiers = set()
        self._lock = threading.RLock()
        self._last_trigger_time = 0
        self._debounce_interval = 0.1  # 防抖间隔100ms
        #endregion
    
    #region 公共方法实现
    
    def RegisterHotkey(self, key: str, modifiers: Tuple[HotkeyModifier, ...], callback: Callable[[], None]) -> bool:
        """
        注册全局热键
        
        Args:
            key: 按键名称 (如 'g', 'escape')  
            modifiers: 修饰符组合
            callback: 热键触发回调函数
            
        Returns:
            bool: 注册是否成功
        """
        try:
            with self._lock:
                hotkey_id = self._CreateHotkeyId(key, modifiers)
                
                # 检查是否已注册
                if hotkey_id in self._hotkeys:
                    raise HotkeyRegistrationError(f"热键 {hotkey_id} 已经注册")
                
                # 创建热键信息
                hotkey_info = HotkeyInfo(
                    Key=key.lower(),
                    Modifiers=modifiers,
                    Callback=callback,
                    IsRegistered=False
                )
                
                # 保存热键信息
                self._hotkeys[hotkey_id] = hotkey_info
                
                # 启动监听器
                self._StartListener()
                
                hotkey_info.IsRegistered = True
                return True
                
        except Exception as e:
            raise HotkeyRegistrationError(f"注册热键失败: {str(e)}")
    
    def UnregisterHotkey(self, key: str, modifiers: Tuple[HotkeyModifier, ...]) -> bool:
        """注销指定热键"""
        try:
            with self._lock:
                hotkey_id = self._CreateHotkeyId(key, modifiers)
                
                if hotkey_id in self._hotkeys:
                    del self._hotkeys[hotkey_id]
                    
                    # 如果没有热键了，停止监听器
                    if not self._hotkeys:
                        self._StopListener()
                    
                    return True
                    
                return False
                
        except Exception as e:
            raise HotkeyRegistrationError(f"注销热键失败: {str(e)}")
    
    def UnregisterAll(self) -> None:
        """注销所有热键"""
        with self._lock:
            self._hotkeys.clear()
            self._StopListener()
    
    def IsHotkeyRegistered(self, key: str, modifiers: Tuple[HotkeyModifier, ...]) -> bool:
        """检查热键是否已注册"""
        hotkey_id = self._CreateHotkeyId(key, modifiers)
        return hotkey_id in self._hotkeys
    
    #endregion
    
    #region 私有方法实现
    
    def _CreateHotkeyId(self, key: str, modifiers: Tuple[HotkeyModifier, ...]) -> str:
        """创建热键唯一标识"""
        modifier_str = "+".join(sorted([mod.value for mod in modifiers]))
        return f"{modifier_str}+{key.lower()}" if modifier_str else key.lower()
    
    def _StartListener(self) -> None:
        """启动键盘监听器"""
        if self._listener is None or not self._listener.running:
            self._listener = Listener(
                on_press=self._OnKeyPress,
                on_release=self._OnKeyRelease
            )
            self._listener.start()
            self._is_running = True
    
    def _StopListener(self) -> None:
        """停止键盘监听器"""
        if self._listener and self._listener.running:
            self._listener.stop()
            self._listener = None
            self._is_running = False
            self._current_modifiers.clear()
    
    def _OnKeyPress(self, key) -> None:
        """按键按下事件处理"""
        try:
            with self._lock:
                # 防抖处理
                current_time = time.time()
                if current_time - self._last_trigger_time < self._debounce_interval:
                    return
                
                # 更新修饰符状态
                self._UpdateModifierState(key, True)
                
                # 检查热键匹配
                self._CheckHotkeyMatch(key)
                
        except Exception:
            # 忽略监听器内部异常，避免影响系统稳定性
            pass
    
    def _OnKeyRelease(self, key) -> None:
        """按键释放事件处理"""
        try:
            with self._lock:
                # 更新修饰符状态
                self._UpdateModifierState(key, False)
                
        except Exception:
            # 忽略监听器内部异常
            pass
    
    def _UpdateModifierState(self, key, is_pressed: bool) -> None:
        """更新修饰符状态"""
        modifier_map = {
            Key.alt_l: HotkeyModifier.ALT,
            Key.alt_r: HotkeyModifier.ALT,
            Key.ctrl_l: HotkeyModifier.CTRL,
            Key.ctrl_r: HotkeyModifier.CTRL,
            Key.shift_l: HotkeyModifier.SHIFT,
            Key.shift_r: HotkeyModifier.SHIFT,
            Key.cmd: HotkeyModifier.WIN,
        }
        
        if key in modifier_map:
            modifier = modifier_map[key]
            if is_pressed:
                self._current_modifiers.add(modifier)
            else:
                self._current_modifiers.discard(modifier)
    
    def _CheckHotkeyMatch(self, key) -> None:
        """检查是否匹配注册的热键"""
        try:
            # 获取按键字符串
            key_str = self._GetKeyString(key)
            if not key_str:
                return
            
            # 检查所有注册的热键
            for hotkey_id, hotkey_info in self._hotkeys.items():
                if self._IsHotkeyMatch(hotkey_info, key_str):
                    # 更新触发时间
                    self._last_trigger_time = time.time()
                    
                    # 异步执行回调，避免阻塞监听器
                    threading.Thread(
                        target=self._ExecuteCallback,
                        args=(hotkey_info.Callback,),
                        daemon=True
                    ).start()
                    break
                    
        except Exception:
            # 忽略匹配检查异常
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
                    'space': ' '
                }
                return special_keys.get(key.name, key.name)
            else:
                return str(key).replace('Key.', '').lower()
        except:
            return None
    
    def _IsHotkeyMatch(self, hotkey_info: HotkeyInfo, key_str: str) -> bool:
        """检查热键是否匹配"""
        # 检查按键是否匹配
        if hotkey_info.Key != key_str:
            return False
        
        # 检查修饰符是否匹配
        required_modifiers = set(hotkey_info.Modifiers)
        return self._current_modifiers == required_modifiers
    
    def _ExecuteCallback(self, callback: Callable[[], None]) -> None:
        """安全执行回调函数"""
        try:
            callback()
        except Exception:
            # 忽略回调函数异常，避免影响系统稳定性
            pass
    
    #endregion
    
    #region 资源清理
    
    def __del__(self):
        """析构函数，确保资源清理"""
        try:
            self.UnregisterAll()
        except:
            pass
    
    #endregion