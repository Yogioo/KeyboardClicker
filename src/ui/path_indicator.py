#region PathIndicator Implementation
"""
路径指示器实现
显示当前按键路径和系统状态
"""

from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics
from PyQt6.QtCore import QRect, Qt
from typing import List, Optional


class PathIndicator:
    """
    路径指示器
    
    功能：
    - 显示当前按键路径 (Q → W → E)
    - 系统状态指示
    - 递归层级显示
    - 错误状态提示
    """
    
    #region Constants
    _MAX_PATH_LENGTH = 10  # 最大显示路径长度
    _SEPARATOR = " → "  # 路径分隔符
    #endregion
    
    def __init__(self):
        """
        初始化路径指示器
        """
        self._keyPath: List[str] = []
        self._currentLevel = 0
        self._isActive = False
        self._hasError = False
        self._errorMessage = ""
        
        # 样式配置
        self._backgroundColor = QColor(0, 0, 0, 180)  # 半透明黑色背景
        self._textColor = QColor("#FFFFFF")  # 白色文字
        self._errorColor = QColor("#FF0000")  # 红色错误文字
        self._borderColor = QColor("#555555")  # 灰色边框
        self._fontSize = 18  # 字体大小
        self._padding = 15  # 内边距
        self._borderRadius = 8  # 圆角半径
    
    #region Public Methods
    def UpdatePath(self, keySequence: List[str]) -> None:
        """
        更新按键路径
        
        Args:
            keySequence: 按键序列列表
        """
        # 限制路径长度
        if len(keySequence) > self._MAX_PATH_LENGTH:
            self._keyPath = keySequence[-self._MAX_PATH_LENGTH:]
        else:
            self._keyPath = keySequence.copy()
        
        self._currentLevel = len(self._keyPath)
        self._ClearError()
    
    def AddKey(self, key: str) -> None:
        """
        添加单个按键到路径
        
        Args:
            key: 按键字符
        """
        if len(self._keyPath) < self._MAX_PATH_LENGTH:
            self._keyPath.append(key.upper())
            self._currentLevel = len(self._keyPath)
            self._ClearError()
    
    def RemoveLastKey(self) -> bool:
        """
        移除最后一个按键
        
        Returns:
            bool: 是否成功移除
        """
        if self._keyPath:
            self._keyPath.pop()
            self._currentLevel = len(self._keyPath)
            self._ClearError()
            return True
        return False
    
    def ClearPath(self) -> None:
        """
        清空路径
        """
        self._keyPath.clear()
        self._currentLevel = 0
        self._ClearError()
    
    def SetActive(self, isActive: bool) -> None:
        """
        设置激活状态
        
        Args:
            isActive: 是否激活
        """
        self._isActive = isActive
        if not isActive:
            self.ClearPath()
    
    def ShowError(self, message: str) -> None:
        """
        显示错误消息
        
        Args:
            message: 错误消息
        """
        self._hasError = True
        self._errorMessage = message
    
    def ClearError(self) -> None:
        """
        清除错误状态
        """
        self._ClearError()
    
    def Render(self, painter: QPainter, screenRect: QRect) -> None:
        """
        渲染路径指示器
        
        Args:
            painter: QPainter绘制对象
            screenRect: 屏幕矩形区域
        """
        if not self._isActive and not self._hasError:
            return
        
        # 计算显示位置（屏幕顶部中央）
        indicatorRect = self._CalculateIndicatorRect(painter, screenRect)
        
        # 绘制背景
        self._DrawBackground(painter, indicatorRect)
        
        # 绘制内容
        if self._hasError:
            self._DrawErrorMessage(painter, indicatorRect)
        else:
            self._DrawPathContent(painter, indicatorRect)
    #endregion
    
    #region Drawing Methods
    def _CalculateIndicatorRect(self, painter: QPainter, screenRect: QRect) -> QRect:
        """
        计算指示器矩形区域
        
        Args:
            painter: QPainter绘制对象
            screenRect: 屏幕矩形
            
        Returns:
            QRect: 指示器矩形区域
        """
        # 设置字体
        font = QFont("Arial", self._fontSize, QFont.Weight.Bold)
        painter.setFont(font)
        fontMetrics = QFontMetrics(font)
        
        # 计算文本内容
        if self._hasError:
            text = f"错误: {self._errorMessage}"
        else:
            pathText = self._SEPARATOR.join(self._keyPath) if self._keyPath else "网格模式已激活"
            levelText = f" (第{self._currentLevel}层)" if self._currentLevel > 0 else ""
            text = pathText + levelText
        
        # 计算文本尺寸
        textWidth = fontMetrics.horizontalAdvance(text)
        textHeight = fontMetrics.height()
        
        # 计算指示器尺寸
        indicatorWidth = textWidth + 2 * self._padding
        indicatorHeight = textHeight + 2 * self._padding
        
        # 计算位置（屏幕顶部中央）
        x = (screenRect.width() - indicatorWidth) // 2
        y = 50  # 距离顶部50像素
        
        return QRect(x, y, indicatorWidth, indicatorHeight)
    
    def _DrawBackground(self, painter: QPainter, rect: QRect) -> None:
        """
        绘制背景
        
        Args:
            painter: QPainter绘制对象
            rect: 背景矩形
        """
        # 绘制圆角矩形背景
        painter.setBrush(self._backgroundColor)
        painter.setPen(QPen(self._borderColor, 1))
        painter.drawRoundedRect(rect, self._borderRadius, self._borderRadius)
    
    def _DrawPathContent(self, painter: QPainter, rect: QRect) -> None:
        """
        绘制路径内容
        
        Args:
            painter: QPainter绘制对象
            rect: 内容矩形
        """
        # 设置文字样式
        font = QFont("Arial", self._fontSize, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(self._textColor)
        
        # 生成显示文本
        if self._keyPath:
            pathText = self._SEPARATOR.join(self._keyPath)
            levelText = f" (第{self._currentLevel}层)"
            text = pathText + levelText
        else:
            text = "网格模式已激活"
        
        # 绘制文本（居中对齐）
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
    
    def _DrawErrorMessage(self, painter: QPainter, rect: QRect) -> None:
        """
        绘制错误消息
        
        Args:
            painter: QPainter绘制对象
            rect: 内容矩形
        """
        # 设置错误文字样式
        font = QFont("Arial", self._fontSize, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(self._errorColor)
        
        # 绘制错误文本
        text = f"错误: {self._errorMessage}"
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
    
    def _ClearError(self) -> None:
        """
        内部方法：清除错误状态
        """
        self._hasError = False
        self._errorMessage = ""
    #endregion
    
    #region Properties
    @property
    def KeyPath(self) -> List[str]:
        """获取当前按键路径"""
        return self._keyPath.copy()
    
    @property
    def CurrentLevel(self) -> int:
        """获取当前递归层级"""
        return self._currentLevel
    
    @property
    def IsActive(self) -> bool:
        """获取激活状态"""
        return self._isActive
    
    @property
    def HasError(self) -> bool:
        """获取错误状态"""
        return self._hasError
    
    @property
    def PathString(self) -> str:
        """获取路径字符串表示"""
        return self._SEPARATOR.join(self._keyPath) if self._keyPath else ""
    #endregion
    
    #region Style Configuration
    def SetFontSize(self, size: int) -> None:
        """设置字体大小"""
        self._fontSize = size
    
    def SetTextColor(self, color: QColor) -> None:
        """设置文字颜色"""
        self._textColor = color
    
    def SetBackgroundColor(self, color: QColor) -> None:
        """设置背景颜色"""
        self._backgroundColor = color
    
    def SetErrorColor(self, color: QColor) -> None:
        """设置错误文字颜色"""
        self._errorColor = color
    
    def SetPadding(self, padding: int) -> None:
        """设置内边距"""
        self._padding = padding
    #endregion

#endregion