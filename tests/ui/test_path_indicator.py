#region PathIndicator Tests
"""
PathIndicator 组件测试
测试路径指示器的各项功能
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QColor, QPainter, QFont, QFontMetrics

# 添加源代码路径
sys.path.insert(0, r'D:\GitProj\KeyboardClicker\src')

from ui.path_indicator import PathIndicator


class TestPathIndicator:
    """PathIndicator 测试类"""
    
    @pytest.fixture
    def indicator(self):
        """创建PathIndicator实例"""
        return PathIndicator()
    
    @pytest.fixture
    def mock_painter(self):
        """创建模拟QPainter"""
        return Mock(spec=QPainter)
    
    @pytest.fixture
    def test_screen_rect(self):
        """测试用屏幕矩形"""
        return QRect(0, 0, 1920, 1080)
    
    def test_init_default_values(self, indicator):
        """测试初始化默认值"""
        assert indicator._keyPath == []
        assert indicator._currentLevel == 0
        assert not indicator._isActive
        assert not indicator._hasError
        assert indicator._errorMessage == ""
        
        # 测试样式默认值
        assert indicator._backgroundColor == QColor(0, 0, 0, 180)
        assert indicator._textColor == QColor("#FFFFFF")
        assert indicator._errorColor == QColor("#FF0000")
        assert indicator._fontSize == 18
        assert indicator._padding == 15
    
    def test_update_path(self, indicator):
        """测试路径更新"""
        # 测试正常路径
        path = ['Q', 'W', 'E']
        indicator.UpdatePath(path)
        
        assert indicator.KeyPath == path
        assert indicator.CurrentLevel == 3
        assert not indicator.HasError
        
        # 测试空路径
        indicator.UpdatePath([])
        assert indicator.KeyPath == []
        assert indicator.CurrentLevel == 0
    
    def test_update_path_max_length(self, indicator):
        """测试路径最大长度限制"""
        # 创建超过最大长度的路径
        long_path = ['Q'] * 15  # 超过_MAX_PATH_LENGTH(10)
        indicator.UpdatePath(long_path)
        
        # 应该只保留最后10个
        assert len(indicator.KeyPath) == 10
        assert indicator.KeyPath == ['Q'] * 10
        assert indicator.CurrentLevel == 10
    
    def test_add_key(self, indicator):
        """测试添加单个按键"""
        # 添加第一个按键
        indicator.AddKey('Q')
        assert indicator.KeyPath == ['Q']
        assert indicator.CurrentLevel == 1
        
        # 添加更多按键
        indicator.AddKey('w')  # 测试小写转大写
        indicator.AddKey('E')
        assert indicator.KeyPath == ['Q', 'W', 'E']
        assert indicator.CurrentLevel == 3
    
    def test_add_key_max_length(self, indicator):
        """测试添加按键的最大长度限制"""
        # 添加到最大长度
        for i in range(10):
            indicator.AddKey('Q')
        
        assert len(indicator.KeyPath) == 10
        
        # 尝试添加第11个，应该被忽略
        indicator.AddKey('W')
        assert len(indicator.KeyPath) == 10
        assert indicator.KeyPath[-1] == 'Q'  # 最后一个仍然是Q
    
    def test_remove_last_key(self, indicator):
        """测试移除最后一个按键"""
        # 准备测试数据
        indicator.UpdatePath(['Q', 'W', 'E'])
        
        # 移除最后一个
        result = indicator.RemoveLastKey()
        assert result is True
        assert indicator.KeyPath == ['Q', 'W']
        assert indicator.CurrentLevel == 2
        
        # 继续移除
        indicator.RemoveLastKey()
        indicator.RemoveLastKey()
        assert indicator.KeyPath == []
        assert indicator.CurrentLevel == 0
        
        # 尝试从空路径移除
        result = indicator.RemoveLastKey()
        assert result is False
    
    def test_clear_path(self, indicator):
        """测试清空路径"""
        # 准备测试数据
        indicator.UpdatePath(['Q', 'W', 'E'])
        indicator.ShowError("测试错误")
        
        # 清空路径
        indicator.ClearPath()
        
        assert indicator.KeyPath == []
        assert indicator.CurrentLevel == 0
        assert not indicator.HasError
    
    def test_set_active(self, indicator):
        """测试设置激活状态"""
        # 准备测试数据
        indicator.UpdatePath(['Q', 'W'])
        
        # 设置激活
        indicator.SetActive(True)
        assert indicator.IsActive
        
        # 设置非激活（应该清空路径）
        indicator.SetActive(False)
        assert not indicator.IsActive
        assert indicator.KeyPath == []
    
    def test_error_handling(self, indicator):
        """测试错误处理"""
        # 显示错误
        error_msg = "测试错误消息"
        indicator.ShowError(error_msg)
        
        assert indicator.HasError
        assert indicator._errorMessage == error_msg
        
        # 清除错误
        indicator.ClearError()
        assert not indicator.HasError
        assert indicator._errorMessage == ""
    
    def test_path_string_property(self, indicator):
        """测试路径字符串属性"""
        # 空路径
        assert indicator.PathString == ""
        
        # 单个按键
        indicator.AddKey('Q')
        assert indicator.PathString == "Q"
        
        # 多个按键
        indicator.AddKey('W')
        indicator.AddKey('E')
        assert indicator.PathString == "Q → W → E"
    
    def test_render_inactive_no_error(self, indicator, mock_painter, test_screen_rect):
        """测试非激活且无错误时的渲染"""
        indicator.SetActive(False)
        indicator.ClearError()
        
        indicator.Render(mock_painter, test_screen_rect)
        
        # 应该没有任何绘制调用
        mock_painter.setFont.assert_not_called()
        mock_painter.setBrush.assert_not_called()
        mock_painter.drawRoundedRect.assert_not_called()
        mock_painter.drawText.assert_not_called()
    
    def test_render_active_path(self, indicator, mock_painter, test_screen_rect):
        """测试激活状态下的路径渲染"""
        indicator.SetActive(True)
        indicator.UpdatePath(['Q', 'W'])
        
        with patch.object(indicator, '_CalculateIndicatorRect') as mock_calc, \
             patch.object(indicator, '_DrawBackground') as mock_bg, \
             patch.object(indicator, '_DrawPathContent') as mock_content:
            
            mock_rect = QRect(100, 50, 200, 40)
            mock_calc.return_value = mock_rect
            
            indicator.Render(mock_painter, test_screen_rect)
            
            mock_calc.assert_called_once_with(mock_painter, test_screen_rect)
            mock_bg.assert_called_once_with(mock_painter, mock_rect)
            mock_content.assert_called_once_with(mock_painter, mock_rect)
    
    def test_render_error_state(self, indicator, mock_painter, test_screen_rect):
        """测试错误状态下的渲染"""
        indicator.ShowError("测试错误")
        
        with patch.object(indicator, '_CalculateIndicatorRect') as mock_calc, \
             patch.object(indicator, '_DrawBackground') as mock_bg, \
             patch.object(indicator, '_DrawErrorMessage') as mock_error:
            
            mock_rect = QRect(100, 50, 200, 40)
            mock_calc.return_value = mock_rect
            
            indicator.Render(mock_painter, test_screen_rect)
            
            mock_calc.assert_called_once_with(mock_painter, test_screen_rect)
            mock_bg.assert_called_once_with(mock_painter, mock_rect)
            mock_error.assert_called_once_with(mock_painter, mock_rect)
    
    def test_calculate_indicator_rect(self, indicator, mock_painter, test_screen_rect):
        """测试指示器矩形计算"""
        with patch('ui.path_indicator.QFont') as mock_font, \
             patch('ui.path_indicator.QFontMetrics') as mock_metrics:
            
            # 模拟字体度量
            mock_metrics_instance = Mock()
            mock_metrics_instance.horizontalAdvance.return_value = 100
            mock_metrics_instance.height.return_value = 20
            mock_metrics.return_value = mock_metrics_instance
            
            indicator.SetActive(True)
            indicator.UpdatePath(['Q', 'W'])
            
            result_rect = indicator._CalculateIndicatorRect(mock_painter, test_screen_rect)
            
            # 验证计算结果
            expected_width = 100 + 2 * 15  # text_width + 2 * padding
            expected_height = 20 + 2 * 15  # text_height + 2 * padding
            expected_x = (1920 - expected_width) // 2  # 居中
            expected_y = 50  # 固定距离顶部50像素
            
            assert result_rect.width() == expected_width
            assert result_rect.height() == expected_height
            assert result_rect.x() == expected_x
            assert result_rect.y() == expected_y
    
    def test_draw_background(self, indicator, mock_painter):
        """测试背景绘制"""
        test_rect = QRect(100, 50, 200, 40)
        
        indicator._DrawBackground(mock_painter, test_rect)
        
        # 验证绘制调用
        mock_painter.setBrush.assert_called_once_with(indicator._backgroundColor)
        mock_painter.setPen.assert_called_once()
        mock_painter.drawRoundedRect.assert_called_once_with(
            test_rect, indicator._borderRadius, indicator._borderRadius
        )
    
    def test_draw_path_content_empty(self, indicator, mock_painter):
        """测试空路径的内容绘制"""
        test_rect = QRect(100, 50, 200, 40)
        
        with patch('ui.path_indicator.QFont') as mock_font:
            indicator._DrawPathContent(mock_painter, test_rect)
            
            # 验证绘制默认文本
            mock_painter.setFont.assert_called_once()
            mock_painter.setPen.assert_called_once_with(indicator._textColor)
            mock_painter.drawText.assert_called_once()
            
            # 检查绘制的文本是否为默认激活消息
            call_args = mock_painter.drawText.call_args
            assert "网格模式已激活" in str(call_args)
    
    def test_draw_path_content_with_path(self, indicator, mock_painter):
        """测试有路径的内容绘制"""
        test_rect = QRect(100, 50, 200, 40)
        indicator.UpdatePath(['Q', 'W', 'E'])
        
        with patch('ui.path_indicator.QFont') as mock_font:
            indicator._DrawPathContent(mock_painter, test_rect)
            
            # 验证绘制调用
            mock_painter.setFont.assert_called_once()
            mock_painter.setPen.assert_called_once_with(indicator._textColor)
            mock_painter.drawText.assert_called_once()
            
            # 检查绘制的文本包含路径
            call_args = mock_painter.drawText.call_args
            assert "Q → W → E" in str(call_args)
            assert "(第3层)" in str(call_args)
    
    def test_draw_error_message(self, indicator, mock_painter):
        """测试错误消息绘制"""
        test_rect = QRect(100, 50, 200, 40)
        error_msg = "测试错误"
        indicator.ShowError(error_msg)
        
        with patch('ui.path_indicator.QFont') as mock_font:
            indicator._DrawErrorMessage(mock_painter, test_rect)
            
            # 验证错误绘制
            mock_painter.setFont.assert_called_once()
            mock_painter.setPen.assert_called_once_with(indicator._errorColor)
            mock_painter.drawText.assert_called_once()
            
            # 检查绘制的文本包含错误信息
            call_args = mock_painter.drawText.call_args
            assert f"错误: {error_msg}" in str(call_args)
    
    def test_style_configuration(self, indicator):
        """测试样式配置"""
        # 测试字体大小设置
        indicator.SetFontSize(24)
        assert indicator._fontSize == 24
        
        # 测试文字颜色设置
        new_color = QColor("#FF0000")
        indicator.SetTextColor(new_color)
        assert indicator._textColor == new_color
        
        # 测试背景颜色设置
        bg_color = QColor(255, 255, 255, 100)
        indicator.SetBackgroundColor(bg_color)
        assert indicator._backgroundColor == bg_color
        
        # 测试错误颜色设置
        error_color = QColor("#0000FF")
        indicator.SetErrorColor(error_color)
        assert indicator._errorColor == error_color
        
        # 测试内边距设置
        indicator.SetPadding(20)
        assert indicator._padding == 20
    
    def test_error_clears_on_path_update(self, indicator):
        """测试路径更新时清除错误状态"""
        # 设置错误状态
        indicator.ShowError("测试错误")
        assert indicator.HasError
        
        # 更新路径应该清除错误
        indicator.UpdatePath(['Q'])
        assert not indicator.HasError
        
        # 添加按键也应该清除错误
        indicator.ShowError("另一个错误")
        indicator.AddKey('W')
        assert not indicator.HasError


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

#endregion