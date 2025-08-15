# -*- coding: utf-8 -*-
"""
GridCalculator单元测试
测试网格计算引擎的所有功能
"""

import unittest
from typing import List
from src.core.grid_calculator import GridCalculator
from src.core.interfaces import Rectangle, Point, GridCell


#region 基础测试类

class TestGridCalculator(unittest.TestCase):
    """GridCalculator测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.calculator = GridCalculator()
        self.testRect = Rectangle(0, 0, 300, 300)  # 300x300的测试区域
    
    def tearDown(self):
        """测试后清理"""
        pass

#endregion


#region 网格计算测试

class TestGrid3x3Calculation(TestGridCalculator):
    """3x3网格计算测试"""
    
    def test_CalculateGrid3x3_正常区域(self):
        """测试正常区域的3x3网格计算"""
        cells = self.calculator.CalculateGrid3x3(self.testRect)
        
        # 验证基本属性
        self.assertEqual(len(cells), 9)
        self.assertIsInstance(cells, list)
        
        # 验证每个单元格
        for i, cell in enumerate(cells):
            self.assertIsInstance(cell, GridCell)
            self.assertEqual(cell.Index, i)
            self.assertIsInstance(cell.Region, Rectangle)
            self.assertIsInstance(cell.Center, Point)
    
    def test_CalculateGrid3x3_单元格尺寸正确(self):
        """测试单元格尺寸计算正确性"""
        cells = self.calculator.CalculateGrid3x3(self.testRect)
        
        expectedSize = 100  # 300/3 = 100
        
        # 检查前8个单元格(非边界)
        for i in range(8):
            cell = cells[i]
            if i % 3 != 2:  # 非最后一列
                self.assertEqual(cell.Region.Width, expectedSize)
            if i < 6:  # 非最后一行
                self.assertEqual(cell.Region.Height, expectedSize)
    
    def test_CalculateGrid3x3_位置映射正确(self):
        """测试单元格位置映射正确性"""
        cells = self.calculator.CalculateGrid3x3(self.testRect)
        
        # 测试九宫格位置
        # Q(0) W(1) E(2)
        # A(3) S(4) D(5) 
        # Z(6) X(7) C(8)
        
        # Q - 左上角
        self.assertEqual(cells[0].Region.X, 0)
        self.assertEqual(cells[0].Region.Y, 0)
        
        # E - 右上角  
        self.assertEqual(cells[2].Region.X, 200)
        self.assertEqual(cells[2].Region.Y, 0)
        
        # Z - 左下角
        self.assertEqual(cells[6].Region.X, 0)
        self.assertEqual(cells[6].Region.Y, 200)
        
        # C - 右下角
        self.assertEqual(cells[8].Region.X, 200)
        self.assertEqual(cells[8].Region.Y, 200)
    
    def test_CalculateGrid3x3_中心点计算(self):
        """测试中心点计算正确性"""
        cells = self.calculator.CalculateGrid3x3(self.testRect)
        
        # 检查S键对应的中心单元格
        centerCell = cells[4]  # S键索引为4
        expectedCenter = Point(150, 150)  # 中心应该在(150,150)
        
        self.assertEqual(centerCell.Center.X, expectedCenter.X)
        self.assertEqual(centerCell.Center.Y, expectedCenter.Y)
    
    def test_CalculateGrid3x3_边界对齐(self):
        """测试边界对齐处理"""
        # 使用不能被3整除的区域
        testRect = Rectangle(0, 0, 301, 301)
        cells = self.calculator.CalculateGrid3x3(testRect)
        
        # 最后一列和最后一行应该对齐到边界
        lastColCell = cells[2]  # E键
        lastRowCell = cells[6]  # Z键  
        cornerCell = cells[8]   # C键
        
        # 验证最后一列宽度
        expectedLastColWidth = 301 - 200  # 101
        self.assertEqual(lastColCell.Region.Width, expectedLastColWidth)
        
        # 验证最后一行高度
        expectedLastRowHeight = 301 - 200  # 101
        self.assertEqual(lastRowCell.Region.Height, expectedLastRowHeight)
        
        # 验证右下角单元格
        self.assertEqual(cornerCell.Region.Width, expectedLastColWidth)
        self.assertEqual(cornerCell.Region.Height, expectedLastRowHeight)

#endregion


#region 按键映射测试

class TestKeyMapping(TestGridCalculator):
    """按键映射测试"""
    
    def test_KeyToIndex_有效按键(self):
        """测试有效按键的索引转换"""
        expectedMapping = {
            'Q': 0, 'W': 1, 'E': 2,
            'A': 3, 'S': 4, 'D': 5,
            'Z': 6, 'X': 7, 'C': 8
        }
        
        for key, expectedIndex in expectedMapping.items():
            # 测试大写
            result = self.calculator.KeyToIndex(key)
            self.assertEqual(result, expectedIndex)
            
            # 测试小写
            result = self.calculator.KeyToIndex(key.lower())
            self.assertEqual(result, expectedIndex)
    
    def test_KeyToIndex_无效按键(self):
        """测试无效按键返回None"""
        invalidKeys = ['F', 'G', 'H', '1', '2', '3', '', ' ']
        
        for key in invalidKeys:
            result = self.calculator.KeyToIndex(key)
            self.assertIsNone(result)
    
    def test_IndexToKey_有效索引(self):
        """测试有效索引的按键转换"""
        expectedMapping = {
            0: 'Q', 1: 'W', 2: 'E',
            3: 'A', 4: 'S', 5: 'D',
            6: 'Z', 7: 'X', 8: 'C'
        }
        
        for index, expectedKey in expectedMapping.items():
            result = self.calculator.IndexToKey(index)
            self.assertEqual(result, expectedKey)
    
    def test_IndexToKey_无效索引(self):
        """测试无效索引返回None"""
        invalidIndices = [-1, 9, 10, 100]
        
        for index in invalidIndices:
            result = self.calculator.IndexToKey(index)
            self.assertIsNone(result)

#endregion


#region 单元格获取测试

class TestGridCellRetrieval(TestGridCalculator):
    """网格单元格获取测试"""
    
    def test_GetGridCell_有效索引(self):
        """测试获取有效索引的单元格"""
        for index in range(9):
            cell = self.calculator.GetGridCell(self.testRect, index)
            self.assertIsNotNone(cell)
            self.assertEqual(cell.Index, index)
    
    def test_GetGridCell_无效索引(self):
        """测试获取无效索引的单元格"""
        invalidIndices = [-1, 9, 10, -10]
        
        for index in invalidIndices:
            cell = self.calculator.GetGridCell(self.testRect, index)
            self.assertIsNone(cell)
    
    def test_GetCellCenter_正确计算(self):
        """测试单元格中心点计算"""
        testCellRect = Rectangle(100, 100, 200, 200)
        center = self.calculator.GetCellCenter(testCellRect)
        
        expectedCenter = Point(200, 200)  # 100 + 200/2 = 200
        self.assertEqual(center.X, expectedCenter.X)
        self.assertEqual(center.Y, expectedCenter.Y)

#endregion


#region 路径处理测试

class TestKeyPathProcessing(TestGridCalculator):
    """按键路径处理测试"""
    
    def test_ProcessKeyPath_单个按键(self):
        """测试单个按键的路径处理"""
        targetPoint, regions = self.calculator.ProcessKeyPath("S", self.testRect)
        
        # 验证目标点不为空
        self.assertIsNotNone(targetPoint)
        self.assertIsInstance(targetPoint, Point)
        
        # 验证区域列表
        self.assertEqual(len(regions), 2)  # 原始区域 + 选中区域
        self.assertEqual(regions[0], self.testRect)
        
        # S键应该指向中心
        expectedCenter = Point(150, 150)
        self.assertEqual(targetPoint.X, expectedCenter.X)
        self.assertEqual(targetPoint.Y, expectedCenter.Y)
    
    def test_ProcessKeyPath_多个按键(self):
        """测试多个按键的递归路径处理"""
        targetPoint, regions = self.calculator.ProcessKeyPath("EDC", self.testRect)
        
        # 验证目标点
        self.assertIsNotNone(targetPoint)
        
        # 验证递归层级
        self.assertEqual(len(regions), 4)  # 原始 + 3层递归
        
        # 验证每层区域都在缩小
        for i in range(1, len(regions)):
            currentRegion = regions[i]
            previousRegion = regions[i-1]
            
            self.assertLessEqual(currentRegion.Width, previousRegion.Width)
            self.assertLessEqual(currentRegion.Height, previousRegion.Height)
    
    def test_ProcessKeyPath_空序列(self):
        """测试空按键序列"""
        targetPoint, regions = self.calculator.ProcessKeyPath("", self.testRect)
        
        self.assertIsNone(targetPoint)
        self.assertEqual(len(regions), 0)
    
    def test_ProcessKeyPath_无效按键(self):
        """测试包含无效按键的序列"""
        targetPoint, regions = self.calculator.ProcessKeyPath("SFD", self.testRect)
        
        self.assertIsNone(targetPoint)
        # 应该处理到无效按键为止
        self.assertGreater(len(regions), 0)
    
    def test_ProcessKeyPath_路径一致性(self):
        """测试相同路径的一致性结果"""
        path = "ECD"
        
        # 多次执行相同路径
        result1 = self.calculator.ProcessKeyPath(path, self.testRect)
        result2 = self.calculator.ProcessKeyPath(path, self.testRect)
        
        # 结果应该一致
        self.assertEqual(result1[0].X, result2[0].X)
        self.assertEqual(result1[0].Y, result2[0].Y)
        self.assertEqual(len(result1[1]), len(result2[1]))

#endregion


#region 递归细分测试

class TestRecursiveSubdivision(TestGridCalculator):
    """递归细分测试"""
    
    def test_RecursiveSubdivide_有效索引(self):
        """测试有效索引的递归细分"""
        for index in range(9):
            subdivided = self.calculator.RecursiveSubdivide(self.testRect, index)
            self.assertIsNotNone(subdivided)
            self.assertIsInstance(subdivided, Rectangle)
            
            # 细分后的区域应该在原区域内
            self.assertGreaterEqual(subdivided.X, self.testRect.X)
            self.assertGreaterEqual(subdivided.Y, self.testRect.Y)
            self.assertLessEqual(subdivided.X + subdivided.Width, 
                               self.testRect.X + self.testRect.Width)
            self.assertLessEqual(subdivided.Y + subdivided.Height,
                               self.testRect.Y + self.testRect.Height)
    
    def test_RecursiveSubdivide_无效索引(self):
        """测试无效索引的递归细分"""
        invalidIndices = [-1, 9, 10]
        
        for index in invalidIndices:
            result = self.calculator.RecursiveSubdivide(self.testRect, index)
            self.assertIsNone(result)

#endregion


#region 验证功能测试

class TestValidationFunctions(TestGridCalculator):
    """验证功能测试"""
    
    def test_ValidateKeySequence_有效序列(self):
        """测试有效按键序列验证"""
        validSequences = ["Q", "S", "EDC", "QWEASDZXC", "qwe", "ASD"]
        
        for sequence in validSequences:
            result = self.calculator.ValidateKeySequence(sequence)
            self.assertTrue(result)
    
    def test_ValidateKeySequence_无效序列(self):
        """测试无效按键序列验证"""
        invalidSequences = ["", "F", "QF", "123", "Q1", " ", "Q "]
        
        for sequence in invalidSequences:
            result = self.calculator.ValidateKeySequence(sequence)
            self.assertFalse(result)
    
    def test_CalculateRecursionDepth_正确计算(self):
        """测试递归深度计算"""
        testCases = [
            ("Q", 1),
            ("QW", 2), 
            ("QWE", 3),
            ("QWEASD", 6),
            ("", 0),
            ("QF", 0),  # 无效序列
        ]
        
        for sequence, expectedDepth in testCases:
            depth = self.calculator.CalculateRecursionDepth(sequence)
            self.assertEqual(depth, expectedDepth)
    
    def test_GetMinimumRegionSize_返回合理值(self):
        """测试最小区域尺寸"""
        minWidth, minHeight = self.calculator.GetMinimumRegionSize()
        
        self.assertIsInstance(minWidth, int)
        self.assertIsInstance(minHeight, int)
        self.assertGreater(minWidth, 0)
        self.assertGreater(minHeight, 0)
        self.assertEqual(minWidth, 9)
        self.assertEqual(minHeight, 9)
    
    def test_CanSubdivide_正确判断(self):
        """测试区域可细分性判断"""
        # 可以细分的区域
        largeRect = Rectangle(0, 0, 300, 300)
        self.assertTrue(self.calculator.CanSubdivide(largeRect))
        
        # 不能细分的区域
        smallRect = Rectangle(0, 0, 20, 20)
        self.assertFalse(self.calculator.CanSubdivide(smallRect))
        
        # 边界情况
        borderRect = Rectangle(0, 0, 27, 27)  # 恰好3*9=27
        self.assertTrue(self.calculator.CanSubdivide(borderRect))
        
        tooSmallRect = Rectangle(0, 0, 26, 26)
        self.assertFalse(self.calculator.CanSubdivide(tooSmallRect))

#endregion


#region 边界条件和异常测试

class TestEdgeCasesAndExceptions(TestGridCalculator):
    """边界条件和异常测试"""
    
    def test_极小区域处理(self):
        """测试极小区域的处理"""
        tinyRect = Rectangle(0, 0, 3, 3)
        cells = self.calculator.CalculateGrid3x3(tinyRect)
        
        # 应该仍然返回9个单元格
        self.assertEqual(len(cells), 9)
        
        # 某些单元格可能为0尺寸，但不应该出错
        for cell in cells:
            self.assertIsNotNone(cell)
            self.assertGreaterEqual(cell.Region.Width, 0)
            self.assertGreaterEqual(cell.Region.Height, 0)
    
    def test_负坐标区域处理(self):
        """测试负坐标区域的处理"""
        negRect = Rectangle(-100, -100, 300, 300)
        cells = self.calculator.CalculateGrid3x3(negRect)
        
        self.assertEqual(len(cells), 9)
        
        # 第一个单元格应该从负坐标开始
        firstCell = cells[0]
        self.assertEqual(firstCell.Region.X, -100)
        self.assertEqual(firstCell.Region.Y, -100)
    
    def test_零尺寸区域处理(self):
        """测试零尺寸区域的处理"""
        zeroRect = Rectangle(0, 0, 0, 0)
        cells = self.calculator.CalculateGrid3x3(zeroRect)
        
        self.assertEqual(len(cells), 9)
        
        # 所有单元格应该在同一位置
        for cell in cells:
            self.assertEqual(cell.Region.Width, 0)
            self.assertEqual(cell.Region.Height, 0)

#endregion


#region 性能测试

class TestPerformance(TestGridCalculator):
    """性能测试"""
    
    def test_大量计算性能(self):
        """测试大量计算的性能"""
        import time
        
        start_time = time.time()
        
        # 执行1000次网格计算
        for _ in range(1000):
            self.calculator.CalculateGrid3x3(self.testRect)
        
        elapsed_time = time.time() - start_time
        
        # 1000次计算应该在1秒内完成
        self.assertLess(elapsed_time, 1.0)
    
    def test_复杂路径处理性能(self):
        """测试复杂路径处理性能"""
        import time
        
        longPath = "QWEASDZXC" * 5  # 45个字符的长路径
        
        start_time = time.time()
        
        # 处理10次长路径
        for _ in range(10):
            self.calculator.ProcessKeyPath(longPath, self.testRect)
        
        elapsed_time = time.time() - start_time
        
        # 应该在合理时间内完成
        self.assertLess(elapsed_time, 0.1)

#endregion


if __name__ == '__main__':
    unittest.main()