# -*- coding: utf-8 -*-
"""
核心业务逻辑模块

提供网格坐标系统的核心功能：
- 网格计算引擎
- 输入处理器  
- 指令执行器
- 状态管理器
"""

# 基础数据结构和接口
from .interfaces import (
    Point, Rectangle, GridCell,
    IGridRenderer, IInputListener, IMouseController, ISystemHook
)

# 状态管理
from .grid_state import (
    GridStateType, GridState, GridStateManager
)

# 网格计算
from .grid_calculator import GridCalculator

# 输入处理
from .input_processor import (
    CommandType, ParsedCommand, InputProcessor
)

# 指令执行
from .command_executor import (
    ExecutionResult, CommandExecutor
)

# 主控制器
from .grid_coordinate_system import (
    GridEventCallbacks, GridCoordinateSystem
)

# 导出的公共接口
__all__ = [
    # 数据结构
    'Point', 'Rectangle', 'GridCell',
    
    # 接口定义
    'IGridRenderer', 'IInputListener', 'IMouseController', 'ISystemHook',
    
    # 状态管理
    'GridStateType', 'GridState', 'GridStateManager',
    
    # 网格计算
    'GridCalculator',
    
    # 输入处理
    'CommandType', 'ParsedCommand', 'InputProcessor',
    
    # 指令执行
    'ExecutionResult', 'CommandExecutor',
    
    # 主控制器
    'GridEventCallbacks', 'GridCoordinateSystem'
]