# -*- coding: utf-8 -*-
"""
输入处理器
处理键盘输入和指令解析
"""

from typing import Optional, Tuple, Set
from enum import Enum
from dataclasses import dataclass


#region 指令类型定义

class CommandType(Enum):
    """指令类型枚举"""
    DEFAULT_CLICK = "default"     # 默认左键单击
    RIGHT_CLICK = "right"         # 右键单击 (R后缀)
    HOVER = "hover"               # 悬停移动 (H后缀)
    INVALID = "invalid"           # 无效指令


@dataclass
class ParsedCommand:
    """解析后的指令"""
    KeySequence: str           # 按键序列 (不包含后缀)
    CommandType: CommandType   # 指令类型
    RawInput: str             # 原始输入
    IsValid: bool             # 是否有效

#endregion


#region 输入处理器核心类

class InputProcessor:
    """输入处理器
    
    负责处理九宫格按键映射和指令解析
    """
    
    def __init__(self):
        # 有效的九宫格按键
        self._validGridKeys: Set[str] = {
            'Q', 'W', 'E',    # 第一行
            'A', 'S', 'D',    # 第二行  
            'Z', 'X', 'C'     # 第三行
        }
        
        # 指令后缀映射
        self._commandSuffixes = {
            'R': CommandType.RIGHT_CLICK,
            'H': CommandType.HOVER
        }
        
        # 特殊控制键
        self._controlKeys = {'ESC', 'ESCAPE'}
    
    def IsValidGridKey(self, key: str) -> bool:
        """检查是否为有效的九宫格按键
        
        Args:
            key: 按键字符
            
        Returns:
            是否为有效按键
        """
        return key.upper() in self._validGridKeys
    
    def IsControlKey(self, key: str) -> bool:
        """检查是否为控制键
        
        Args:
            key: 按键字符
            
        Returns:
            是否为控制键
        """
        return key.upper() in self._controlKeys
    
    def IsCommandSuffix(self, key: str) -> bool:
        """检查是否为指令后缀
        
        Args:
            key: 按键字符
            
        Returns:
            是否为指令后缀
        """
        return key.upper() in self._commandSuffixes
    
    def ParseCommand(self, keySequence: str) -> ParsedCommand:
        """解析指令
        
        将输入的按键序列解析为指令对象
        
        Args:
            keySequence: 按键序列 (如 "EDCR", "ASH", "QWE")
            
        Returns:
            ParsedCommand对象
        """
        if not keySequence:
            return ParsedCommand(
                KeySequence="",
                CommandType=CommandType.INVALID,
                RawInput=keySequence,
                IsValid=False
            )
        
        rawInput = keySequence
        keySequence = keySequence.upper()
        
        # 检查最后一个字符是否为指令后缀
        commandType = CommandType.DEFAULT_CLICK
        actualKeys = keySequence
        
        if len(keySequence) > 1:
            lastChar = keySequence[-1]
            if lastChar in self._commandSuffixes:
                commandType = self._commandSuffixes[lastChar]
                actualKeys = keySequence[:-1]  # 移除后缀
        
        # 验证按键序列有效性
        isValid = self._validateKeySequence(actualKeys)
        
        if not isValid:
            commandType = CommandType.INVALID
        
        return ParsedCommand(
            KeySequence=actualKeys,
            CommandType=commandType,
            RawInput=rawInput,
            IsValid=isValid
        )
    
    def ExtractCommandSuffix(self, keys: str) -> Tuple[str, CommandType]:
        """提取指令后缀
        
        Args:
            keys: 按键字符串
            
        Returns:
            元组 (纯按键序列, 指令类型)
        """
        if not keys:
            return "", CommandType.INVALID
        
        keys = keys.upper()
        lastChar = keys[-1]
        
        if lastChar in self._commandSuffixes:
            return keys[:-1], self._commandSuffixes[lastChar]
        else:
            return keys, CommandType.DEFAULT_CLICK
    
    def ValidateCommand(self, command: ParsedCommand) -> bool:
        """验证指令有效性
        
        Args:
            command: 要验证的指令
            
        Returns:
            是否有效
        """
        return (command.IsValid and 
                command.CommandType != CommandType.INVALID and
                len(command.KeySequence) > 0)
    
    def _validateKeySequence(self, keys: str) -> bool:
        """验证按键序列
        
        Args:
            keys: 按键序列
            
        Returns:
            是否有效
        """
        if not keys:
            return False
        
        # 检查每个字符是否为有效的九宫格按键
        return all(self.IsValidGridKey(key) for key in keys)
    
    def ProcessSingleKey(self, key: str) -> Tuple[bool, bool]:
        """处理单个按键输入
        
        Args:
            key: 按键字符
            
        Returns:
            元组 (是否为有效网格键, 是否为控制键)
        """
        isGridKey = self.IsValidGridKey(key)
        isControlKey = self.IsControlKey(key)
        
        return isGridKey, isControlKey
    
    def ShouldProcessKey(self, key: str) -> bool:
        """判断是否应该处理该按键
        
        Args:
            key: 按键字符
            
        Returns:
            是否应该处理
        """
        isGridKey, isControlKey = self.ProcessSingleKey(key)
        return isGridKey or isControlKey
    
    def GetValidKeys(self) -> Set[str]:
        """获取所有有效按键
        
        Returns:
            有效按键集合
        """
        return self._validGridKeys.copy()
    
    def GetCommandSuffixes(self) -> Set[str]:
        """获取所有指令后缀
        
        Returns:
            指令后缀集合
        """
        return set(self._commandSuffixes.keys())
    
    def IsCompleteCommand(self, keySequence: str) -> bool:
        """检查是否为完整指令
        
        一个完整的指令应该至少包含一个有效的网格按键
        
        Args:
            keySequence: 按键序列
            
        Returns:
            是否为完整指令
        """
        command = self.ParseCommand(keySequence)
        return command.IsValid and len(command.KeySequence) > 0

#endregion