#region GridRenderer Tests
"""
GridRenderer 组件测试
测试网格渲染系统的各项功能
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QColor, QPainter, QPen, QFont

# 添加源代码路径
sys.path.insert(0, r'D:\GitProj\KeyboardClicker\src')

from ui.grid_renderer import GridRenderer


class TestGridRenderer:
    """GridRenderer 测试类"""
    
    @pytest.fixture
    def renderer(self):
        """创建GridRenderer实例"""
        return GridRenderer()
    
    @pytest.fixture
    def mock_painter(self):
        """创建模拟QPainter"""
        return Mock(spec=QPainter)
    
    @pytest.fixture
    def test_rect(self):
        """测试用矩形"""
        return QRect(0, 0, 300, 300)
    
    def test_init_default_values(self, renderer):
        """测试初始化默认值"""
        assert renderer._gridColor == QColor("#00FF00")
        assert renderer._gridWidth == 2
        assert renderer._keyFontSize == 24
        assert renderer._keyColor == QColor("#FFFFFF")
        assert renderer._highlightColor == QColor("#FFFF00")
        assert renderer._activeCell == (-1, -1)
    
    def test_key_position_mapping(self):
        """测试按键位置映射"""
        # 测试按键到位置的映射
        assert GridRenderer.GetKeyPosition('Q') == (0, 0)
        assert GridRenderer.GetKeyPosition('W') == (0, 1)
        assert GridRenderer.GetKeyPosition('E') == (0, 2)
        assert GridRenderer.GetKeyPosition('A') == (1, 0)
        assert GridRenderer.GetKeyPosition('S') == (1, 1)
        assert GridRenderer.GetKeyPosition('D') == (1, 2)
        assert GridRenderer.GetKeyPosition('Z') == (2, 0)
        assert GridRenderer.GetKeyPosition('X') == (2, 1)
        assert GridRenderer.GetKeyPosition('C') == (2, 2)
        
        # 测试无效按键
        assert GridRenderer.GetKeyPosition('F') == (-1, -1)
        
        # 测试位置到按键的映射
        assert GridRenderer.GetPositionKey(0, 0) == 'Q'
        assert GridRenderer.GetPositionKey(1, 1) == 'S'
        assert GridRenderer.GetPositionKey(2, 2) == 'C'
        
        # 测试无效位置
        assert GridRenderer.GetPositionKey(3, 0) == ""
        assert GridRenderer.GetPositionKey(-1, 0) == ""
    
    def test_update_grid(self, renderer):
        """测试网格更新"""
        new_rect = QRect(100, 100, 400, 400)
        renderer.UpdateGrid(new_rect)
        assert renderer._currentRegion == new_rect
    
    def test_set_active_cell(self, renderer):
        """测试设置活跃单元格"""
        # 测试有效单元格
        renderer.SetActiveCell(1, 2)
        assert renderer._activeCell == (1, 2)
        
        # 测试边界值
        renderer.SetActiveCell(0, 0)
        assert renderer._activeCell == (0, 0)
        
        renderer.SetActiveCell(2, 2)
        assert renderer._activeCell == (2, 2)
        
        # 测试无效单元格
        renderer.SetActiveCell(-1, 0)
        assert renderer._activeCell == (-1, -1)
        
        renderer.SetActiveCell(3, 0)
        assert renderer._activeCell == (-1, -1)
        
        renderer.SetActiveCell(0, 3)
        assert renderer._activeCell == (-1, -1)
    
    def test_clear_active_cell(self, renderer):
        """测试清除活跃单元格"""
        renderer.SetActiveCell(1, 1)
        assert renderer._activeCell == (1, 1)
        
        renderer.ClearActiveCell()
        assert renderer._activeCell == (-1, -1)
    
    def test_get_cell_rect(self, renderer, test_rect):
        """测试获取单元格矩形"""
        # 测试各个单元格
        cell_00 = renderer.GetCellRect(0, 0, test_rect)
        assert cell_00 == QRect(0, 0, 100, 100)
        
        cell_11 = renderer.GetCellRect(1, 1, test_rect)
        assert cell_11 == QRect(100, 100, 100, 100)
        
        cell_22 = renderer.GetCellRect(2, 2, test_rect)
        assert cell_22 == QRect(200, 200, 100, 100)
        
        # 测试偏移矩形
        offset_rect = QRect(50, 50, 300, 300)
        cell_01 = renderer.GetCellRect(0, 1, offset_rect)
        assert cell_01 == QRect(150, 50, 100, 100)
    
    def test_render_grid_calls(self, renderer, mock_painter, test_rect):
        """测试网格渲染调用"""
        with patch.object(renderer, '_DrawBackground') as mock_bg, \
             patch.object(renderer, '_DrawGridLines') as mock_lines, \
             patch.object(renderer, '_DrawKeyLabels') as mock_labels, \
             patch.object(renderer, '_DrawActiveHighlight') as mock_highlight:
            
            renderer.RenderGrid(mock_painter, test_rect)
            
            # 验证所有绘制方法被调用
            mock_bg.assert_called_once_with(mock_painter, test_rect)
            mock_lines.assert_called_once_with(mock_painter, test_rect)
            mock_labels.assert_called_once_with(mock_painter, test_rect)
            mock_highlight.assert_called_once_with(mock_painter, test_rect)
            
            # 验证当前区域已更新
            assert renderer._currentRegion == test_rect
    
    def test_draw_background(self, renderer, mock_painter, test_rect):
        """测试背景绘制"""
        renderer._DrawBackground(mock_painter, test_rect)
        
        # 验证fillRect被调用
        mock_painter.fillRect.assert_called_once_with(test_rect, renderer._backgroundColor)
    
    def test_draw_grid_lines(self, renderer, mock_painter, test_rect):
        """测试网格线绘制"""
        renderer._DrawGridLines(mock_painter, test_rect)
        
        # 验证画笔设置
        mock_painter.setPen.assert_called()
        
        # 验证绘制线条调用 (2条垂直线 + 2条水平线 + 1个边框)
        assert mock_painter.drawLine.call_count == 4
        mock_painter.drawRect.assert_called_once_with(test_rect)
    
    def test_draw_key_labels(self, renderer, mock_painter, test_rect):
        """测试按键标签绘制"""
        with patch('ui.grid_renderer.QFont') as mock_font, \
             patch('ui.grid_renderer.QFontMetrics') as mock_metrics:
            
            mock_metrics_instance = Mock()
            mock_metrics_instance.horizontalAdvance.return_value = 10
            mock_metrics_instance.height.return_value = 20
            mock_metrics.return_value = mock_metrics_instance
            
            renderer._DrawKeyLabels(mock_painter, test_rect)
            
            # 验证字体设置
            mock_painter.setFont.assert_called()
            mock_painter.setPen.assert_called_with(renderer._keyColor)
            
            # 验证文字绘制 (9个单元格)
            assert mock_painter.drawText.call_count == 9
    
    def test_draw_active_highlight_no_active(self, renderer, mock_painter, test_rect):
        """测试无活跃单元格时的高亮绘制"""
        renderer.ClearActiveCell()
        renderer._DrawActiveHighlight(mock_painter, test_rect)
        
        # 应该没有绘制调用
        mock_painter.setPen.assert_not_called()
        mock_painter.drawRect.assert_not_called()
        mock_painter.fillRect.assert_not_called()
    
    def test_draw_active_highlight_with_active(self, renderer, mock_painter, test_rect):
        """测试有活跃单元格时的高亮绘制"""
        renderer.SetActiveCell(1, 1)
        renderer._DrawActiveHighlight(mock_painter, test_rect)
        
        # 验证高亮绘制
        assert mock_painter.setPen.call_count >= 1
        assert mock_painter.drawRect.call_count >= 1
        assert mock_painter.fillRect.call_count >= 1
    
    def test_style_configuration(self, renderer):
        """测试样式配置"""
        # 测试设置网格颜色
        new_color = QColor("#FF0000")
        renderer.SetGridColor(new_color)
        assert renderer._gridColor == new_color
        
        # 测试设置网格宽度
        renderer.SetGridWidth(5)
        assert renderer._gridWidth == 5
        
        # 测试设置字体大小
        renderer.SetKeyFontSize(30)
        assert renderer._keyFontSize == 30
        
        # 测试设置按键颜色
        key_color = QColor("#0000FF")
        renderer.SetKeyColor(key_color)
        assert renderer._keyColor == key_color
        
        # 测试设置高亮颜色
        highlight_color = QColor("#00FFFF")
        renderer.SetHighlightColor(highlight_color)
        assert renderer._highlightColor == highlight_color
    
    def test_case_insensitive_key_position(self):
        """测试按键位置获取的大小写不敏感"""
        assert GridRenderer.GetKeyPosition('q') == (0, 0)
        assert GridRenderer.GetKeyPosition('Q') == (0, 0)
        assert GridRenderer.GetKeyPosition('s') == (1, 1)
        assert GridRenderer.GetKeyPosition('S') == (1, 1)
    
    def test_edge_cases(self, renderer, test_rect):
        """测试边界情况"""
        # 测试零尺寸矩形
        zero_rect = QRect(0, 0, 0, 0)
        cell_rect = renderer.GetCellRect(0, 0, zero_rect)
        assert cell_rect.width() == 0
        assert cell_rect.height() == 0
        
        # 测试非均匀分割（301x301）
        odd_rect = QRect(0, 0, 301, 301)
        cell_rect = renderer.GetCellRect(0, 0, odd_rect)
        assert cell_rect.width() == 100  # 301 // 3 = 100
        assert cell_rect.height() == 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

#endregion