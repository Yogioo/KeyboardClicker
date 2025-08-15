# -*- coding: utf-8 -*-
"""
网格计算引擎
实现3x3网格的递归分割计算逻辑
"""

from typing import List, Optional, Tuple
import math
from .interfaces import Rectangle, Point, GridCell


#region 网格计算核心类

class GridCalculator:
    """网格计算引擎
    
    负责3x3网格的计算、递归分割和坐标转换
    """
    
    def __init__(self):
        # 九宫格按键映射 (索引0-8对应QWEASDZXC)
        self._keyMapping = {
            'Q': 0, 'W': 1, 'E': 2,    # 第一行
            'A': 3, 'S': 4, 'D': 5,    # 第二行
            'Z': 6, 'X': 7, 'C': 8     # 第三行
        }
        
        # 反向映射
        self._indexMapping = {v: k for k, v in self._keyMapping.items()}
    
    def CalculateGrid3x3(self, region: Rectangle) -> List[GridCell]:
        """计算3x3网格
        
        将给定区域分割为3x3网格，返回9个网格单元
        
        Args:
            region: 要分割的矩形区域
            
        Returns:
            包含9个GridCell的列表
        """
        cells = []
        
        # 计算每个单元格的尺寸
        cellWidth = region.Width // 3
        cellHeight = region.Height // 3
        
        # 生成3x3网格
        for row in range(3):
            for col in range(3):
                # 计算单元格索引 (0-8)
                index = row * 3 + col
                
                # 计算单元格位置
                x = region.X + col * cellWidth
                y = region.Y + row * cellHeight
                
                # 最后一列/行处理边界对齐
                width = cellWidth
                height = cellHeight
                
                if col == 2:  # 最后一列
                    width = region.X + region.Width - x
                if row == 2:  # 最后一行
                    height = region.Y + region.Height - y
                
                # 创建单元格区域
                cellRegion = Rectangle(x, y, width, height)
                
                # 创建网格单元
                cell = GridCell(
                    Index=index,
                    Region=cellRegion,
                    Center=cellRegion.Center
                )
                
                cells.append(cell)
        
        return cells
    
    def GetGridCell(self, region: Rectangle, cellIndex: int) -> Optional[GridCell]:
        """获取指定索引的网格单元
        
        Args:
            region: 网格区域
            cellIndex: 单元格索引 (0-8)
            
        Returns:
            GridCell对象，如果索引无效返回None
        """
        if not (0 <= cellIndex <= 8):
            return None
        
        cells = self.CalculateGrid3x3(region)
        return cells[cellIndex]
    
    def GetCellCenter(self, cellRect: Rectangle) -> Point:
        """获取单元格中心点
        
        Args:
            cellRect: 单元格矩形
            
        Returns:
            中心点坐标
        """
        return cellRect.Center
    
    def KeyToIndex(self, key: str) -> Optional[int]:
        """按键转换为网格索引
        
        Args:
            key: 按键字符 (Q,W,E,A,S,D,Z,X,C)
            
        Returns:
            网格索引 (0-8)，无效按键返回None
        """
        return self._keyMapping.get(key.upper())
    
    def IndexToKey(self, index: int) -> Optional[str]:
        """网格索引转换为按键
        
        Args:
            index: 网格索引 (0-8)
            
        Returns:
            按键字符，无效索引返回None
        """
        return self._indexMapping.get(index)
    
    def ProcessKeyPath(self, keySequence: str, screenRect: Rectangle) -> Tuple[Optional[Point], List[Rectangle]]:
        """处理按键路径，计算最终目标点
        
        Args:
            keySequence: 按键序列字符串 (如 "EDC")
            screenRect: 屏幕区域
            
        Returns:
            元组 (目标点, 递归区域列表)
            如果路径无效，目标点为None
        """
        if not keySequence:
            return None, []
        
        regions = [screenRect]  # 保存每层的区域
        currentRegion = screenRect
        
        # 逐层处理每个按键
        for i, key in enumerate(keySequence):
            # 获取按键对应的网格索引
            cellIndex = self.KeyToIndex(key)
            if cellIndex is None:
                return None, regions
            
            # 获取指定的网格单元
            cell = self.GetGridCell(currentRegion, cellIndex)
            if cell is None:
                return None, regions
            
            # 更新当前区域为选中的单元格
            currentRegion = cell.Region
            regions.append(currentRegion)
        
        # 返回最终区域的中心点作为目标
        targetPoint = self.GetCellCenter(currentRegion)
        return targetPoint, regions
    
    def RecursiveSubdivide(self, currentRect: Rectangle, keyIndex: int) -> Optional[Rectangle]:
        """递归细分区域
        
        Args:
            currentRect: 当前区域
            keyIndex: 按键索引 (0-8)
            
        Returns:
            细分后的子区域，无效索引返回None
        """
        cell = self.GetGridCell(currentRect, keyIndex)
        return cell.Region if cell else None
    
    def ValidateKeySequence(self, keys: str) -> bool:
        """验证按键序列有效性
        
        Args:
            keys: 按键序列
            
        Returns:
            是否为有效序列
        """
        if not keys:
            return False
        
        # 检查每个字符是否为有效的九宫格按键
        validKeys = set(self._keyMapping.keys())
        return all(key.upper() in validKeys for key in keys)
    
    def CalculateRecursionDepth(self, keySequence: str) -> int:
        """计算递归深度
        
        Args:
            keySequence: 按键序列
            
        Returns:
            递归深度
        """
        return len(keySequence) if self.ValidateKeySequence(keySequence) else 0
    
    def GetMinimumRegionSize(self) -> Tuple[int, int]:
        """获取最小区域尺寸
        
        Returns:
            最小宽度和高度的元组
        """
        # 最小区域应该至少能容纳有意义的点击
        return (9, 9)  # 3x3的最小单元格
    
    def CanSubdivide(self, region: Rectangle) -> bool:
        """检查区域是否可以继续细分
        
        Args:
            region: 要检查的区域
            
        Returns:
            是否可以细分
        """
        minWidth, minHeight = self.GetMinimumRegionSize()
        return (region.Width >= minWidth * 3 and 
                region.Height >= minHeight * 3)

#endregion