# -*- coding: utf-8 -*-
"""
核心模块接口定义
定义了核心业务逻辑模块的所有接口
"""

from abc import ABC, abstractmethod
from typing import Tuple, List, Optional
from dataclasses import dataclass


#region 数据结构定义

@dataclass
class Point:
    """坐标点数据结构"""
    X: int
    Y: int


@dataclass
class Rectangle:
    """矩形区域数据结构"""
    X: int
    Y: int
    Width: int
    Height: int
    
    @property
    def Center(self) -> Point:
        """获取矩形中心点"""
        return Point(
            self.X + self.Width // 2,
            self.Y + self.Height // 2
        )


@dataclass
class GridCell:
    """网格单元格数据结构"""
    Index: int
    Region: Rectangle
    Center: Point

#endregion


#region 核心接口定义

class IGridRenderer(ABC):
    """网格渲染接口"""
    
    @abstractmethod
    def ShowGrid(self, cells: List[GridCell], activeRegion: Rectangle) -> None:
        """显示网格"""
        pass
    
    @abstractmethod
    def HideGrid(self) -> None:
        """隐藏网格"""
        pass
    
    @abstractmethod
    def UpdateActiveRegion(self, region: Rectangle) -> None:
        """更新当前活跃区域"""
        pass


class IInputListener(ABC):
    """输入监听接口"""
    
    @abstractmethod
    def StartListening(self) -> None:
        """开始监听输入"""
        pass
    
    @abstractmethod
    def StopListening(self) -> None:
        """停止监听输入"""
        pass
    
    @abstractmethod
    def RegisterKeyHandler(self, handler) -> None:
        """注册按键处理器"""
        pass


class IMouseController(ABC):
    """鼠标控制接口"""
    
    @abstractmethod
    def LeftClick(self, point: Point) -> None:
        """左键单击"""
        pass
    
    @abstractmethod
    def RightClick(self, point: Point) -> None:
        """右键单击"""
        pass
    
    @abstractmethod
    def MoveTo(self, point: Point) -> None:
        """移动到指定位置"""
        pass


class ISystemHook(ABC):
    """系统钩子接口"""
    
    @abstractmethod
    def RegisterHotkey(self, key: str, callback) -> None:
        """注册全局热键"""
        pass
    
    @abstractmethod
    def UnregisterHotkey(self, key: str) -> None:
        """注销全局热键"""
        pass

#endregion