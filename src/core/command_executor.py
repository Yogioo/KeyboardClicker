# -*- coding: utf-8 -*-
"""
指令执行器
执行各种鼠标操作指令
"""

from typing import Optional, Callable
from .interfaces import Point, IMouseController
from .input_processor import CommandType, ParsedCommand


#region 执行结果定义

class ExecutionResult:
    """执行结果"""
    
    def __init__(self, success: bool, message: str = "", error: Optional[Exception] = None):
        self.Success = success
        self.Message = message
        self.Error = error
    
    @staticmethod
    def CreateSuccess(message: str = "") -> 'ExecutionResult':
        """创建成功结果"""
        return ExecutionResult(True, message)
    
    @staticmethod
    def CreateFailure(message: str, error: Optional[Exception] = None) -> 'ExecutionResult':
        """创建失败结果"""
        return ExecutionResult(False, message, error)

#endregion


#region 指令执行器核心类

class CommandExecutor:
    """指令执行器
    
    负责执行各种鼠标操作指令
    """
    
    def __init__(self, mouseController: Optional[IMouseController] = None):
        self._mouseController = mouseController
        self._onExecutionComplete: Optional[Callable[[ExecutionResult], None]] = None
    
    def SetMouseController(self, controller: IMouseController) -> None:
        """设置鼠标控制器
        
        Args:
            controller: 鼠标控制器实例
        """
        self._mouseController = controller
    
    def SetExecutionCompleteCallback(self, callback: Callable[[ExecutionResult], None]) -> None:
        """设置执行完成回调
        
        Args:
            callback: 回调函数
        """
        self._onExecutionComplete = callback
    
    def ExecuteCommand(self, command: ParsedCommand, targetPoint: Point) -> ExecutionResult:
        """执行指令
        
        Args:
            command: 要执行的指令
            targetPoint: 目标点
            
        Returns:
            执行结果
        """
        if not command.IsValid:
            return ExecutionResult.CreateFailure("无效的指令")
        
        if self._mouseController is None:
            return ExecutionResult.CreateFailure("鼠标控制器未设置")
        
        try:
            result = None
            
            if command.CommandType == CommandType.DEFAULT_CLICK:
                result = self.ExecuteDefaultClick(targetPoint)
            elif command.CommandType == CommandType.RIGHT_CLICK:
                result = self.ExecuteRightClick(targetPoint)
            elif command.CommandType == CommandType.HOVER:
                result = self.ExecuteHover(targetPoint)
            else:
                result = ExecutionResult.CreateFailure(f"不支持的指令类型: {command.CommandType}")
            
            # 触发完成回调
            if self._onExecutionComplete:
                self._onExecutionComplete(result)
            
            return result
            
        except Exception as e:
            result = ExecutionResult.CreateFailure(f"执行指令时发生错误: {str(e)}", e)
            
            if self._onExecutionComplete:
                self._onExecutionComplete(result)
            
            return result
    
    def ExecuteDefaultClick(self, targetPoint: Point) -> ExecutionResult:
        """执行默认左键单击
        
        Args:
            targetPoint: 目标点
            
        Returns:
            执行结果
        """
        try:
            if self._mouseController is None:
                return ExecutionResult.CreateFailure("鼠标控制器未设置")
            
            # 执行左键单击
            self._mouseController.LeftClick(targetPoint)
            
            return ExecutionResult.CreateSuccess(
                f"成功执行左键单击，位置: ({targetPoint.X}, {targetPoint.Y})"
            )
            
        except Exception as e:
            return ExecutionResult.CreateFailure(
                f"执行左键单击失败: {str(e)}", e
            )
    
    def ExecuteRightClick(self, targetPoint: Point) -> ExecutionResult:
        """执行右键单击
        
        Args:
            targetPoint: 目标点
            
        Returns:
            执行结果
        """
        try:
            if self._mouseController is None:
                return ExecutionResult.CreateFailure("鼠标控制器未设置")
            
            # 执行右键单击
            self._mouseController.RightClick(targetPoint)
            
            return ExecutionResult.CreateSuccess(
                f"成功执行右键单击，位置: ({targetPoint.X}, {targetPoint.Y})"
            )
            
        except Exception as e:
            return ExecutionResult.CreateFailure(
                f"执行右键单击失败: {str(e)}", e
            )
    
    def ExecuteHover(self, targetPoint: Point) -> ExecutionResult:
        """执行悬停操作
        
        Args:
            targetPoint: 目标点
            
        Returns:
            执行结果
        """
        try:
            if self._mouseController is None:
                return ExecutionResult.CreateFailure("鼠标控制器未设置")
            
            # 移动到目标位置
            self._mouseController.MoveTo(targetPoint)
            
            return ExecutionResult.CreateSuccess(
                f"成功移动到位置: ({targetPoint.X}, {targetPoint.Y})"
            )
            
        except Exception as e:
            return ExecutionResult.CreateFailure(
                f"移动鼠标失败: {str(e)}", e
            )
    
    def CanExecute(self, command: ParsedCommand) -> bool:
        """检查是否可以执行指令
        
        Args:
            command: 要检查的指令
            
        Returns:
            是否可以执行
        """
        return (command.IsValid and 
                self._mouseController is not None and
                command.CommandType != CommandType.INVALID)
    
    def GetSupportedCommands(self) -> list[CommandType]:
        """获取支持的指令类型
        
        Returns:
            支持的指令类型列表
        """
        return [
            CommandType.DEFAULT_CLICK,
            CommandType.RIGHT_CLICK,
            CommandType.HOVER
        ]

#endregion