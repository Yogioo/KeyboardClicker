# -*- coding: utf-8 -*-
"""
网格坐标系统主控制器
整合所有核心模块，提供统一的操作接口
"""

from typing import Optional, Callable, List
import time
from .interfaces import (
    Rectangle, Point, IGridRenderer, IMouseController, 
    IInputListener, ISystemHook
)
from .grid_state import GridStateManager, GridStateType
from .grid_calculator import GridCalculator
from .input_processor import InputProcessor, CommandType
from .command_executor import CommandExecutor, ExecutionResult


#region 事件回调定义

class GridEventCallbacks:
    """网格事件回调集合"""
    
    def __init__(self):
        self.OnSessionStarted: Optional[Callable[[Rectangle], None]] = None
        self.OnSessionEnded: Optional[Callable[[], None]] = None
        self.OnKeyProcessed: Optional[Callable[[str, Rectangle], None]] = None
        self.OnCommandExecuted: Optional[Callable[[ExecutionResult], None]] = None
        self.OnError: Optional[Callable[[str, Exception], None]] = None

#endregion


#region 主控制器类

class GridCoordinateSystem:
    """网格坐标系统主控制器
    
    整合所有核心模块，提供完整的网格坐标系统功能
    """
    
    def __init__(self, 
                 renderer: Optional[IGridRenderer] = None,
                 mouseController: Optional[IMouseController] = None,
                 inputListener: Optional[IInputListener] = None,
                 systemHook: Optional[ISystemHook] = None):
        
        # 核心模块
        self._stateManager = GridStateManager()
        self._calculator = GridCalculator()
        self._inputProcessor = InputProcessor()
        self._commandExecutor = CommandExecutor(mouseController)
        
        # 外部依赖
        self._renderer = renderer
        self._mouseController = mouseController
        self._inputListener = inputListener
        self._systemHook = systemHook
        
        # 事件回调
        self._callbacks = GridEventCallbacks()
        
        # 性能监控
        self._lastKeyTime = 0.0
        self._maxResponseTime = 0.050  # 50ms最大响应时间
        
        # 设置内部回调
        self._setupInternalCallbacks()
    
    def _setupInternalCallbacks(self) -> None:
        """设置内部回调"""
        # 设置指令执行完成回调
        self._commandExecutor.SetExecutionCompleteCallback(self._onCommandExecuted)
        
        # 注册热键
        if self._systemHook:
            self._systemHook.RegisterHotkey("alt+g", self._onActivationHotkey)
        
        # 注册输入监听
        if self._inputListener:
            self._inputListener.RegisterKeyHandler(self._onKeyInput)
    
    def SetCallbacks(self, callbacks: GridEventCallbacks) -> None:
        """设置事件回调
        
        Args:
            callbacks: 事件回调集合
        """
        self._callbacks = callbacks
    
    def SetRenderer(self, renderer: IGridRenderer) -> None:
        """设置渲染器
        
        Args:
            renderer: 网格渲染器
        """
        self._renderer = renderer
    
    def SetMouseController(self, controller: IMouseController) -> None:
        """设置鼠标控制器
        
        Args:
            controller: 鼠标控制器
        """
        self._mouseController = controller
        self._commandExecutor.SetMouseController(controller)
    
    def StartSession(self, screenRect: Optional[Rectangle] = None) -> bool:
        """开始网格会话
        
        Args:
            screenRect: 屏幕区域，如果为None则使用默认屏幕
            
        Returns:
            是否成功开始会话
        """
        try:
            # 如果已经在会话中，先结束当前会话
            if self._stateManager.IsActive():
                self.EndSession()
            
            # 使用默认屏幕区域
            if screenRect is None:
                screenRect = Rectangle(0, 0, 1920, 1080)  # 默认1080p
            
            # 开始新会话
            self._stateManager.StartSession(screenRect)
            
            # 显示初始网格
            if self._renderer:
                cells = self._calculator.CalculateGrid3x3(screenRect)
                self._renderer.ShowGrid(cells, screenRect)
            
            # 开始输入监听
            if self._inputListener:
                self._inputListener.StartListening()
            
            # 触发回调
            if self._callbacks.OnSessionStarted:
                self._callbacks.OnSessionStarted(screenRect)
            
            return True
            
        except Exception as e:
            self._handleError("开始会话失败", e)
            return False
    
    def EndSession(self) -> None:
        """结束网格会话"""
        try:
            # 停止输入监听
            if self._inputListener:
                self._inputListener.StopListening()
            
            # 隐藏网格
            if self._renderer:
                self._renderer.HideGrid()
            
            # 重置状态
            self._stateManager.EndSession()
            
            # 触发回调
            if self._callbacks.OnSessionEnded:
                self._callbacks.OnSessionEnded()
                
        except Exception as e:
            self._handleError("结束会话失败", e)
    
    def ProcessKeyInput(self, key: str) -> bool:
        """处理按键输入
        
        Args:
            key: 按键字符
            
        Returns:
            是否成功处理
        """
        try:
            # 记录处理时间
            startTime = time.time()
            
            # 检查是否为控制键
            if self._inputProcessor.IsControlKey(key):
                if key.upper() in ['ESC', 'ESCAPE']:
                    self.EndSession()
                    return True
            
            # 检查会话状态
            if not self._stateManager.IsActive():
                return False
            
            # 检查是否为有效按键
            if not self._inputProcessor.IsValidGridKey(key):
                return False
            
            # 添加按键到路径
            if not self._stateManager.ProcessKeyInput(key):
                return False
            
            # 获取当前路径
            currentPath = self._stateManager.GetKeyPath()
            
            # 计算新的活跃区域
            targetPoint, regions = self._calculator.ProcessKeyPath(
                currentPath, 
                self._stateManager.State.ScreenRect
            )
            
            if targetPoint is None or not regions:
                return False
            
            # 更新活跃区域
            newRegion = regions[-1]
            self._stateManager.UpdateRegion(newRegion)
            self._stateManager.SetTarget(targetPoint)
            
            # 更新渲染
            if self._renderer:
                cells = self._calculator.CalculateGrid3x3(newRegion)
                self._renderer.ShowGrid(cells, newRegion)
            
            # 检查响应时间
            processingTime = time.time() - startTime
            if processingTime > self._maxResponseTime:
                print(f"警告: 按键处理时间超过预期 ({processingTime:.3f}s)")
            
            # 触发回调
            if self._callbacks.OnKeyProcessed:
                self._callbacks.OnKeyProcessed(key, newRegion)
            
            return True
            
        except Exception as e:
            self._handleError(f"处理按键 '{key}' 失败", e)
            return False
    
    def ExecuteCommand(self, keySequence: str) -> bool:
        """执行指令
        
        Args:
            keySequence: 完整的按键序列
            
        Returns:
            是否成功执行
        """
        try:
            # 解析指令
            command = self._inputProcessor.ParseCommand(keySequence)
            
            if not command.IsValid:
                return False
            
            # 计算目标点
            targetPoint, _ = self._calculator.ProcessKeyPath(
                command.KeySequence,
                self._stateManager.State.ScreenRect
            )
            
            if targetPoint is None:
                return False
            
            # 设置处理状态
            self._stateManager.SetProcessing(True)
            
            # 执行指令
            result = self._commandExecutor.ExecuteCommand(command, targetPoint)
            
            # 如果执行成功，结束会话
            if result.Success:
                self.EndSession()
            else:
                self._stateManager.SetProcessing(False)
            
            return result.Success
            
        except Exception as e:
            self._handleError(f"执行指令 '{keySequence}' 失败", e)
            self._stateManager.SetProcessing(False)
            return False
    
    def _onActivationHotkey(self) -> None:
        """激活热键回调"""
        if not self._stateManager.IsActive():
            self.StartSession()
        else:
            self.EndSession()
    
    def _onKeyInput(self, key: str) -> None:
        """按键输入回调"""
        if self._stateManager.IsActive():
            self.ProcessKeyInput(key)
    
    def _onCommandExecuted(self, result: ExecutionResult) -> None:
        """指令执行完成回调"""
        if self._callbacks.OnCommandExecuted:
            self._callbacks.OnCommandExecuted(result)
    
    def _handleError(self, message: str, error: Exception) -> None:
        """处理错误"""
        if self._callbacks.OnError:
            self._callbacks.OnError(message, error)
        else:
            print(f"错误: {message} - {str(error)}")
    
    def GetCurrentState(self) -> dict:
        """获取当前状态信息
        
        Returns:
            状态信息字典
        """
        state = self._stateManager.State
        return {
            'IsActive': self._stateManager.IsActive(),
            'IsProcessing': self._stateManager.IsProcessing(),
            'CurrentLevel': state.CurrentLevel,
            'KeyPath': state.GetCurrentKeyPath(),
            'ActiveRegion': {
                'X': state.ActiveRegion.X if state.ActiveRegion else 0,
                'Y': state.ActiveRegion.Y if state.ActiveRegion else 0,
                'Width': state.ActiveRegion.Width if state.ActiveRegion else 0,
                'Height': state.ActiveRegion.Height if state.ActiveRegion else 0
            } if state.ActiveRegion else None,
            'TargetPoint': {
                'X': state.TargetPoint.X if state.TargetPoint else 0,
                'Y': state.TargetPoint.Y if state.TargetPoint else 0
            } if state.TargetPoint else None
        }
    
    def IsActive(self) -> bool:
        """检查是否处于激活状态"""
        return self._stateManager.IsActive()
    
    def IsProcessing(self) -> bool:
        """检查是否正在处理"""
        return self._stateManager.IsProcessing()

#endregion