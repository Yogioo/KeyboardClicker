# -*- coding: utf-8 -*-
"""
GridCoordinateSystem单元测试
测试网格坐标系统主控制器的所有功能
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import time
from src.core.grid_coordinate_system import GridCoordinateSystem, GridEventCallbacks
from src.core.interfaces import (
    Rectangle, Point, IGridRenderer, IMouseController, 
    IInputListener, ISystemHook, GridCell
)
from src.core.input_processor import CommandType, ParsedCommand
from src.core.command_executor import ExecutionResult


#region Mock类定义

class MockGridRenderer(IGridRenderer):
    """Mock网格渲染器"""
    
    def __init__(self):
        self.showGridCalled = False
        self.hideGridCalled = False
        self.updateActiveRegionCalled = False
        self.lastCells = None
        self.lastActiveRegion = None
    
    def ShowGrid(self, cells, activeRegion: Rectangle) -> None:
        self.showGridCalled = True
        self.lastCells = cells
        self.lastActiveRegion = activeRegion
    
    def HideGrid(self) -> None:
        self.hideGridCalled = True
    
    def UpdateActiveRegion(self, region: Rectangle) -> None:
        self.updateActiveRegionCalled = True
        self.lastActiveRegion = region
    
    def Reset(self):
        self.showGridCalled = False
        self.hideGridCalled = False
        self.updateActiveRegionCalled = False
        self.lastCells = None
        self.lastActiveRegion = None


class MockMouseController(IMouseController):
    """Mock鼠标控制器"""
    
    def __init__(self):
        self.leftClickCalled = False
        self.rightClickCalled = False
        self.moveTooCalled = False
        self.lastPoint = None
    
    def LeftClick(self, point: Point) -> None:
        self.leftClickCalled = True
        self.lastPoint = point
    
    def RightClick(self, point: Point) -> None:
        self.rightClickCalled = True
        self.lastPoint = point
    
    def MoveTo(self, point: Point) -> None:
        self.moveTooCalled = True
        self.lastPoint = point
    
    def Reset(self):
        self.leftClickCalled = False
        self.rightClickCalled = False
        self.moveTooCalled = False
        self.lastPoint = None


class MockInputListener(IInputListener):
    """Mock输入监听器"""
    
    def __init__(self):
        self.startListeningCalled = False
        self.stopListeningCalled = False
        self.keyHandler = None
    
    def StartListening(self) -> None:
        self.startListeningCalled = True
    
    def StopListening(self) -> None:
        self.stopListeningCalled = True
    
    def RegisterKeyHandler(self, handler) -> None:
        self.keyHandler = handler
    
    def SimulateKeyInput(self, key: str):
        """模拟按键输入"""
        if self.keyHandler:
            self.keyHandler(key)
    
    def Reset(self):
        self.startListeningCalled = False
        self.stopListeningCalled = False


class MockSystemHook(ISystemHook):
    """Mock系统钩子"""
    
    def __init__(self):
        self.registeredHotkeys = {}
        self.unregisteredHotkeys = set()
    
    def RegisterHotkey(self, key: str, callback) -> None:
        self.registeredHotkeys[key] = callback
    
    def UnregisterHotkey(self, key: str) -> None:
        self.unregisteredHotkeys.add(key)
        if key in self.registeredHotkeys:
            del self.registeredHotkeys[key]
    
    def SimulateHotkey(self, key: str):
        """模拟热键触发"""
        if key in self.registeredHotkeys:
            self.registeredHotkeys[key]()
    
    def Reset(self):
        self.registeredHotkeys.clear()
        self.unregisteredHotkeys.clear()

#endregion


#region 基础测试类

class TestGridCoordinateSystem(unittest.TestCase):
    """GridCoordinateSystem测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.mockRenderer = MockGridRenderer()
        self.mockMouseController = MockMouseController()
        self.mockInputListener = MockInputListener()
        self.mockSystemHook = MockSystemHook()
        
        self.system = GridCoordinateSystem(
            renderer=self.mockRenderer,
            mouseController=self.mockMouseController,
            inputListener=self.mockInputListener,
            systemHook=self.mockSystemHook
        )
        
        self.testScreenRect = Rectangle(0, 0, 300, 300)
    
    def tearDown(self):
        """测试后清理"""
        self.system.EndSession()

#endregion


#region 初始化测试

class TestInitialization(TestGridCoordinateSystem):
    """初始化测试"""
    
    def test_构造函数_带所有参数(self):
        """测试带所有参数的构造函数"""
        system = GridCoordinateSystem(
            renderer=self.mockRenderer,
            mouseController=self.mockMouseController,
            inputListener=self.mockInputListener,
            systemHook=self.mockSystemHook
        )
        
        self.assertIsNotNone(system)
        self.assertFalse(system.IsActive())
        self.assertFalse(system.IsProcessing())
    
    def test_构造函数_无参数(self):
        """测试无参数的构造函数"""
        system = GridCoordinateSystem()
        
        self.assertIsNotNone(system)
        self.assertFalse(system.IsActive())
        self.assertFalse(system.IsProcessing())
    
    def test_构造函数_部分参数(self):
        """测试部分参数的构造函数"""
        system = GridCoordinateSystem(
            mouseController=self.mockMouseController
        )
        
        self.assertIsNotNone(system)
    
    def test_热键注册(self):
        """测试热键注册"""
        # 验证alt+g热键已注册
        self.assertIn("alt+g", self.mockSystemHook.registeredHotkeys)
    
    def test_输入监听器注册(self):
        """测试输入监听器注册"""
        # 验证按键处理器已注册
        self.assertIsNotNone(self.mockInputListener.keyHandler)

#endregion


#region 组件设置测试

class TestComponentSetup(TestGridCoordinateSystem):
    """组件设置测试"""
    
    def test_SetRenderer_设置渲染器(self):
        """测试设置渲染器"""
        newRenderer = MockGridRenderer()
        self.system.SetRenderer(newRenderer)
        
        # 启动会话验证新渲染器被使用
        self.system.StartSession(self.testScreenRect)
        self.assertTrue(newRenderer.showGridCalled)
    
    def test_SetMouseController_设置鼠标控制器(self):
        """测试设置鼠标控制器"""
        newController = MockMouseController()
        self.system.SetMouseController(newController)
        
        # 执行指令验证新控制器被使用
        self.system.StartSession(self.testScreenRect)
        success = self.system.ExecuteCommand("Q")
        
        self.assertTrue(success)
        self.assertTrue(newController.leftClickCalled)
    
    def test_SetCallbacks_设置回调(self):
        """测试设置事件回调"""
        callbacks = GridEventCallbacks()
        sessionStartedCalled = False
        sessionEndedCalled = False
        
        def onSessionStarted(rect):
            nonlocal sessionStartedCalled
            sessionStartedCalled = True
        
        def onSessionEnded():
            nonlocal sessionEndedCalled
            sessionEndedCalled = True
        
        callbacks.OnSessionStarted = onSessionStarted
        callbacks.OnSessionEnded = onSessionEnded
        
        self.system.SetCallbacks(callbacks)
        
        # 测试回调触发
        self.system.StartSession(self.testScreenRect)
        self.assertTrue(sessionStartedCalled)
        
        self.system.EndSession()
        self.assertTrue(sessionEndedCalled)

#endregion


#region 会话管理测试

class TestSessionManagement(TestGridCoordinateSystem):
    """会话管理测试"""
    
    def test_StartSession_成功启动(self):
        """测试成功启动会话"""
        success = self.system.StartSession(self.testScreenRect)
        
        self.assertTrue(success)
        self.assertTrue(self.system.IsActive())
        self.assertFalse(self.system.IsProcessing())
        
        # 验证渲染器被调用
        self.assertTrue(self.mockRenderer.showGridCalled)
        self.assertEqual(self.mockRenderer.lastActiveRegion, self.testScreenRect)
        
        # 验证输入监听开始
        self.assertTrue(self.mockInputListener.startListeningCalled)
    
    def test_StartSession_默认屏幕区域(self):
        """测试使用默认屏幕区域启动会话"""
        success = self.system.StartSession()
        
        self.assertTrue(success)
        self.assertTrue(self.system.IsActive())
        
        # 应该使用默认的1080p区域
        expectedRect = Rectangle(0, 0, 1920, 1080)
        self.assertEqual(self.mockRenderer.lastActiveRegion.Width, expectedRect.Width)
        self.assertEqual(self.mockRenderer.lastActiveRegion.Height, expectedRect.Height)
    
    def test_StartSession_覆盖现有会话(self):
        """测试覆盖现有会话"""
        # 启动第一个会话
        self.system.StartSession(self.testScreenRect)
        self.assertTrue(self.system.IsActive())
        
        # 启动第二个会话
        newRect = Rectangle(100, 100, 400, 400)
        success = self.system.StartSession(newRect)
        
        self.assertTrue(success)
        self.assertTrue(self.system.IsActive())
        self.assertEqual(self.mockRenderer.lastActiveRegion, newRect)
    
    def test_EndSession_正常结束(self):
        """测试正常结束会话"""
        # 启动会话
        self.system.StartSession(self.testScreenRect)
        self.assertTrue(self.system.IsActive())
        
        # 结束会话
        self.system.EndSession()
        
        self.assertFalse(self.system.IsActive())
        self.assertFalse(self.system.IsProcessing())
        
        # 验证资源清理
        self.assertTrue(self.mockRenderer.hideGridCalled)
        self.assertTrue(self.mockInputListener.stopListeningCalled)
    
    def test_EndSession_重复结束(self):
        """测试重复结束会话"""
        # 启动并结束会话
        self.system.StartSession(self.testScreenRect)
        self.system.EndSession()
        
        # 重复结束（不应该出错）
        self.system.EndSession()
        
        self.assertFalse(self.system.IsActive())

#endregion


#region 按键处理测试

class TestKeyProcessing(TestGridCoordinateSystem):
    """按键处理测试"""
    
    def test_ProcessKeyInput_有效网格键(self):
        """测试处理有效网格键"""
        self.system.StartSession(self.testScreenRect)
        
        success = self.system.ProcessKeyInput("Q")
        
        self.assertTrue(success)
        
        # 验证渲染器更新
        self.assertTrue(self.mockRenderer.showGridCalled)
        
        # 验证状态更新
        state = self.system.GetCurrentState()
        self.assertEqual(state['KeyPath'], "Q")
        self.assertEqual(state['CurrentLevel'], 1)
    
    def test_ProcessKeyInput_多个按键(self):
        """测试处理多个按键"""
        self.system.StartSession(self.testScreenRect)
        
        # 连续处理多个按键
        keys = ["E", "D", "C"]
        for key in keys:
            success = self.system.ProcessKeyInput(key)
            self.assertTrue(success)
        
        # 验证路径
        state = self.system.GetCurrentState()
        self.assertEqual(state['KeyPath'], "EDC")
        self.assertEqual(state['CurrentLevel'], 3)
    
    def test_ProcessKeyInput_控制键ESC(self):
        """测试处理ESC控制键"""
        self.system.StartSession(self.testScreenRect)
        self.assertTrue(self.system.IsActive())
        
        success = self.system.ProcessKeyInput("ESC")
        
        self.assertTrue(success)
        self.assertFalse(self.system.IsActive())  # 会话应该结束
    
    def test_ProcessKeyInput_无效按键(self):
        """测试处理无效按键"""
        self.system.StartSession(self.testScreenRect)
        
        success = self.system.ProcessKeyInput("F")
        
        self.assertFalse(success)
        
        # 状态不应该改变
        state = self.system.GetCurrentState()
        self.assertEqual(state['KeyPath'], "")
        self.assertEqual(state['CurrentLevel'], 0)
    
    def test_ProcessKeyInput_未激活状态(self):
        """测试未激活状态下处理按键"""
        # 不启动会话
        success = self.system.ProcessKeyInput("Q")
        
        self.assertFalse(success)
    
    def test_ProcessKeyInput_性能测试(self):
        """测试按键处理性能"""
        self.system.StartSession(self.testScreenRect)
        
        start_time = time.time()
        
        # 处理按键
        self.system.ProcessKeyInput("Q")
        
        elapsed_time = time.time() - start_time
        
        # 应该在50ms内完成
        self.assertLess(elapsed_time, 0.05)

#endregion


#region 指令执行测试

class TestCommandExecution(TestGridCoordinateSystem):
    """指令执行测试"""
    
    def test_ExecuteCommand_默认点击(self):
        """测试执行默认点击指令"""
        self.system.StartSession(self.testScreenRect)
        
        success = self.system.ExecuteCommand("Q")
        
        self.assertTrue(success)
        self.assertTrue(self.mockMouseController.leftClickCalled)
        self.assertFalse(self.system.IsActive())  # 执行后会话应该结束
    
    def test_ExecuteCommand_右键点击(self):
        """测试执行右键点击指令"""
        self.system.StartSession(self.testScreenRect)
        
        success = self.system.ExecuteCommand("QR")
        
        self.assertTrue(success)
        self.assertTrue(self.mockMouseController.rightClickCalled)
        self.assertFalse(self.system.IsActive())
    
    def test_ExecuteCommand_悬停操作(self):
        """测试执行悬停操作"""
        self.system.StartSession(self.testScreenRect)
        
        success = self.system.ExecuteCommand("QH")
        
        self.assertTrue(success)
        self.assertTrue(self.mockMouseController.moveTooCalled)
        self.assertFalse(self.system.IsActive())
    
    def test_ExecuteCommand_复杂路径(self):
        """测试执行复杂路径指令"""
        self.system.StartSession(self.testScreenRect)
        
        success = self.system.ExecuteCommand("EDCR")
        
        self.assertTrue(success)
        self.assertTrue(self.mockMouseController.rightClickCalled)
        
        # 验证最终点击位置是正确计算的
        self.assertIsNotNone(self.mockMouseController.lastPoint)
    
    def test_ExecuteCommand_无效指令(self):
        """测试执行无效指令"""
        self.system.StartSession(self.testScreenRect)
        
        success = self.system.ExecuteCommand("QF")
        
        self.assertFalse(success)
        self.assertFalse(self.mockMouseController.leftClickCalled)
        self.assertTrue(self.system.IsActive())  # 会话应该保持激活
    
    def test_ExecuteCommand_空指令(self):
        """测试执行空指令"""
        self.system.StartSession(self.testScreenRect)
        
        success = self.system.ExecuteCommand("")
        
        self.assertFalse(success)
        self.assertTrue(self.system.IsActive())
    
    def test_ExecuteCommand_未激活状态(self):
        """测试未激活状态下执行指令"""
        success = self.system.ExecuteCommand("Q")
        
        self.assertFalse(success)

#endregion


#region 热键测试

class TestHotkey(TestGridCoordinateSystem):
    """热键测试"""
    
    def test_激活热键_启动会话(self):
        """测试激活热键启动会话"""
        self.assertFalse(self.system.IsActive())
        
        # 模拟alt+g热键
        self.mockSystemHook.SimulateHotkey("alt+g")
        
        self.assertTrue(self.system.IsActive())
        self.assertTrue(self.mockRenderer.showGridCalled)
    
    def test_激活热键_结束会话(self):
        """测试激活热键结束会话"""
        # 启动会话
        self.system.StartSession(self.testScreenRect)
        self.assertTrue(self.system.IsActive())
        
        # 再次按alt+g应该结束会话
        self.mockSystemHook.SimulateHotkey("alt+g")
        
        self.assertFalse(self.system.IsActive())
        self.assertTrue(self.mockRenderer.hideGridCalled)
    
    def test_激活热键_切换状态(self):
        """测试激活热键切换状态"""
        # 初始状态：未激活
        self.assertFalse(self.system.IsActive())
        
        # 第一次按：激活
        self.mockSystemHook.SimulateHotkey("alt+g")
        self.assertTrue(self.system.IsActive())
        
        # 第二次按：取消激活
        self.mockSystemHook.SimulateHotkey("alt+g")
        self.assertFalse(self.system.IsActive())
        
        # 第三次按：重新激活
        self.mockSystemHook.SimulateHotkey("alt+g")
        self.assertTrue(self.system.IsActive())

#endregion


#region 输入监听测试

class TestInputListening(TestGridCoordinateSystem):
    """输入监听测试"""
    
    def test_输入监听_网格键(self):
        """测试输入监听处理网格键"""
        self.system.StartSession(self.testScreenRect)
        
        # 模拟按键输入
        self.mockInputListener.SimulateKeyInput("Q")
        
        # 验证按键被处理
        state = self.system.GetCurrentState()
        self.assertEqual(state['KeyPath'], "Q")
    
    def test_输入监听_控制键(self):
        """测试输入监听处理控制键"""
        self.system.StartSession(self.testScreenRect)
        self.assertTrue(self.system.IsActive())
        
        # 模拟ESC按键
        self.mockInputListener.SimulateKeyInput("ESC")
        
        # 会话应该结束
        self.assertFalse(self.system.IsActive())
    
    def test_输入监听_无效键(self):
        """测试输入监听处理无效键"""
        self.system.StartSession(self.testScreenRect)
        
        # 模拟无效按键
        self.mockInputListener.SimulateKeyInput("F")
        
        # 状态不应该改变
        state = self.system.GetCurrentState()
        self.assertEqual(state['KeyPath'], "")
    
    def test_输入监听_未激活状态(self):
        """测试未激活状态下的输入监听"""
        # 不启动会话
        
        # 模拟按键输入
        self.mockInputListener.SimulateKeyInput("Q")
        
        # 应该没有任何反应
        self.assertFalse(self.system.IsActive())

#endregion


#region 状态查询测试

class TestStateQuery(TestGridCoordinateSystem):
    """状态查询测试"""
    
    def test_GetCurrentState_初始状态(self):
        """测试获取初始状态"""
        state = self.system.GetCurrentState()
        
        self.assertFalse(state['IsActive'])
        self.assertFalse(state['IsProcessing'])
        self.assertEqual(state['CurrentLevel'], 0)
        self.assertEqual(state['KeyPath'], "")
        self.assertIsNone(state['ActiveRegion'])
        self.assertIsNone(state['TargetPoint'])
    
    def test_GetCurrentState_激活状态(self):
        """测试获取激活状态"""
        self.system.StartSession(self.testScreenRect)
        
        state = self.system.GetCurrentState()
        
        self.assertTrue(state['IsActive'])
        self.assertFalse(state['IsProcessing'])
        self.assertEqual(state['CurrentLevel'], 0)
        self.assertEqual(state['KeyPath'], "")
        self.assertIsNotNone(state['ActiveRegion'])
        self.assertIsNone(state['TargetPoint'])
    
    def test_GetCurrentState_处理按键后(self):
        """测试处理按键后的状态"""
        self.system.StartSession(self.testScreenRect)
        self.system.ProcessKeyInput("Q")
        
        state = self.system.GetCurrentState()
        
        self.assertTrue(state['IsActive'])
        self.assertFalse(state['IsProcessing'])
        self.assertEqual(state['CurrentLevel'], 1)
        self.assertEqual(state['KeyPath'], "Q")
        self.assertIsNotNone(state['ActiveRegion'])
        self.assertIsNotNone(state['TargetPoint'])
    
    def test_IsActive_状态检查(self):
        """测试IsActive状态检查"""
        self.assertFalse(self.system.IsActive())
        
        self.system.StartSession(self.testScreenRect)
        self.assertTrue(self.system.IsActive())
        
        self.system.EndSession()
        self.assertFalse(self.system.IsActive())
    
    def test_IsProcessing_状态检查(self):
        """测试IsProcessing状态检查"""
        self.assertFalse(self.system.IsProcessing())
        
        # 正常情况下处理状态很短暂，难以直接测试
        # 这里主要验证接口可用性

#endregion


#region 回调事件测试

class TestCallbackEvents(TestGridCoordinateSystem):
    """回调事件测试"""
    
    def test_会话开始回调(self):
        """测试会话开始回调"""
        callbacks = GridEventCallbacks()
        callbackCalled = False
        receivedRect = None
        
        def onSessionStarted(rect):
            nonlocal callbackCalled, receivedRect
            callbackCalled = True
            receivedRect = rect
        
        callbacks.OnSessionStarted = onSessionStarted
        self.system.SetCallbacks(callbacks)
        
        self.system.StartSession(self.testScreenRect)
        
        self.assertTrue(callbackCalled)
        self.assertEqual(receivedRect, self.testScreenRect)
    
    def test_会话结束回调(self):
        """测试会话结束回调"""
        callbacks = GridEventCallbacks()
        callbackCalled = False
        
        def onSessionEnded():
            nonlocal callbackCalled
            callbackCalled = True
        
        callbacks.OnSessionEnded = onSessionEnded
        self.system.SetCallbacks(callbacks)
        
        self.system.StartSession(self.testScreenRect)
        self.system.EndSession()
        
        self.assertTrue(callbackCalled)
    
    def test_按键处理回调(self):
        """测试按键处理回调"""
        callbacks = GridEventCallbacks()
        callbackCalled = False
        receivedKey = None
        receivedRegion = None
        
        def onKeyProcessed(key, region):
            nonlocal callbackCalled, receivedKey, receivedRegion
            callbackCalled = True
            receivedKey = key
            receivedRegion = region
        
        callbacks.OnKeyProcessed = onKeyProcessed
        self.system.SetCallbacks(callbacks)
        
        self.system.StartSession(self.testScreenRect)
        self.system.ProcessKeyInput("Q")
        
        self.assertTrue(callbackCalled)
        self.assertEqual(receivedKey, "Q")
        self.assertIsNotNone(receivedRegion)
    
    def test_指令执行回调(self):
        """测试指令执行回调"""
        callbacks = GridEventCallbacks()
        callbackCalled = False
        receivedResult = None
        
        def onCommandExecuted(result):
            nonlocal callbackCalled, receivedResult
            callbackCalled = True
            receivedResult = result
        
        callbacks.OnCommandExecuted = onCommandExecuted
        self.system.SetCallbacks(callbacks)
        
        self.system.StartSession(self.testScreenRect)
        self.system.ExecuteCommand("Q")
        
        self.assertTrue(callbackCalled)
        self.assertIsNotNone(receivedResult)
        self.assertTrue(receivedResult.Success)

#endregion


#region 错误处理测试

class TestErrorHandling(TestGridCoordinateSystem):
    """错误处理测试"""
    
    def test_错误回调(self):
        """测试错误回调"""
        callbacks = GridEventCallbacks()
        errorCalled = False
        errorMessage = None
        errorException = None
        
        def onError(message, exception):
            nonlocal errorCalled, errorMessage, errorException
            errorCalled = True
            errorMessage = message
            errorException = exception
        
        callbacks.OnError = onError
        self.system.SetCallbacks(callbacks)
        
        # 触发错误（使用损坏的依赖）
        system = GridCoordinateSystem()
        system.SetCallbacks(callbacks)
        
        # 尝试执行需要依赖的操作
        success = system.ExecuteCommand("Q")
        self.assertFalse(success)
    
    def test_启动会话异常处理(self):
        """测试启动会话异常处理"""
        # 使用会抛出异常的渲染器
        class FailingRenderer(IGridRenderer):
            def ShowGrid(self, cells, activeRegion):
                raise Exception("渲染失败")
            def HideGrid(self):
                pass
            def UpdateActiveRegion(self, region):
                pass
        
        system = GridCoordinateSystem(renderer=FailingRenderer())
        
        # 启动应该失败但不应该崩溃
        success = system.StartSession(self.testScreenRect)
        self.assertFalse(success)
    
    def test_无依赖组件时的行为(self):
        """测试无依赖组件时的行为"""
        system = GridCoordinateSystem()
        
        # 应该能启动但功能受限
        success = system.StartSession(self.testScreenRect)
        self.assertTrue(success)
        
        # 应该能处理按键
        success = system.ProcessKeyInput("Q")
        self.assertTrue(success)
        
        # 执行指令应该失败（无鼠标控制器）
        success = system.ExecuteCommand("Q")
        self.assertFalse(success)

#endregion


#region 集成测试

class TestIntegration(TestGridCoordinateSystem):
    """集成测试"""
    
    def test_完整工作流程_简单点击(self):
        """测试完整工作流程(简单点击)"""
        # 1. 启动会话
        success = self.system.StartSession(self.testScreenRect)
        self.assertTrue(success)
        self.assertTrue(self.system.IsActive())
        
        # 2. 处理按键
        success = self.system.ProcessKeyInput("S")
        self.assertTrue(success)
        
        # 3. 执行指令
        success = self.system.ExecuteCommand("S")
        self.assertTrue(success)
        self.assertTrue(self.mockMouseController.leftClickCalled)
        self.assertFalse(self.system.IsActive())
    
    def test_完整工作流程_复杂路径(self):
        """测试完整工作流程(复杂路径)"""
        # 1. 启动会话
        self.system.StartSession(self.testScreenRect)
        
        # 2. 逐步处理按键
        keys = ["E", "D", "C"]
        for key in keys:
            success = self.system.ProcessKeyInput(key)
            self.assertTrue(success)
        
        # 3. 执行右键指令
        success = self.system.ExecuteCommand("EDCR")
        self.assertTrue(success)
        self.assertTrue(self.mockMouseController.rightClickCalled)
    
    def test_完整工作流程_热键激活(self):
        """测试完整工作流程(热键激活)"""
        # 1. 热键激活
        self.mockSystemHook.SimulateHotkey("alt+g")
        self.assertTrue(self.system.IsActive())
        
        # 2. 输入监听处理
        self.mockInputListener.SimulateKeyInput("Q")
        
        # 3. ESC退出
        self.mockInputListener.SimulateKeyInput("ESC")
        self.assertFalse(self.system.IsActive())
    
    def test_完整工作流程_错误恢复(self):
        """测试完整工作流程(错误恢复)"""
        # 1. 启动会话
        self.system.StartSession(self.testScreenRect)
        
        # 2. 处理无效按键（应该被忽略）
        success = self.system.ProcessKeyInput("F")
        self.assertFalse(success)
        self.assertTrue(self.system.IsActive())  # 仍然激活
        
        # 3. 处理有效按键
        success = self.system.ProcessKeyInput("Q")
        self.assertTrue(success)
        
        # 4. 执行指令
        success = self.system.ExecuteCommand("Q")
        self.assertTrue(success)

#endregion


#region 性能测试

class TestPerformance(TestGridCoordinateSystem):
    """性能测试"""
    
    def test_启动会话性能(self):
        """测试启动会话性能"""
        start_time = time.time()
        
        success = self.system.StartSession(self.testScreenRect)
        
        elapsed_time = time.time() - start_time
        
        self.assertTrue(success)
        self.assertLess(elapsed_time, 0.1)  # 应该在100ms内完成
    
    def test_按键处理性能(self):
        """测试按键处理性能"""
        self.system.StartSession(self.testScreenRect)
        
        start_time = time.time()
        
        # 处理100个按键
        for i in range(100):
            key = ["Q", "W", "E", "A", "S", "D", "Z", "X", "C"][i % 9]
            self.system.ProcessKeyInput(key)
        
        elapsed_time = time.time() - start_time
        
        self.assertLess(elapsed_time, 0.5)  # 100个按键应该在500ms内完成
    
    def test_指令执行性能(self):
        """测试指令执行性能"""
        self.system.StartSession(self.testScreenRect)
        
        start_time = time.time()
        
        success = self.system.ExecuteCommand("EDC")
        
        elapsed_time = time.time() - start_time
        
        self.assertTrue(success)
        self.assertLess(elapsed_time, 0.05)  # 应该在50ms内完成

#endregion


if __name__ == '__main__':
    unittest.main()