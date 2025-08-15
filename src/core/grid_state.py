# -*- coding: utf-8 -*-
"""
网格状态管理
管理网格坐标系统的状态和状态转换
"""

from enum import Enum
from typing import List, Optional
from dataclasses import dataclass, field
from .interfaces import Rectangle, Point


#region 状态枚举定义

class GridStateType(Enum):
    """网格状态枚举"""
    INACTIVE = "inactive"      # 未激活状态
    ACTIVE = "active"          # 激活状态，等待输入
    PROCESSING = "processing"  # 处理中状态

#endregion


#region 网格状态类

@dataclass
class GridState:
    """网格状态数据类"""
    
    # 状态相关
    StateType: GridStateType = GridStateType.INACTIVE
    CurrentLevel: int = 0
    IsProcessing: bool = False
    
    # 路径相关
    KeyPath: List[str] = field(default_factory=list)
    
    # 区域相关
    ActiveRegion: Optional[Rectangle] = None
    ScreenRect: Optional[Rectangle] = None
    
    # 目标相关
    TargetPoint: Optional[Point] = None
    
    def Reset(self) -> None:
        """重置状态到初始状态"""
        self.StateType = GridStateType.INACTIVE
        self.CurrentLevel = 0
        self.IsProcessing = False
        self.KeyPath.clear()
        self.ActiveRegion = None
        self.TargetPoint = None
    
    def StartNewSession(self, screenRect: Rectangle) -> None:
        """开始新的定位会话"""
        self.Reset()
        self.StateType = GridStateType.ACTIVE
        self.ScreenRect = screenRect
        self.ActiveRegion = screenRect
        self.CurrentLevel = 0
    
    def AddKeyToPath(self, key: str) -> None:
        """添加按键到路径"""
        if not self.IsProcessing:
            self.KeyPath.append(key)
            self.CurrentLevel = len(self.KeyPath)
    
    def SetProcessing(self, processing: bool) -> None:
        """设置处理状态"""
        self.IsProcessing = processing
        if processing:
            self.StateType = GridStateType.PROCESSING
        elif self.StateType == GridStateType.PROCESSING:
            self.StateType = GridStateType.ACTIVE
    
    def UpdateActiveRegion(self, region: Rectangle) -> None:
        """更新当前活跃区域"""
        self.ActiveRegion = region
    
    def SetTargetPoint(self, point: Point) -> None:
        """设置目标点"""
        self.TargetPoint = point
    
    def CanProcessInput(self) -> bool:
        """检查是否可以处理输入"""
        return (self.StateType == GridStateType.ACTIVE and 
                not self.IsProcessing)
    
    def GetCurrentKeyPath(self) -> str:
        """获取当前按键路径字符串"""
        return ''.join(self.KeyPath)

#endregion


#region 状态管理器

class GridStateManager:
    """网格状态管理器"""
    
    def __init__(self):
        self._state = GridState()
    
    @property
    def State(self) -> GridState:
        """获取当前状态"""
        return self._state
    
    def StartSession(self, screenRect: Rectangle) -> None:
        """开始新会话"""
        self._state.StartNewSession(screenRect)
    
    def EndSession(self) -> None:
        """结束会话"""
        self._state.Reset()
    
    def ProcessKeyInput(self, key: str) -> bool:
        """处理按键输入"""
        if not self._state.CanProcessInput():
            return False
        
        self._state.AddKeyToPath(key)
        return True
    
    def SetProcessing(self, processing: bool) -> None:
        """设置处理状态"""
        self._state.SetProcessing(processing)
    
    def UpdateRegion(self, region: Rectangle) -> None:
        """更新活跃区域"""
        self._state.UpdateActiveRegion(region)
    
    def SetTarget(self, point: Point) -> None:
        """设置目标点"""
        self._state.SetTargetPoint(point)
    
    def IsActive(self) -> bool:
        """检查是否处于激活状态"""
        return self._state.StateType != GridStateType.INACTIVE
    
    def IsProcessing(self) -> bool:
        """检查是否正在处理"""
        return self._state.IsProcessing
    
    def GetKeyPath(self) -> str:
        """获取按键路径"""
        return self._state.GetCurrentKeyPath()
    
    def GetCurrentLevel(self) -> int:
        """获取当前层级"""
        return self._state.CurrentLevel

#endregion