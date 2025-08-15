# -*- coding: utf-8 -*-
"""
平台操作模块接口定义
定义了Windows平台特定操作的接口
"""

from abc import ABC, abstractmethod
from typing import Callable, Optional, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum


#region 数据结构定义

class HotkeyModifier(Enum):
    """热键修饰符枚举"""
    ALT = "alt"
    CTRL = "ctrl"
    SHIFT = "shift"
    WIN = "win"


class MouseButton(Enum):
    """鼠标按键枚举"""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


@dataclass
class HotkeyInfo:
    """热键信息数据结构"""
    Key: str
    Modifiers: Tuple[HotkeyModifier, ...]
    Callback: Callable[[], None]
    IsRegistered: bool = False


@dataclass
class SystemMetrics:
    """系统性能指标数据结构"""
    CpuUsagePercent: float
    MemoryUsageMb: float
    HandleCount: int
    ResponseTimeMs: float

#endregion


#region 平台接口定义

class IHotkeyManager(ABC):
    """全局热键管理器接口"""
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def UnregisterHotkey(self, key: str, modifiers: Tuple[HotkeyModifier, ...]) -> bool:
        """注销指定热键"""
        pass
    
    @abstractmethod
    def UnregisterAll(self) -> None:
        """注销所有热键"""
        pass
    
    @abstractmethod
    def IsHotkeyRegistered(self, key: str, modifiers: Tuple[HotkeyModifier, ...]) -> bool:
        """检查热键是否已注册"""
        pass


class IKeyboardListener(ABC):
    """全局键盘监听器接口"""
    
    @abstractmethod
    def StartListening(self) -> bool:
        """开始全局键盘监听"""
        pass
    
    @abstractmethod
    def StopListening(self) -> None:
        """停止键盘监听"""
        pass
    
    @abstractmethod
    def SetKeyFilter(self, allowed_keys: Tuple[str, ...]) -> None:
        """设置允许的按键过滤器"""
        pass
    
    @abstractmethod
    def RegisterKeyHandler(self, handler: Callable[[str], None]) -> None:
        """注册按键处理器"""
        pass
    
    @abstractmethod
    def IsListening(self) -> bool:
        """检查是否正在监听"""
        pass


class IMouseController(ABC):
    """鼠标控制器接口"""
    
    @abstractmethod
    def MoveTo(self, x: int, y: int) -> bool:
        """移动鼠标到指定坐标"""
        pass
    
    @abstractmethod
    def LeftClick(self, x: int, y: int) -> bool:
        """执行左键单击"""
        pass
    
    @abstractmethod
    def RightClick(self, x: int, y: int) -> bool:
        """执行右键单击"""
        pass
    
    @abstractmethod
    def DoubleClick(self, x: int, y: int) -> bool:
        """执行双击"""
        pass
    
    @abstractmethod
    def GetCursorPosition(self) -> Tuple[int, int]:
        """获取当前光标位置"""
        pass
    
    @abstractmethod
    def SmoothMoveTo(self, x: int, y: int, duration_ms: int = 100) -> bool:
        """平滑移动到指定位置"""
        pass


class IScreenManager(ABC):
    """屏幕管理器接口"""
    
    @abstractmethod
    def GetPrimaryScreenRect(self) -> Tuple[int, int, int, int]:
        """获取主显示器矩形 (x, y, width, height)"""
        pass
    
    @abstractmethod
    def GetScreenDpi(self) -> float:
        """获取屏幕DPI缩放比例"""
        pass
    
    @abstractmethod
    def ValidateCoordinates(self, x: int, y: int) -> bool:
        """验证坐标是否在屏幕范围内"""
        pass
    
    @abstractmethod
    def ScreenToClient(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """屏幕坐标转换为客户端坐标"""
        pass


class ISystemManager(ABC):
    """系统资源管理器接口"""
    
    @abstractmethod
    def GetSystemMetrics(self) -> SystemMetrics:
        """获取系统性能指标"""
        pass
    
    @abstractmethod
    def SetProcessPriority(self, priority: str = "normal") -> bool:
        """设置进程优先级"""
        pass
    
    @abstractmethod
    def CheckSystemCompatibility(self) -> Dict[str, bool]:
        """检查系统兼容性"""
        pass
    
    @abstractmethod
    def MonitorResourceUsage(self, callback: Callable[[SystemMetrics], None]) -> None:
        """开始监控资源使用情况"""
        pass
    
    @abstractmethod
    def StopResourceMonitoring(self) -> None:
        """停止资源监控"""
        pass


class IPlatformException(Exception):
    """平台操作异常基类"""
    
    def __init__(self, message: str, error_code: Optional[int] = None):
        super().__init__(message)
        self._error_code = error_code
    
    @property
    def ErrorCode(self) -> Optional[int]:
        return self._error_code


class HotkeyRegistrationError(IPlatformException):
    """热键注册异常"""
    pass


class MouseOperationError(IPlatformException):
    """鼠标操作异常"""
    pass


class SystemResourceError(IPlatformException):
    """系统资源异常"""
    pass

#endregion