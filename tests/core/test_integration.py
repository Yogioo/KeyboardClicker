# -*- coding: utf-8 -*-
"""
核心模块集成测试
测试各个核心模块之间的协作
"""

import unittest
from unittest.mock import Mock, MagicMock
import time
from src.core.grid_calculator import GridCalculator
from src.core.input_processor import InputProcessor, CommandType, ParsedCommand
from src.core.command_executor import CommandExecutor, ExecutionResult
from src.core.grid_coordinate_system import GridCoordinateSystem
from src.core.grid_state import GridStateManager
from src.core.interfaces import Rectangle, Point, IMouseController


#region Mock类定义

class IntegrationTestMouseController(IMouseController):
    """集成测试鼠标控制器"""
    
    def __init__(self):
        self.actions = []  # 记录所有操作
        self.shouldFail = False
        self.failureMessage = "模拟失败"
    
    def LeftClick(self, point: Point) -> None:
        if self.shouldFail:
            raise Exception(self.failureMessage)
        self.actions.append(('left_click', point))
    
    def RightClick(self, point: Point) -> None:
        if self.shouldFail:
            raise Exception(self.failureMessage)
        self.actions.append(('right_click', point))
    
    def MoveTo(self, point: Point) -> None:
        if self.shouldFail:
            raise Exception(self.failureMessage)
        self.actions.append(('move_to', point))
    
    def GetLastAction(self):
        return self.actions[-1] if self.actions else None
    
    def GetActionCount(self):
        return len(self.actions)
    
    def Reset(self):
        self.actions.clear()
        self.shouldFail = False

#endregion


#region 基础集成测试类

class TestCoreIntegration(unittest.TestCase):
    """核心模块集成测试基类"""
    
    def setUp(self):
        """测试前准备"""
        self.calculator = GridCalculator()
        self.processor = InputProcessor()
        self.mouseController = IntegrationTestMouseController()
        self.executor = CommandExecutor(self.mouseController)
        self.testRect = Rectangle(0, 0, 300, 300)
    
    def tearDown(self):
        """测试后清理"""
        self.mouseController.Reset()

#endregion


#region 计算器与处理器集成测试

class TestCalculatorProcessorIntegration(TestCoreIntegration):
    """计算器与处理器集成测试"""
    
    def test_按键映射一致性(self):
        """测试按键映射在两个模块间的一致性"""
        validKeys = self.processor.GetValidKeys()
        
        for key in validKeys:
            # 处理器认为有效的按键，计算器也应该能转换
            index = self.calculator.KeyToIndex(key)
            self.assertIsNotNone(index)
            
            # 反向转换应该一致
            reversedKey = self.calculator.IndexToKey(index)
            self.assertEqual(reversedKey, key)
    
    def test_路径验证一致性(self):
        """测试路径验证的一致性"""
        testPaths = ["Q", "EDC", "QWEASD", "ASZ", "invalid", "QF", ""]
        
        for path in testPaths:
            # 处理器验证
            processorValid = self.processor.IsCompleteCommand(path)
            
            # 计算器验证
            calculatorValid = self.calculator.ValidateKeySequence(path)
            
            # 两者结果应该一致（对于纯按键序列）
            if not any(suffix in path.upper() for suffix in ['R', 'H']):
                self.assertEqual(processorValid, calculatorValid, 
                               f"路径 '{path}' 的验证结果不一致")
    
    def test_指令解析与计算集成(self):
        """测试指令解析与坐标计算的集成"""
        testCommands = ["Q", "EDC", "ASR", "QWH"]
        
        for commandStr in testCommands:
            # 1. 解析指令
            command = self.processor.ParseCommand(commandStr)
            
            if command.IsValid:
                # 2. 计算目标点
                targetPoint, regions = self.calculator.ProcessKeyPath(
                    command.KeySequence, self.testRect
                )
                
                # 3. 验证结果
                self.assertIsNotNone(targetPoint)
                self.assertGreater(len(regions), 0)
                
                # 验证目标点在屏幕区域内
                self.assertGreaterEqual(targetPoint.X, self.testRect.X)
                self.assertGreaterEqual(targetPoint.Y, self.testRect.Y)
                self.assertLessEqual(targetPoint.X, 
                                   self.testRect.X + self.testRect.Width)
                self.assertLessEqual(targetPoint.Y,
                                   self.testRect.Y + self.testRect.Height)

#endregion


#region 处理器与执行器集成测试

class TestProcessorExecutorIntegration(TestCoreIntegration):
    """处理器与执行器集成测试"""
    
    def test_指令类型支持一致性(self):
        """测试指令类型支持的一致性"""
        # 获取处理器支持的后缀
        suffixes = self.processor.GetCommandSuffixes()
        
        # 获取执行器支持的指令类型
        supportedCommands = self.executor.GetSupportedCommands()
        
        # 验证每种后缀都有对应的支持
        suffixToType = {'R': CommandType.RIGHT_CLICK, 'H': CommandType.HOVER}
        
        for suffix in suffixes:
            expectedType = suffixToType.get(suffix)
            self.assertIn(expectedType, supportedCommands)
    
    def test_指令执行流程(self):
        """测试完整的指令执行流程"""
        testCases = [
            ("Q", CommandType.DEFAULT_CLICK, 'left_click'),
            ("SR", CommandType.RIGHT_CLICK, 'right_click'),
            ("EH", CommandType.HOVER, 'move_to')
        ]
        
        for commandStr, expectedType, expectedAction in testCases:
            # 1. 解析指令
            command = self.processor.ParseCommand(commandStr)
            
            # 2. 验证解析结果
            self.assertTrue(command.IsValid)
            self.assertEqual(command.CommandType, expectedType)
            
            # 3. 验证执行能力
            self.assertTrue(self.executor.CanExecute(command))
            
            # 4. 执行指令
            testPoint = Point(100, 100)
            result = self.executor.ExecuteCommand(command, testPoint)
            
            # 5. 验证执行结果
            self.assertTrue(result.Success)
            
            # 6. 验证实际动作
            lastAction = self.mouseController.GetLastAction()
            self.assertIsNotNone(lastAction)
            self.assertEqual(lastAction[0], expectedAction)
            self.assertEqual(lastAction[1], testPoint)
            
            # 重置状态
            self.mouseController.Reset()

#endregion


#region 计算器与执行器集成测试

class TestCalculatorExecutorIntegration(TestCoreIntegration):
    """计算器与执行器集成测试"""
    
    def test_坐标计算与执行精度(self):
        """测试坐标计算与执行的精度"""
        # 使用精确的测试区域
        testRect = Rectangle(0, 0, 900, 900)  # 能被3整除
        
        # 测试九宫格的每个位置
        keyIndexPairs = [
            ('Q', 0), ('W', 1), ('E', 2),
            ('A', 3), ('S', 4), ('D', 5),
            ('Z', 6), ('X', 7), ('C', 8)
        ]
        
        for key, index in keyIndexPairs:
            # 1. 计算目标点
            targetPoint, regions = self.calculator.ProcessKeyPath(key, testRect)
            self.assertIsNotNone(targetPoint)
            
            # 2. 执行点击
            command = ParsedCommand(key, CommandType.DEFAULT_CLICK, key, True)
            result = self.executor.ExecuteCommand(command, targetPoint)
            self.assertTrue(result.Success)
            
            # 3. 验证点击位置
            lastAction = self.mouseController.GetLastAction()
            self.assertEqual(lastAction[1], targetPoint)
            
            # 4. 验证位置在正确的网格单元内
            cell = self.calculator.GetGridCell(testRect, index)
            self.assertIsNotNone(cell)
            
            # 点击位置应该在对应单元格内
            self.assertGreaterEqual(targetPoint.X, cell.Region.X)
            self.assertGreaterEqual(targetPoint.Y, cell.Region.Y)
            self.assertLessEqual(targetPoint.X, 
                               cell.Region.X + cell.Region.Width)
            self.assertLessEqual(targetPoint.Y,
                               cell.Region.Y + cell.Region.Height)
            
            self.mouseController.Reset()
    
    def test_递归路径计算与执行(self):
        """测试递归路径的计算与执行"""
        recursivePaths = ["ED", "QSC", "AWEZ"]
        
        for path in recursivePaths:
            # 1. 计算递归路径
            targetPoint, regions = self.calculator.ProcessKeyPath(path, self.testRect)
            self.assertIsNotNone(targetPoint)
            self.assertEqual(len(regions), len(path) + 1)  # 包括初始区域
            
            # 2. 验证区域递减
            for i in range(1, len(regions)):
                currentRegion = regions[i]
                previousRegion = regions[i-1]
                
                # 新区域应该更小
                self.assertLessEqual(currentRegion.Width, previousRegion.Width)
                self.assertLessEqual(currentRegion.Height, previousRegion.Height)
                
                # 新区域应该在前一个区域内
                self.assertGreaterEqual(currentRegion.X, previousRegion.X)
                self.assertGreaterEqual(currentRegion.Y, previousRegion.Y)
            
            # 3. 执行指令
            command = ParsedCommand(path, CommandType.DEFAULT_CLICK, path, True)
            result = self.executor.ExecuteCommand(command, targetPoint)
            self.assertTrue(result.Success)
            
            self.mouseController.Reset()

#endregion


#region 状态管理器集成测试

class TestStateManagerIntegration(TestCoreIntegration):
    """状态管理器集成测试"""
    
    def setUp(self):
        super().setUp()
        self.stateManager = GridStateManager()
    
    def test_状态与计算器集成(self):
        """测试状态管理与计算器的集成"""
        # 1. 启动会话
        self.stateManager.StartSession(self.testRect)
        self.assertTrue(self.stateManager.IsActive())
        
        # 2. 处理按键序列
        keySequence = "EDC"
        for key in keySequence:
            success = self.stateManager.ProcessKeyInput(key)
            self.assertTrue(success)
        
        # 3. 验证状态
        currentPath = self.stateManager.GetKeyPath()
        self.assertEqual(currentPath, keySequence)
        
        # 4. 使用计算器验证路径
        isValid = self.calculator.ValidateKeySequence(currentPath)
        self.assertTrue(isValid)
        
        # 5. 计算最终结果
        targetPoint, regions = self.calculator.ProcessKeyPath(
            currentPath, self.testRect
        )
        
        self.assertIsNotNone(targetPoint)
        self.assertEqual(len(regions), len(keySequence) + 1)
    
    def test_状态与处理器集成(self):
        """测试状态管理与处理器的集成"""
        self.stateManager.StartSession(self.testRect)
        
        testCommands = ["Q", "ASR", "EDH"]
        
        for commandStr in testCommands:
            # 1. 处理器解析
            command = self.processor.ParseCommand(commandStr)
            self.assertTrue(command.IsValid)
            
            # 2. 模拟状态管理器处理
            for key in command.KeySequence:
                success = self.stateManager.ProcessKeyInput(key)
                self.assertTrue(success)
            
            # 3. 验证状态路径
            statePath = self.stateManager.GetKeyPath()
            self.assertEqual(statePath, command.KeySequence)
            
            # 4. 重置状态
            self.stateManager.EndSession()
            self.stateManager.StartSession(self.testRect)

#endregion


#region 完整系统集成测试

class TestFullSystemIntegration(TestCoreIntegration):
    """完整系统集成测试"""
    
    def test_端到端工作流程_简单(self):
        """测试端到端工作流程(简单指令)"""
        # 创建完整系统
        system = GridCoordinateSystem(mouseController=self.mouseController)
        
        # 1. 启动会话
        success = system.StartSession(self.testRect)
        self.assertTrue(success)
        
        # 2. 处理按键
        success = system.ProcessKeyInput("S")
        self.assertTrue(success)
        
        # 3. 执行指令
        success = system.ExecuteCommand("S")
        self.assertTrue(success)
        
        # 4. 验证结果
        self.assertEqual(self.mouseController.GetActionCount(), 1)
        lastAction = self.mouseController.GetLastAction()
        self.assertEqual(lastAction[0], 'left_click')
        
        # 5. 验证会话已结束
        self.assertFalse(system.IsActive())
    
    def test_端到端工作流程_复杂(self):
        """测试端到端工作流程(复杂指令)"""
        system = GridCoordinateSystem(mouseController=self.mouseController)
        
        # 1. 启动会话
        system.StartSession(self.testRect)
        
        # 2. 逐步处理按键
        keySequence = "EDC"
        for key in keySequence:
            success = system.ProcessKeyInput(key)
            self.assertTrue(success)
        
        # 3. 执行右键指令
        success = system.ExecuteCommand("EDCR")
        self.assertTrue(success)
        
        # 4. 验证结果
        lastAction = self.mouseController.GetLastAction()
        self.assertEqual(lastAction[0], 'right_click')
        
        # 5. 验证点击位置的精确性
        # 重新计算期望位置
        targetPoint, _ = self.calculator.ProcessKeyPath("EDC", self.testRect)
        self.assertEqual(lastAction[1], targetPoint)
    
    def test_端到端工作流程_错误处理(self):
        """测试端到端工作流程(错误处理)"""
        system = GridCoordinateSystem(mouseController=self.mouseController)
        
        # 1. 启动会话
        system.StartSession(self.testRect)
        
        # 2. 处理无效按键（应该被忽略）
        success = system.ProcessKeyInput("F")
        self.assertFalse(success)
        
        # 3. 系统应该仍然活跃
        self.assertTrue(system.IsActive())
        
        # 4. 处理有效按键
        success = system.ProcessKeyInput("Q")
        self.assertTrue(success)
        
        # 5. 执行有效指令
        success = system.ExecuteCommand("Q")
        self.assertTrue(success)
        
        # 6. 验证正常执行
        self.assertEqual(self.mouseController.GetActionCount(), 1)
    
    def test_并发操作安全性(self):
        """测试并发操作的安全性"""
        system = GridCoordinateSystem(mouseController=self.mouseController)
        
        # 1. 启动会话
        system.StartSession(self.testRect)
        
        # 2. 快速连续操作
        operations = [
            lambda: system.ProcessKeyInput("Q"),
            lambda: system.ProcessKeyInput("W"),
            lambda: system.ProcessKeyInput("E"),
            lambda: system.ExecuteCommand("QWE")
        ]
        
        results = []
        for operation in operations:
            try:
                result = operation()
                results.append(result)
            except Exception as e:
                results.append(False)
        
        # 3. 验证至少有一些操作成功
        self.assertTrue(any(results))

#endregion


#region 性能集成测试

class TestPerformanceIntegration(TestCoreIntegration):
    """性能集成测试"""
    
    def test_端到端性能_单次操作(self):
        """测试端到端性能(单次操作)"""
        system = GridCoordinateSystem(mouseController=self.mouseController)
        
        # 预热
        system.StartSession(self.testRect)
        system.EndSession()
        
        # 测试完整流程
        start_time = time.time()
        
        # 1. 启动
        system.StartSession(self.testRect)
        
        # 2. 处理按键
        system.ProcessKeyInput("S")
        
        # 3. 执行指令
        system.ExecuteCommand("S")
        
        elapsed_time = time.time() - start_time
        
        # 整个流程应该在50ms内完成
        self.assertLess(elapsed_time, 0.05)
        
        # 验证正确执行
        self.assertEqual(self.mouseController.GetActionCount(), 1)
    
    def test_端到端性能_批量操作(self):
        """测试端到端性能(批量操作)"""
        system = GridCoordinateSystem(mouseController=self.mouseController)
        
        commands = ["Q", "W", "E", "A", "S", "D", "Z", "X", "C"] * 10  # 90个指令
        
        start_time = time.time()
        
        for command in commands:
            system.StartSession(self.testRect)
            system.ExecuteCommand(command)
        
        elapsed_time = time.time() - start_time
        
        # 90个指令应该在5秒内完成
        self.assertLess(elapsed_time, 5.0)
        
        # 验证所有指令都执行了
        self.assertEqual(self.mouseController.GetActionCount(), 90)
    
    def test_模块间通信性能(self):
        """测试模块间通信性能"""
        # 测试大量的模块间调用
        testPaths = ["Q", "ED", "ASC", "QWED"] * 25  # 100个路径
        
        start_time = time.time()
        
        for path in testPaths:
            # 1. 处理器解析
            command = self.processor.ParseCommand(path)
            
            # 2. 计算器计算
            if command.IsValid:
                targetPoint, regions = self.calculator.ProcessKeyPath(
                    command.KeySequence, self.testRect
                )
                
                # 3. 执行器执行
                if targetPoint:
                    result = self.executor.ExecuteCommand(command, targetPoint)
        
        elapsed_time = time.time() - start_time
        
        # 100次完整处理应该在1秒内完成
        self.assertLess(elapsed_time, 1.0)

#endregion


#region 边界条件集成测试

class TestEdgeCaseIntegration(TestCoreIntegration):
    """边界条件集成测试"""
    
    def test_极限坐标系统集成(self):
        """测试极限坐标的系统集成"""
        extremeRects = [
            Rectangle(0, 0, 3, 3),          # 最小区域
            Rectangle(-1000, -1000, 2000, 2000),  # 负坐标大区域
            Rectangle(0, 0, 1, 1),          # 单像素区域
        ]
        
        for rect in extremeRects:
            # 测试每个极限区域
            targetPoint, regions = self.calculator.ProcessKeyPath("S", rect)
            
            if targetPoint:  # 如果计算成功
                command = ParsedCommand("S", CommandType.DEFAULT_CLICK, "S", True)
                result = self.executor.ExecuteCommand(command, targetPoint)
                
                # 应该能够执行，即使在极限情况下
                self.assertTrue(result.Success)
                
                self.mouseController.Reset()
    
    def test_错误链式传播(self):
        """测试错误的链式传播"""
        # 设置鼠标控制器失败
        self.mouseController.shouldFail = True
        
        # 测试错误是否正确传播
        command = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        targetPoint = Point(150, 150)
        
        result = self.executor.ExecuteCommand(command, targetPoint)
        
        # 应该正确处理并报告失败
        self.assertFalse(result.Success)
        self.assertIsNotNone(result.Error)
    
    def test_资源清理集成(self):
        """测试资源清理的集成"""
        system = GridCoordinateSystem(mouseController=self.mouseController)
        
        # 启动多个会话并确保正确清理
        for i in range(10):
            success = system.StartSession(self.testRect)
            self.assertTrue(success)
            
            # 执行一些操作
            system.ProcessKeyInput("Q")
            
            # 结束会话
            system.EndSession()
            self.assertFalse(system.IsActive())
        
        # 验证没有资源泄漏的迹象
        # (这里主要是确保没有异常抛出)

#endregion


#region 兼容性测试

class TestCompatibilityIntegration(TestCoreIntegration):
    """兼容性测试"""
    
    def test_模块版本兼容性(self):
        """测试模块版本兼容性"""
        # 验证所有模块能够正常工作
        modules = [
            self.calculator,
            self.processor,
            self.executor
        ]
        
        # 每个模块都应该有基本功能
        for module in modules:
            self.assertIsNotNone(module)
    
    def test_接口一致性(self):
        """测试接口一致性"""
        # 验证关键接口的一致性
        
        # 1. Point对象兼容性
        testPoint = Point(100, 200)
        self.assertEqual(testPoint.X, 100)
        self.assertEqual(testPoint.Y, 200)
        
        # 2. Rectangle对象兼容性
        testRect = Rectangle(0, 0, 300, 300)
        center = testRect.Center
        self.assertEqual(center.X, 150)
        self.assertEqual(center.Y, 150)
        
        # 3. 指令类型兼容性
        command = ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True)
        self.assertTrue(self.executor.CanExecute(command))

#endregion


if __name__ == '__main__':
    unittest.main()