# -*- coding: utf-8 -*-
"""
CommandExecutor单元测试
测试指令执行器的所有功能
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from src.core.command_executor import CommandExecutor, ExecutionResult
from src.core.input_processor import CommandType, ParsedCommand
from src.core.interfaces import Point, IMouseController


#region Mock类定义

class MockMouseController(IMouseController):
    """Mock鼠标控制器"""
    
    def __init__(self):
        self.leftClickCalled = False
        self.rightClickCalled = False
        self.moveTooCalled = False
        self.lastPoint = None
        self.shouldThrowError = False
        self.errorMessage = "Mock error"
    
    def LeftClick(self, point: Point) -> None:
        if self.shouldThrowError:
            raise Exception(self.errorMessage)
        self.leftClickCalled = True
        self.lastPoint = point
    
    def RightClick(self, point: Point) -> None:
        if self.shouldThrowError:
            raise Exception(self.errorMessage)
        self.rightClickCalled = True
        self.lastPoint = point
    
    def MoveTo(self, point: Point) -> None:
        if self.shouldThrowError:
            raise Exception(self.errorMessage)
        self.moveTooCalled = True
        self.lastPoint = point
    
    def Reset(self):
        """重置状态"""
        self.leftClickCalled = False
        self.rightClickCalled = False
        self.moveTooCalled = False
        self.lastPoint = None
        self.shouldThrowError = False

#endregion


#region 基础测试类

class TestCommandExecutor(unittest.TestCase):
    """CommandExecutor测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.mockController = MockMouseController()
        self.executor = CommandExecutor(self.mockController)
        self.testPoint = Point(100, 200)
    
    def tearDown(self):
        """测试后清理"""
        self.mockController.Reset()

#endregion


#region 初始化测试

class TestInitialization(TestCommandExecutor):
    """初始化测试"""
    
    def test_构造函数_带鼠标控制器(self):
        """测试带鼠标控制器的构造函数"""
        executor = CommandExecutor(self.mockController)
        self.assertIsNotNone(executor)
    
    def test_构造函数_无鼠标控制器(self):
        """测试无鼠标控制器的构造函数"""
        executor = CommandExecutor()
        self.assertIsNotNone(executor)
    
    def test_SetMouseController_设置控制器(self):
        """测试设置鼠标控制器"""
        executor = CommandExecutor()
        executor.SetMouseController(self.mockController)
        
        # 验证控制器已设置
        command = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        result = executor.ExecuteCommand(command, self.testPoint)
        self.assertTrue(result.Success)
    
    def test_SetExecutionCompleteCallback_设置回调(self):
        """测试设置执行完成回调"""
        callbackCalled = False
        receivedResult = None
        
        def callback(result):
            nonlocal callbackCalled, receivedResult
            callbackCalled = True
            receivedResult = result
        
        self.executor.SetExecutionCompleteCallback(callback)
        
        command = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        result = self.executor.ExecuteCommand(command, self.testPoint)
        
        self.assertTrue(callbackCalled)
        self.assertEqual(receivedResult, result)

#endregion


#region 执行结果测试

class TestExecutionResult(unittest.TestCase):
    """执行结果测试"""
    
    def test_CreateSuccess_成功结果(self):
        """测试创建成功结果"""
        message = "操作成功"
        result = ExecutionResult.CreateSuccess(message)
        
        self.assertTrue(result.Success)
        self.assertEqual(result.Message, message)
        self.assertIsNone(result.Error)
    
    def test_CreateSuccess_空消息(self):
        """测试创建成功结果(空消息)"""
        result = ExecutionResult.CreateSuccess()
        
        self.assertTrue(result.Success)
        self.assertEqual(result.Message, "")
        self.assertIsNone(result.Error)
    
    def test_CreateFailure_失败结果(self):
        """测试创建失败结果"""
        message = "操作失败"
        error = Exception("测试错误")
        result = ExecutionResult.CreateFailure(message, error)
        
        self.assertFalse(result.Success)
        self.assertEqual(result.Message, message)
        self.assertEqual(result.Error, error)
    
    def test_CreateFailure_无错误对象(self):
        """测试创建失败结果(无错误对象)"""
        message = "操作失败"
        result = ExecutionResult.CreateFailure(message)
        
        self.assertFalse(result.Success)
        self.assertEqual(result.Message, message)
        self.assertIsNone(result.Error)

#endregion


#region 默认左键点击测试

class TestDefaultClick(TestCommandExecutor):
    """默认左键点击测试"""
    
    def test_ExecuteDefaultClick_成功执行(self):
        """测试成功执行默认左键点击"""
        result = self.executor.ExecuteDefaultClick(self.testPoint)
        
        self.assertTrue(result.Success)
        self.assertTrue(self.mockController.leftClickCalled)
        self.assertEqual(self.mockController.lastPoint, self.testPoint)
        self.assertIn("成功执行左键单击", result.Message)
        self.assertIn(f"({self.testPoint.X}, {self.testPoint.Y})", result.Message)
    
    def test_ExecuteDefaultClick_无鼠标控制器(self):
        """测试无鼠标控制器时的默认点击"""
        executor = CommandExecutor()
        result = executor.ExecuteDefaultClick(self.testPoint)
        
        self.assertFalse(result.Success)
        self.assertIn("鼠标控制器未设置", result.Message)
    
    def test_ExecuteDefaultClick_控制器异常(self):
        """测试鼠标控制器异常"""
        self.mockController.shouldThrowError = True
        result = self.executor.ExecuteDefaultClick(self.testPoint)
        
        self.assertFalse(result.Success)
        self.assertIn("执行左键单击失败", result.Message)
        self.assertIsNotNone(result.Error)

#endregion


#region 右键点击测试

class TestRightClick(TestCommandExecutor):
    """右键点击测试"""
    
    def test_ExecuteRightClick_成功执行(self):
        """测试成功执行右键点击"""
        result = self.executor.ExecuteRightClick(self.testPoint)
        
        self.assertTrue(result.Success)
        self.assertTrue(self.mockController.rightClickCalled)
        self.assertEqual(self.mockController.lastPoint, self.testPoint)
        self.assertIn("成功执行右键单击", result.Message)
        self.assertIn(f"({self.testPoint.X}, {self.testPoint.Y})", result.Message)
    
    def test_ExecuteRightClick_无鼠标控制器(self):
        """测试无鼠标控制器时的右键点击"""
        executor = CommandExecutor()
        result = executor.ExecuteRightClick(self.testPoint)
        
        self.assertFalse(result.Success)
        self.assertIn("鼠标控制器未设置", result.Message)
    
    def test_ExecuteRightClick_控制器异常(self):
        """测试鼠标控制器异常"""
        self.mockController.shouldThrowError = True
        result = self.executor.ExecuteRightClick(self.testPoint)
        
        self.assertFalse(result.Success)
        self.assertIn("执行右键单击失败", result.Message)
        self.assertIsNotNone(result.Error)

#endregion


#region 悬停操作测试

class TestHover(TestCommandExecutor):
    """悬停操作测试"""
    
    def test_ExecuteHover_成功执行(self):
        """测试成功执行悬停操作"""
        result = self.executor.ExecuteHover(self.testPoint)
        
        self.assertTrue(result.Success)
        self.assertTrue(self.mockController.moveTooCalled)
        self.assertEqual(self.mockController.lastPoint, self.testPoint)
        self.assertIn("成功移动到位置", result.Message)
        self.assertIn(f"({self.testPoint.X}, {self.testPoint.Y})", result.Message)
    
    def test_ExecuteHover_无鼠标控制器(self):
        """测试无鼠标控制器时的悬停操作"""
        executor = CommandExecutor()
        result = executor.ExecuteHover(self.testPoint)
        
        self.assertFalse(result.Success)
        self.assertIn("鼠标控制器未设置", result.Message)
    
    def test_ExecuteHover_控制器异常(self):
        """测试鼠标控制器异常"""
        self.mockController.shouldThrowError = True
        result = self.executor.ExecuteHover(self.testPoint)
        
        self.assertFalse(result.Success)
        self.assertIn("移动鼠标失败", result.Message)
        self.assertIsNotNone(result.Error)

#endregion


#region 指令执行测试

class TestCommandExecution(TestCommandExecutor):
    """指令执行测试"""
    
    def test_ExecuteCommand_默认点击指令(self):
        """测试执行默认点击指令"""
        command = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        result = self.executor.ExecuteCommand(command, self.testPoint)
        
        self.assertTrue(result.Success)
        self.assertTrue(self.mockController.leftClickCalled)
        self.assertEqual(self.mockController.lastPoint, self.testPoint)
    
    def test_ExecuteCommand_右键点击指令(self):
        """测试执行右键点击指令"""
        command = ParsedCommand("Q", CommandType.RIGHT_CLICK, "QR", True)
        result = self.executor.ExecuteCommand(command, self.testPoint)
        
        self.assertTrue(result.Success)
        self.assertTrue(self.mockController.rightClickCalled)
        self.assertEqual(self.mockController.lastPoint, self.testPoint)
    
    def test_ExecuteCommand_悬停指令(self):
        """测试执行悬停指令"""
        command = ParsedCommand("Q", CommandType.HOVER, "QH", True)
        result = self.executor.ExecuteCommand(command, self.testPoint)
        
        self.assertTrue(result.Success)
        self.assertTrue(self.mockController.moveTooCalled)
        self.assertEqual(self.mockController.lastPoint, self.testPoint)
    
    def test_ExecuteCommand_无效指令(self):
        """测试执行无效指令"""
        command = ParsedCommand("", CommandType.INVALID, "F", False)
        result = self.executor.ExecuteCommand(command, self.testPoint)
        
        self.assertFalse(result.Success)
        self.assertIn("无效的指令", result.Message)
    
    def test_ExecuteCommand_无鼠标控制器(self):
        """测试无鼠标控制器时执行指令"""
        executor = CommandExecutor()
        command = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        result = executor.ExecuteCommand(command, self.testPoint)
        
        self.assertFalse(result.Success)
        self.assertIn("鼠标控制器未设置", result.Message)
    
    def test_ExecuteCommand_不支持的指令类型(self):
        """测试不支持的指令类型"""
        # 创建一个不在处理范围内的指令类型
        command = ParsedCommand("Q", CommandType.INVALID, "Q", True)
        # 手动设置为有效，以测试不支持的类型分支
        command.IsValid = True
        
        result = self.executor.ExecuteCommand(command, self.testPoint)
        self.assertFalse(result.Success)
        self.assertIn("不支持的指令类型", result.Message)
    
    def test_ExecuteCommand_执行过程异常(self):
        """测试执行过程中发生异常"""
        self.mockController.shouldThrowError = True
        command = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        result = self.executor.ExecuteCommand(command, self.testPoint)
        
        self.assertFalse(result.Success)
        self.assertIn("执行", result.Message)
        self.assertIsNotNone(result.Error)

#endregion


#region 回调测试

class TestCallbacks(TestCommandExecutor):
    """回调测试"""
    
    def test_执行完成回调_成功情况(self):
        """测试执行完成回调(成功情况)"""
        callbackResults = []
        
        def callback(result):
            callbackResults.append(result)
        
        self.executor.SetExecutionCompleteCallback(callback)
        
        command = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        result = self.executor.ExecuteCommand(command, self.testPoint)
        
        self.assertEqual(len(callbackResults), 1)
        self.assertEqual(callbackResults[0], result)
        self.assertTrue(callbackResults[0].Success)
    
    def test_执行完成回调_失败情况(self):
        """测试执行完成回调(失败情况)"""
        callbackResults = []
        
        def callback(result):
            callbackResults.append(result)
        
        self.executor.SetExecutionCompleteCallback(callback)
        
        # 触发失败情况 - 使用会触发回调的错误（控制器异常）
        self.mockController.shouldThrowError = True
        command = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        result = self.executor.ExecuteCommand(command, self.testPoint)
        
        self.assertEqual(len(callbackResults), 1)
        self.assertEqual(callbackResults[0], result)
        self.assertFalse(callbackResults[0].Success)
    
    def test_执行完成回调_异常情况(self):
        """测试执行完成回调(异常情况)"""
        callbackResults = []
        
        def callback(result):
            callbackResults.append(result)
        
        self.executor.SetExecutionCompleteCallback(callback)
        
        # 触发异常情况
        self.mockController.shouldThrowError = True
        command = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        result = self.executor.ExecuteCommand(command, self.testPoint)
        
        self.assertEqual(len(callbackResults), 1)
        self.assertEqual(callbackResults[0], result)
        self.assertFalse(callbackResults[0].Success)
    
    def test_无回调函数(self):
        """测试无回调函数的情况"""
        # 不设置回调函数，确保不会出错
        command = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        result = self.executor.ExecuteCommand(command, self.testPoint)
        
        self.assertTrue(result.Success)

#endregion


#region 能力检查测试

class TestCapabilityChecks(TestCommandExecutor):
    """能力检查测试"""
    
    def test_CanExecute_有效指令_有控制器(self):
        """测试可以执行(有效指令，有控制器)"""
        command = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        self.assertTrue(self.executor.CanExecute(command))
    
    def test_CanExecute_无效指令(self):
        """测试不可以执行(无效指令)"""
        command = ParsedCommand("", CommandType.INVALID, "F", False)
        self.assertFalse(self.executor.CanExecute(command))
    
    def test_CanExecute_无控制器(self):
        """测试不可以执行(无控制器)"""
        executor = CommandExecutor()
        command = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        self.assertFalse(executor.CanExecute(command))
    
    def test_CanExecute_无效指令类型(self):
        """测试不可以执行(无效指令类型)"""
        command = ParsedCommand("Q", CommandType.INVALID, "Q", True)
        self.assertFalse(self.executor.CanExecute(command))
    
    def test_GetSupportedCommands_返回正确类型(self):
        """测试获取支持的指令类型"""
        supportedCommands = self.executor.GetSupportedCommands()
        
        expectedCommands = [
            CommandType.DEFAULT_CLICK,
            CommandType.RIGHT_CLICK,
            CommandType.HOVER
        ]
        
        self.assertEqual(supportedCommands, expectedCommands)

#endregion


#region 集成测试

class TestIntegration(TestCommandExecutor):
    """集成测试"""
    
    def test_完整工作流程_默认点击(self):
        """测试完整工作流程(默认点击)"""
        callbackCalled = False
        receivedResult = None
        
        def callback(result):
            nonlocal callbackCalled, receivedResult
            callbackCalled = True
            receivedResult = result
        
        # 设置回调
        self.executor.SetExecutionCompleteCallback(callback)
        
        # 创建并执行指令
        command = ParsedCommand("EDC", CommandType.DEFAULT_CLICK, "EDC", True)
        result = self.executor.ExecuteCommand(command, self.testPoint)
        
        # 验证执行结果
        self.assertTrue(result.Success)
        self.assertTrue(self.mockController.leftClickCalled)
        self.assertEqual(self.mockController.lastPoint, self.testPoint)
        
        # 验证回调
        self.assertTrue(callbackCalled)
        self.assertEqual(receivedResult, result)
    
    def test_完整工作流程_右键点击(self):
        """测试完整工作流程(右键点击)"""
        command = ParsedCommand("AS", CommandType.RIGHT_CLICK, "ASR", True)
        result = self.executor.ExecuteCommand(command, self.testPoint)
        
        self.assertTrue(result.Success)
        self.assertTrue(self.mockController.rightClickCalled)
        self.assertEqual(self.mockController.lastPoint, self.testPoint)
    
    def test_完整工作流程_悬停(self):
        """测试完整工作流程(悬停)"""
        command = ParsedCommand("QW", CommandType.HOVER, "QWH", True)
        result = self.executor.ExecuteCommand(command, self.testPoint)
        
        self.assertTrue(result.Success)
        self.assertTrue(self.mockController.moveTooCalled)
        self.assertEqual(self.mockController.lastPoint, self.testPoint)
    
    def test_多次执行_状态重置(self):
        """测试多次执行时的状态重置"""
        # 第一次执行
        command1 = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        result1 = self.executor.ExecuteCommand(command1, self.testPoint)
        self.assertTrue(result1.Success)
        
        # 重置mock状态
        self.mockController.Reset()
        
        # 第二次执行
        command2 = ParsedCommand("S", CommandType.RIGHT_CLICK, "SR", True)
        point2 = Point(300, 400)
        result2 = self.executor.ExecuteCommand(command2, point2)
        
        self.assertTrue(result2.Success)
        self.assertTrue(self.mockController.rightClickCalled)
        self.assertEqual(self.mockController.lastPoint, point2)

#endregion


#region 边界条件测试

class TestEdgeCases(TestCommandExecutor):
    """边界条件测试"""
    
    def test_坐标边界值(self):
        """测试坐标边界值"""
        edgePoints = [
            Point(0, 0),
            Point(-1, -1),
            Point(9999, 9999),
            Point(-9999, -9999)
        ]
        
        command = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        
        for point in edgePoints:
            result = self.executor.ExecuteCommand(command, point)
            self.assertTrue(result.Success)
            self.assertEqual(self.mockController.lastPoint, point)
            self.mockController.Reset()
    
    def test_多种异常情况(self):
        """测试多种异常情况"""
        # 设置抛出异常
        self.mockController.shouldThrowError = True
        self.mockController.errorMessage = "测试异常"
        
        testCases = [
            (CommandType.DEFAULT_CLICK, "左键单击"),
            (CommandType.RIGHT_CLICK, "右键单击"),
            (CommandType.HOVER, "悬停")
        ]
        
        for commandType, description in testCases:
            command = ParsedCommand("Q", commandType, "Q", True)
            result = self.executor.ExecuteCommand(command, self.testPoint)
            
            self.assertFalse(result.Success)
            self.assertIn("测试异常", str(result.Error))
    
    def test_控制器重新设置(self):
        """测试控制器重新设置"""
        # 创建新的控制器
        newController = MockMouseController()
        
        # 重新设置控制器
        self.executor.SetMouseController(newController)
        
        # 执行指令
        command = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        result = self.executor.ExecuteCommand(command, self.testPoint)
        
        # 验证使用了新的控制器
        self.assertTrue(result.Success)
        self.assertTrue(newController.leftClickCalled)
        self.assertFalse(self.mockController.leftClickCalled)

#endregion


#region 性能测试

class TestPerformance(TestCommandExecutor):
    """性能测试"""
    
    def test_大量执行性能(self):
        """测试大量执行的性能"""
        import time
        
        command = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        
        start_time = time.time()
        
        # 执行1000次
        for i in range(1000):
            point = Point(i % 100, i % 100)
            result = self.executor.ExecuteCommand(command, point)
            self.assertTrue(result.Success)
        
        elapsed_time = time.time() - start_time
        
        # 1000次执行应该在1秒内完成
        self.assertLess(elapsed_time, 1.0)
    
    def test_不同指令类型性能(self):
        """测试不同指令类型的性能"""
        import time
        
        commands = [
            ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True),
            ParsedCommand("S", CommandType.RIGHT_CLICK, "SR", True),
            ParsedCommand("C", CommandType.HOVER, "CH", True)
        ]
        
        for command in commands:
            start_time = time.time()
            
            # 每种类型执行100次
            for i in range(100):
                result = self.executor.ExecuteCommand(command, self.testPoint)
                self.assertTrue(result.Success)
                self.mockController.Reset()
            
            elapsed_time = time.time() - start_time
            
            # 每种类型100次执行应该在0.1秒内完成
            self.assertLess(elapsed_time, 0.1)

#endregion


if __name__ == '__main__':
    unittest.main()