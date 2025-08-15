# -*- coding: utf-8 -*-
"""
平台操作模块
提供Windows系统底层交互功能，包括热键监听、鼠标控制等
"""

# 接口定义
from .interfaces import (
    # 接口
    IHotkeyManager,
    IKeyboardListener,
    IMouseController,
    IScreenManager,
    ISystemManager,
    
    # 数据结构
    HotkeyModifier,
    MouseButton,
    HotkeyInfo,
    SystemMetrics,
    
    # 异常类
    IPlatformException,
    HotkeyRegistrationError,
    MouseOperationError,
    SystemResourceError
)

# 具体实现
from .hotkey_manager import HotkeyManager
from .keyboard_listener import KeyboardListener
from .mouse_controller import MouseController
from .screen_manager import ScreenManager
from .system_manager import SystemManager

# 统一管理器
from .platform_manager import PlatformManager

# 版本信息
__version__ = "1.0.0"
__author__ = "KeyboardClicker Development Team"

# 导出列表
__all__ = [
    # 接口
    'IHotkeyManager',
    'IKeyboardListener', 
    'IMouseController',
    'IScreenManager',
    'ISystemManager',
    
    # 实现类
    'HotkeyManager',
    'KeyboardListener',
    'MouseController', 
    'ScreenManager',
    'SystemManager',
    
    # 管理器
    'PlatformManager',
    
    # 数据结构
    'HotkeyModifier',
    'MouseButton',
    'HotkeyInfo',
    'SystemMetrics',
    
    # 异常类
    'IPlatformException',
    'HotkeyRegistrationError',
    'MouseOperationError',
    'SystemResourceError'
]


#region 便捷函数

def CreatePlatformManager() -> PlatformManager:
    """创建平台管理器实例"""
    return PlatformManager()


def CheckSystemRequirements() -> dict:
    """检查系统兼容性"""
    try:
        system_manager = SystemManager()
        return system_manager.CheckSystemCompatibility()
    except Exception as e:
        return {'error': str(e), 'requirements_check_failed': True}


def GetSystemInfo() -> dict:
    """获取详细系统信息"""
    try:
        system_manager = SystemManager()
        return system_manager.GetDetailedSystemInfo()
    except Exception as e:
        return {'error': str(e), 'system_info_failed': True}

#endregion