#region GridRenderer Implementation
"""
网格渲染系统实现
负责绘制3x3网格线和按键标识
"""

from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics
from PyQt6.QtCore import QRect, Qt
from typing import Dict, List, Tuple


class GridRenderer:
    """
    网格渲染器
    
    功能：
    - 绘制3x3网格线
    - 显示按键标识 (Q,W,E,A,S,D,Z,X,C)
    - 高亮活跃区域
    - 网格样式配置
    """
    
    #region Constants
    # QWEASDZXC 键位映射到 3x3 网格位置
    _KEY_POSITIONS: Dict[str, Tuple[int, int]] = {
        'Q': (0, 0), 'W': (0, 1), 'E': (0, 2),  # 第一行
        'A': (1, 0), 'S': (1, 1), 'D': (1, 2),  # 第二行  
        'Z': (2, 0), 'X': (2, 1), 'C': (2, 2)   # 第三行
    }
    
    # 按位置映射到按键
    _POSITION_KEYS: Dict[Tuple[int, int], str] = {
        v: k for k, v in _KEY_POSITIONS.items()
    }
    #endregion
    
    def __init__(self):
        """
        初始化网格渲染器
        """
        self._gridColor = QColor("#00FF00")  # 绿色网格线
        self._gridWidth = 2  # 网格线宽度
        self._backgroundColor = QColor(0, 0, 0, 25)  # 10%透明黑色背景
        self._keyFontSize = 24  # 按键字体大小
        self._keyColor = QColor("#FFFFFF")  # 白色按键文字
        self._highlightColor = QColor("#FFFF00")  # 黄色高亮
        
        self._currentRegion = QRect()
        self._activeCell = (-1, -1)  # 当前活跃单元格
    
    #region Public Methods
    def RenderGrid(self, painter: QPainter, gridRect: QRect) -> None:
        """
        渲染3x3网格
        
        Args:
            painter: QPainter绘制对象
            gridRect: 网格区域矩形
        """
        self._currentRegion = gridRect
        self._DrawBackground(painter, gridRect)
        self._DrawGridLines(painter, gridRect)
        self._DrawKeyLabels(painter, gridRect)
        self._DrawActiveHighlight(painter, gridRect)
    
    def UpdateGrid(self, newRegion: QRect) -> None:
        """
        更新网格区域
        
        Args:
            newRegion: 新的网格区域
        """
        self._currentRegion = newRegion
    
    def SetActiveCell(self, row: int, col: int) -> None:
        """
        设置活跃单元格
        
        Args:
            row: 行索引 (0-2)
            col: 列索引 (0-2)
        """
        if 0 <= row < 3 and 0 <= col < 3:
            self._activeCell = (row, col)
        else:
            self._activeCell = (-1, -1)
    
    def ClearActiveCell(self) -> None:
        """
        清除活跃单元格
        """
        self._activeCell = (-1, -1)
    
    def GetCellRect(self, row: int, col: int, gridRect: QRect) -> QRect:
        """
        获取指定单元格的矩形区域
        
        Args:
            row: 行索引 (0-2)
            col: 列索引 (0-2) 
            gridRect: 网格总区域
            
        Returns:
            QRect: 单元格矩形区域
        """
        cellWidth = gridRect.width() // 3
        cellHeight = gridRect.height() // 3
        
        x = gridRect.left() + col * cellWidth
        y = gridRect.top() + row * cellHeight
        
        return QRect(x, y, cellWidth, cellHeight)
    #endregion
    
    #region Drawing Methods
    def _DrawBackground(self, painter: QPainter, gridRect: QRect) -> None:
        """
        绘制半透明背景
        
        Args:
            painter: QPainter绘制对象
            gridRect: 网格区域
        """
        painter.fillRect(gridRect, self._backgroundColor)
    
    def _DrawGridLines(self, painter: QPainter, gridRect: QRect) -> None:
        """
        绘制网格线
        
        Args:
            painter: QPainter绘制对象
            gridRect: 网格区域
        """
        # 设置网格线样式
        pen = QPen(self._gridColor, self._gridWidth)
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        
        # 计算网格分割点
        cellWidth = gridRect.width() // 3
        cellHeight = gridRect.height() // 3
        
        # 绘制垂直线
        for i in range(1, 3):
            x = gridRect.left() + i * cellWidth
            painter.drawLine(x, gridRect.top(), x, gridRect.bottom())
        
        # 绘制水平线
        for i in range(1, 3):
            y = gridRect.top() + i * cellHeight
            painter.drawLine(gridRect.left(), y, gridRect.right(), y)
        
        # 绘制边框
        painter.drawRect(gridRect)
    
    def _DrawKeyLabels(self, painter: QPainter, gridRect: QRect) -> None:
        """
        绘制按键标识
        
        Args:
            painter: QPainter绘制对象
            gridRect: 网格区域
        """
        # 设置字体
        font = QFont("Arial", self._keyFontSize, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(self._keyColor)
        
        fontMetrics = QFontMetrics(font)
        
        # 为每个单元格绘制按键标识
        for row in range(3):
            for col in range(3):
                cellRect = self.GetCellRect(row, col, gridRect)
                key = self._POSITION_KEYS.get((row, col), "")
                
                if key:
                    # 计算文字位置（左上角偏移）
                    textWidth = fontMetrics.horizontalAdvance(key)
                    textHeight = fontMetrics.height()
                    
                    x = cellRect.left() + 10  # 左边距10像素
                    y = cellRect.top() + textHeight + 5  # 上边距5像素
                    
                    painter.drawText(x, y, key)
    
    def _DrawActiveHighlight(self, painter: QPainter, gridRect: QRect) -> None:
        """
        绘制活跃单元格高亮
        
        Args:
            painter: QPainter绘制对象
            gridRect: 网格区域
        """
        if self._activeCell[0] >= 0 and self._activeCell[1] >= 0:
            row, col = self._activeCell
            cellRect = self.GetCellRect(row, col, gridRect)
            
            # 绘制高亮边框
            highlightPen = QPen(self._highlightColor, self._gridWidth + 2)
            painter.setPen(highlightPen)
            painter.drawRect(cellRect)
            
            # 绘制半透明高亮填充
            highlightFill = QColor(self._highlightColor)
            highlightFill.setAlpha(50)
            painter.fillRect(cellRect, highlightFill)
    #endregion
    
    #region Style Configuration
    def SetGridColor(self, color: QColor) -> None:
        """设置网格线颜色"""
        self._gridColor = color
    
    def SetGridWidth(self, width: int) -> None:
        """设置网格线宽度"""
        self._gridWidth = width
    
    def SetKeyFontSize(self, size: int) -> None:
        """设置按键字体大小"""
        self._keyFontSize = size
    
    def SetKeyColor(self, color: QColor) -> None:
        """设置按键文字颜色"""
        self._keyColor = color
    
    def SetHighlightColor(self, color: QColor) -> None:
        """设置高亮颜色"""
        self._highlightColor = color
    #endregion
    
    #region Utility Methods
    @staticmethod
    def GetKeyPosition(key: str) -> Tuple[int, int]:
        """
        获取按键对应的网格位置
        
        Args:
            key: 按键字符
            
        Returns:
            Tuple[int, int]: (行, 列) 位置，(-1, -1)表示无效按键
        """
        return GridRenderer._KEY_POSITIONS.get(key.upper(), (-1, -1))
    
    @staticmethod
    def GetPositionKey(row: int, col: int) -> str:
        """
        获取网格位置对应的按键
        
        Args:
            row: 行索引
            col: 列索引
            
        Returns:
            str: 按键字符，空字符串表示无效位置
        """
        return GridRenderer._POSITION_KEYS.get((row, col), "")
    #endregion

#endregion