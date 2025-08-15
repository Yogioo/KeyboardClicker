# -*- coding: utf-8 -*-
"""
InputProcessor单元测试
测试输入处理器的所有功能
"""

import unittest
from src.core.input_processor import InputProcessor, CommandType, ParsedCommand


#region 基础测试类

class TestInputProcessor(unittest.TestCase):
    """InputProcessor测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.processor = InputProcessor()
    
    def tearDown(self):
        """测试后清理"""
        pass

#endregion


#region 按键验证测试

class TestKeyValidation(TestInputProcessor):
    """按键验证测试"""
    
    def test_IsValidGridKey_有效按键(self):
        """测试有效网格按键识别"""
        validKeys = ['Q', 'W', 'E', 'A', 'S', 'D', 'Z', 'X', 'C']
        
        for key in validKeys:
            # 测试大写
            self.assertTrue(self.processor.IsValidGridKey(key))
            # 测试小写
            self.assertTrue(self.processor.IsValidGridKey(key.lower()))
    
    def test_IsValidGridKey_无效按键(self):
        """测试无效网格按键识别"""
        invalidKeys = ['F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
                      'R', 'T', 'U', 'V', 'Y', '1', '2', '3', '4', '5',
                      ' ', '', '!', '@', '#']
        
        for key in invalidKeys:
            self.assertFalse(self.processor.IsValidGridKey(key))
    
    def test_IsControlKey_有效控制键(self):
        """测试有效控制键识别"""
        controlKeys = ['ESC', 'ESCAPE', 'esc', 'escape']
        
        for key in controlKeys:
            self.assertTrue(self.processor.IsControlKey(key))
    
    def test_IsControlKey_无效控制键(self):
        """测试无效控制键识别"""
        nonControlKeys = ['Q', 'ENTER', 'SPACE', 'TAB', 'SHIFT', '1']
        
        for key in nonControlKeys:
            self.assertFalse(self.processor.IsControlKey(key))
    
    def test_IsCommandSuffix_有效后缀(self):
        """测试有效指令后缀识别"""
        suffixes = ['R', 'H', 'r', 'h']
        
        for suffix in suffixes:
            self.assertTrue(self.processor.IsCommandSuffix(suffix))
    
    def test_IsCommandSuffix_无效后缀(self):
        """测试无效指令后缀识别"""
        nonSuffixes = ['Q', 'T', 'L', '1', ' ', '']
        
        for suffix in nonSuffixes:
            self.assertFalse(self.processor.IsCommandSuffix(suffix))

#endregion


#region 指令解析测试

class TestCommandParsing(TestInputProcessor):
    """指令解析测试"""
    
    def test_ParseCommand_默认左键指令(self):
        """测试默认左键指令解析"""
        testCases = ["Q", "S", "EDC", "qwe", "ASD"]
        
        for keySequence in testCases:
            command = self.processor.ParseCommand(keySequence)
            
            self.assertIsInstance(command, ParsedCommand)
            self.assertEqual(command.CommandType, CommandType.DEFAULT_CLICK)
            self.assertEqual(command.KeySequence, keySequence.upper())
            self.assertEqual(command.RawInput, keySequence)
            self.assertTrue(command.IsValid)
    
    def test_ParseCommand_右键指令(self):
        """测试右键指令解析"""
        testCases = ["QR", "SR", "EDCR", "qwer", "ASDR"]
        
        for keySequence in testCases:
            command = self.processor.ParseCommand(keySequence)
            
            self.assertEqual(command.CommandType, CommandType.RIGHT_CLICK)
            # 应该移除R后缀
            expectedKeys = keySequence[:-1].upper()
            self.assertEqual(command.KeySequence, expectedKeys)
            self.assertEqual(command.RawInput, keySequence)
            self.assertTrue(command.IsValid)
    
    def test_ParseCommand_悬停指令(self):
        """测试悬停指令解析"""
        testCases = ["QH", "SH", "EDCH", "qweh", "ASDH"]
        
        for keySequence in testCases:
            command = self.processor.ParseCommand(keySequence)
            
            self.assertEqual(command.CommandType, CommandType.HOVER)
            # 应该移除H后缀
            expectedKeys = keySequence[:-1].upper()
            self.assertEqual(command.KeySequence, expectedKeys)
            self.assertEqual(command.RawInput, keySequence)
            self.assertTrue(command.IsValid)
    
    def test_ParseCommand_单字符后缀(self):
        """测试单字符后缀指令"""
        # 单个R或H应该被识别为无效
        command_r = self.processor.ParseCommand("R")
        command_h = self.processor.ParseCommand("H")
        
        self.assertEqual(command_r.CommandType, CommandType.INVALID)
        self.assertFalse(command_r.IsValid)
        
        self.assertEqual(command_h.CommandType, CommandType.INVALID)
        self.assertFalse(command_h.IsValid)
    
    def test_ParseCommand_空输入(self):
        """测试空输入解析"""
        command = self.processor.ParseCommand("")
        
        self.assertEqual(command.CommandType, CommandType.INVALID)
        self.assertEqual(command.KeySequence, "")
        self.assertEqual(command.RawInput, "")
        self.assertFalse(command.IsValid)
    
    def test_ParseCommand_无效字符(self):
        """测试包含无效字符的指令解析"""
        invalidInputs = ["QF", "S1", "EDG", "Q R", "AS@"]
        
        for keySequence in invalidInputs:
            command = self.processor.ParseCommand(keySequence)
            
            self.assertEqual(command.CommandType, CommandType.INVALID)
            self.assertFalse(command.IsValid)
    
    def test_ParseCommand_大小写混合(self):
        """测试大小写混合输入"""
        mixedCases = ["qWeR", "aSdH", "EdC"]
        
        for keySequence in mixedCases:
            command = self.processor.ParseCommand(keySequence)
            
            if keySequence.endswith('R') or keySequence.endswith('r'):
                expectedType = CommandType.RIGHT_CLICK
                expectedKeys = keySequence[:-1].upper()
            elif keySequence.endswith('H') or keySequence.endswith('h'):
                expectedType = CommandType.HOVER
                expectedKeys = keySequence[:-1].upper()
            else:
                expectedType = CommandType.DEFAULT_CLICK
                expectedKeys = keySequence.upper()
            
            self.assertEqual(command.CommandType, expectedType)
            self.assertEqual(command.KeySequence, expectedKeys)
            self.assertTrue(command.IsValid)

#endregion


#region 后缀提取测试

class TestSuffixExtraction(TestInputProcessor):
    """后缀提取测试"""
    
    def test_ExtractCommandSuffix_无后缀(self):
        """测试无后缀的命令提取"""
        testCases = ["Q", "EDC", "QWEASD"]
        
        for keys in testCases:
            pureKeys, commandType = self.processor.ExtractCommandSuffix(keys)
            
            self.assertEqual(pureKeys, keys.upper())
            self.assertEqual(commandType, CommandType.DEFAULT_CLICK)
    
    def test_ExtractCommandSuffix_R后缀(self):
        """测试R后缀提取"""
        testCases = ["QR", "EDCR", "QWEASDR"]
        
        for keys in testCases:
            pureKeys, commandType = self.processor.ExtractCommandSuffix(keys)
            
            self.assertEqual(pureKeys, keys[:-1].upper())
            self.assertEqual(commandType, CommandType.RIGHT_CLICK)
    
    def test_ExtractCommandSuffix_H后缀(self):
        """测试H后缀提取"""
        testCases = ["QH", "EDCH", "QWEASDH"]
        
        for keys in testCases:
            pureKeys, commandType = self.processor.ExtractCommandSuffix(keys)
            
            self.assertEqual(pureKeys, keys[:-1].upper())
            self.assertEqual(commandType, CommandType.HOVER)
    
    def test_ExtractCommandSuffix_空输入(self):
        """测试空输入的后缀提取"""
        pureKeys, commandType = self.processor.ExtractCommandSuffix("")
        
        self.assertEqual(pureKeys, "")
        self.assertEqual(commandType, CommandType.INVALID)

#endregion


#region 指令验证测试

class TestCommandValidation(TestInputProcessor):
    """指令验证测试"""
    
    def test_ValidateCommand_有效指令(self):
        """测试有效指令验证"""
        validCommands = [
            ParsedCommand("Q", CommandType.DEFAULT_CLICK, "Q", True),
            ParsedCommand("EDC", CommandType.RIGHT_CLICK, "EDCR", True),
            ParsedCommand("AS", CommandType.HOVER, "ASH", True)
        ]
        
        for command in validCommands:
            self.assertTrue(self.processor.ValidateCommand(command))
    
    def test_ValidateCommand_无效指令(self):
        """测试无效指令验证"""
        invalidCommands = [
            ParsedCommand("", CommandType.DEFAULT_CLICK, "", False),
            ParsedCommand("Q", CommandType.INVALID, "QF", False),
            ParsedCommand("", CommandType.INVALID, "", False)
        ]
        
        for command in invalidCommands:
            self.assertFalse(self.processor.ValidateCommand(command))

#endregion


#region 单键处理测试

class TestSingleKeyProcessing(TestInputProcessor):
    """单键处理测试"""
    
    def test_ProcessSingleKey_网格键(self):
        """测试网格键处理"""
        gridKeys = ['Q', 'W', 'E', 'A', 'S', 'D', 'Z', 'X', 'C']
        
        for key in gridKeys:
            isGridKey, isControlKey = self.processor.ProcessSingleKey(key)
            
            self.assertTrue(isGridKey)
            self.assertFalse(isControlKey)
    
    def test_ProcessSingleKey_控制键(self):
        """测试控制键处理"""
        controlKeys = ['ESC', 'ESCAPE']
        
        for key in controlKeys:
            isGridKey, isControlKey = self.processor.ProcessSingleKey(key)
            
            self.assertFalse(isGridKey)
            self.assertTrue(isControlKey)
    
    def test_ProcessSingleKey_其他键(self):
        """测试其他键处理"""
        otherKeys = ['F', 'G', 'ENTER', '1', ' ']
        
        for key in otherKeys:
            isGridKey, isControlKey = self.processor.ProcessSingleKey(key)
            
            self.assertFalse(isGridKey)
            self.assertFalse(isControlKey)
    
    def test_ShouldProcessKey_应该处理(self):
        """测试应该处理的键"""
        shouldProcessKeys = ['Q', 'S', 'C', 'ESC', 'ESCAPE']
        
        for key in shouldProcessKeys:
            self.assertTrue(self.processor.ShouldProcessKey(key))
    
    def test_ShouldProcessKey_不应该处理(self):
        """测试不应该处理的键"""
        shouldNotProcessKeys = ['F', 'G', 'ENTER', '1', 'SPACE', ' ']
        
        for key in shouldNotProcessKeys:
            self.assertFalse(self.processor.ShouldProcessKey(key))

#endregion


#region 工具方法测试

class TestUtilityMethods(TestInputProcessor):
    """工具方法测试"""
    
    def test_GetValidKeys_返回正确集合(self):
        """测试获取有效按键集合"""
        validKeys = self.processor.GetValidKeys()
        
        expectedKeys = {'Q', 'W', 'E', 'A', 'S', 'D', 'Z', 'X', 'C'}
        self.assertEqual(validKeys, expectedKeys)
        
        # 验证返回的是拷贝，不会影响原始集合
        validKeys.add('F')
        newValidKeys = self.processor.GetValidKeys()
        self.assertNotIn('F', newValidKeys)
    
    def test_GetCommandSuffixes_返回正确集合(self):
        """测试获取指令后缀集合"""
        suffixes = self.processor.GetCommandSuffixes()
        
        expectedSuffixes = {'R', 'H'}
        self.assertEqual(suffixes, expectedSuffixes)
    
    def test_IsCompleteCommand_完整指令(self):
        """测试完整指令检查"""
        completeCommands = ["Q", "EDC", "ASR", "QWH"]
        
        for command in completeCommands:
            self.assertTrue(self.processor.IsCompleteCommand(command))
    
    def test_IsCompleteCommand_不完整指令(self):
        """测试不完整指令检查"""
        incompleteCommands = ["", "F", "QF", "123", "R", "H"]
        
        for command in incompleteCommands:
            self.assertFalse(self.processor.IsCompleteCommand(command))

#endregion


#region 边界条件测试

class TestEdgeCases(TestInputProcessor):
    """边界条件测试"""
    
    def test_很长的按键序列(self):
        """测试很长的按键序列"""
        longSequence = "QWEASDZXC" * 10  # 90个字符
        command = self.processor.ParseCommand(longSequence)
        
        self.assertTrue(command.IsValid)
        self.assertEqual(command.CommandType, CommandType.DEFAULT_CLICK)
        self.assertEqual(len(command.KeySequence), 90)
    
    def test_很长的按键序列_带后缀(self):
        """测试很长的按键序列带后缀"""
        longSequence = "QWEASDZXC" * 10 + "R"  # 90个字符 + R
        command = self.processor.ParseCommand(longSequence)
        
        self.assertTrue(command.IsValid)
        self.assertEqual(command.CommandType, CommandType.RIGHT_CLICK)
        self.assertEqual(len(command.KeySequence), 90)
    
    def test_特殊字符处理(self):
        """测试特殊字符处理"""
        specialInputs = [None, "\t", "\n", "\r", "  "]
        
        for specialInput in specialInputs:
            if specialInput is None:
                continue  # None会导致异常，这是预期行为
                
            command = self.processor.ParseCommand(specialInput)
            self.assertFalse(command.IsValid)
    
    def test_Unicode字符处理(self):
        """测试Unicode字符处理"""
        unicodeInputs = ["Ω", "中", "🎮", "αβγ"]
        
        for unicodeInput in unicodeInputs:
            command = self.processor.ParseCommand(unicodeInput)
            self.assertFalse(command.IsValid)

#endregion


#region 性能测试

class TestPerformance(TestInputProcessor):
    """性能测试"""
    
    def test_大量解析性能(self):
        """测试大量指令解析性能"""
        import time
        
        testCommands = ["Q", "EDC", "ASR", "QWEH"] * 250  # 1000个指令
        
        start_time = time.time()
        
        for command in testCommands:
            self.processor.ParseCommand(command)
        
        elapsed_time = time.time() - start_time
        
        # 1000次解析应该在0.1秒内完成
        self.assertLess(elapsed_time, 0.1)
    
    def test_长序列解析性能(self):
        """测试长序列解析性能"""
        import time
        
        longSequence = "QWEASDZXC" * 100  # 900个字符
        
        start_time = time.time()
        
        # 解析100次长序列
        for _ in range(100):
            self.processor.ParseCommand(longSequence)
        
        elapsed_time = time.time() - start_time
        
        # 应该在合理时间内完成
        self.assertLess(elapsed_time, 0.1)

#endregion


#region 状态一致性测试

class TestStateConsistency(TestInputProcessor):
    """状态一致性测试"""
    
    def test_连续解析一致性(self):
        """测试连续解析的一致性"""
        testCommand = "EDCR"
        
        # 多次解析同一指令
        results = []
        for _ in range(10):
            command = self.processor.ParseCommand(testCommand)
            results.append((command.KeySequence, command.CommandType, command.IsValid))
        
        # 所有结果应该一致
        firstResult = results[0]
        for result in results[1:]:
            self.assertEqual(result, firstResult)
    
    def test_处理器状态不变性(self):
        """测试处理器状态不会被处理过程改变"""
        # 记录初始状态
        initialValidKeys = self.processor.GetValidKeys()
        initialSuffixes = self.processor.GetCommandSuffixes()
        
        # 处理各种指令
        testCommands = ["Q", "INVALID", "EDCR", "", "QWEASDZXCH", "123"]
        for command in testCommands:
            self.processor.ParseCommand(command)
        
        # 验证状态未改变
        finalValidKeys = self.processor.GetValidKeys()
        finalSuffixes = self.processor.GetCommandSuffixes()
        
        self.assertEqual(initialValidKeys, finalValidKeys)
        self.assertEqual(initialSuffixes, finalSuffixes)

#endregion


if __name__ == '__main__':
    unittest.main()