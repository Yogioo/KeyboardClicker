#region UI Integration Tests
"""
UI模块集成测试
测试UI组件之间的协作和完整工作流程
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QPainter

# 添加源代码路径
sys.path.insert(0, r'D:\GitProj\KeyboardClicker\src')

from ui.overlay_window import OverlayWindow
from ui.grid_renderer import GridRenderer
from ui.path_indicator import PathIndicator
from ui.event_handler import EventHandler, UIEventType


class TestUIIntegration:
    """UI模块集成测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """设置QApplication"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
        # 清理
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.close()
    
    @pytest.fixture
    def ui_components(self):
        """创建UI组件"""
        overlay = OverlayWindow()
        renderer = GridRenderer()
        indicator = PathIndicator()
        handler = EventHandler()
        
        return {
            'overlay': overlay,
            'renderer': renderer,
            'indicator': indicator,
            'handler': handler
        }
    
    def test_complete_grid_activation_workflow(self, ui_components):
        """测试完整的网格激活工作流程"""
        overlay = ui_components['overlay']
        renderer = ui_components['renderer']
        indicator = ui_components['indicator']
        handler = ui_components['handler']
        
        # 1. 激活网格系统
        with patch.object(overlay, 'show'), \
             patch.object(overlay, 'raise_'), \
             patch.object(overlay, 'activateWindow'):
            
            # 显示叠加层
            overlay.Show()
            assert overlay.IsVisible()
            
            # 激活路径指示器
            indicator.SetActive(True)
            assert indicator.IsActive
            
            # 处理状态变化事件
            handler.HandleStateChange("grid_active", True)
    
    def test_path_building_and_rendering(self, ui_components):
        """测试路径构建和渲染流程"""
        renderer = ui_components['renderer']
        indicator = ui_components['indicator']
        handler = ui_components['handler']
        
        # 模拟按键输入序列
        key_sequence = ['Q', 'W', 'E']
        
        for i, key in enumerate(key_sequence):
            # 添加按键到路径
            indicator.AddKey(key)
            
            # 更新网格渲染器活跃单元格
            row, col = GridRenderer.GetKeyPosition(key)
            renderer.SetActiveCell(row, col)
            
            # 处理路径更新事件
            handler.HandlePathUpdate(indicator.KeyPath)
            
            # 验证状态
            assert len(indicator.KeyPath) == i + 1
            assert indicator.CurrentLevel == i + 1
            assert renderer._activeCell == (row, col)
    
    def test_error_handling_workflow(self, ui_components):
        """测试错误处理工作流程"""
        indicator = ui_components['indicator']
        handler = ui_components['handler']
        
        # 1. 正常状态
        indicator.SetActive(True)
        indicator.AddKey('Q')
        
        # 2. 触发错误
        error_message = "无效的按键输入"
        indicator.ShowError(error_message)
        handler.HandleError(error_message)
        
        # 3. 验证错误状态
        assert indicator.HasError
        assert indicator._errorMessage == error_message
        assert handler.LastError == error_message
        
        # 4. 恢复正常（添加新按键应清除错误）
        indicator.AddKey('W')
        assert not indicator.HasError
    
    def test_grid_subdivision_simulation(self, ui_components):
        """测试网格细分模拟"""
        overlay = ui_components['overlay']
        renderer = ui_components['renderer']
        indicator = ui_components['indicator']
        
        # 初始屏幕区域
        screen_rect = QRect(0, 0, 900, 900)
        overlay._screenRect = screen_rect
        
        # 第一层：选择Q (左上角)
        indicator.AddKey('Q')
        cell_rect_1 = renderer.GetCellRect(0, 0, screen_rect)  # Q位置
        expected_rect_1 = QRect(0, 0, 300, 300)
        assert cell_rect_1 == expected_rect_1
        
        # 第二层：在Q区域内选择S (中心)
        indicator.AddKey('S')
        cell_rect_2 = renderer.GetCellRect(1, 1, cell_rect_1)  # S位置在Q区域内
        expected_rect_2 = QRect(100, 100, 100, 100)
        assert cell_rect_2 == expected_rect_2
        
        # 验证路径状态
        assert indicator.PathString == "Q → S"
        assert indicator.CurrentLevel == 2
    
    def test_window_lifecycle_with_components(self, ui_components):
        """测试窗口生命周期与组件的协作"""
        overlay = ui_components['overlay']
        renderer = ui_components['renderer']
        indicator = ui_components['indicator']
        handler = ui_components['handler']
        
        # 1. 初始状态
        assert not overlay.IsVisible()
        assert not indicator.IsActive
        
        # 2. 激活
        with patch.object(overlay, 'show'), \
             patch.object(overlay, 'raise_'), \
             patch.object(overlay, 'activateWindow'):
            
            overlay.Show()
            indicator.SetActive(True)
            
            assert overlay.IsVisible()
            assert indicator.IsActive
        
        # 3. 使用过程
        indicator.AddKey('Q')
        renderer.SetActiveCell(0, 0)
        handler.HandlePathUpdate(['Q'])
        
        # 4. 关闭
        with patch.object(overlay, 'hide'):
            overlay.Hide()
            indicator.SetActive(False)
            
            assert not overlay.IsVisible()
            assert not indicator.IsActive
            assert indicator.KeyPath == []  # 非激活时应清空路径
    
    def test_rendering_coordination(self, ui_components):
        """测试渲染协调"""
        overlay = ui_components['overlay']
        renderer = ui_components['renderer']
        indicator = ui_components['indicator']
        
        screen_rect = QRect(0, 0, 1200, 800)
        overlay._screenRect = screen_rect
        
        # 创建模拟painter
        mock_painter = Mock(spec=QPainter)
        
        # 设置状态
        indicator.SetActive(True)
        indicator.UpdatePath(['Q', 'W'])
        renderer.SetActiveCell(0, 1)  # W的位置
        
        # 渲染网格
        renderer.RenderGrid(mock_painter, screen_rect)
        
        # 渲染路径指示器
        indicator.Render(mock_painter, screen_rect)
        
        # 验证渲染调用（具体验证在单元测试中，这里只验证没有异常）
        assert mock_painter.call_count > 0
    
    def test_event_propagation(self, ui_components):
        """测试事件传播"""
        handler = ui_components['handler']
        indicator = ui_components['indicator']
        renderer = ui_components['renderer']
        
        # 注册事件处理器
        grid_handler = Mock()
        path_handler = Mock()
        error_handler = Mock()
        
        handler.RegisterEventHandler(UIEventType.GRID_UPDATE, grid_handler)
        handler.RegisterEventHandler(UIEventType.PATH_UPDATE, path_handler)
        handler.RegisterEventHandler(UIEventType.ERROR_OCCURRED, error_handler)
        
        # 触发事件
        test_rect = QRect(100, 100, 200, 200)
        handler.HandleGridUpdate(test_rect)
        
        test_path = ['Q', 'S']
        handler.HandlePathUpdate(test_path)
        
        test_error = "测试错误"
        handler.HandleError(test_error)
        
        # 验证事件处理器被调用
        grid_handler.assert_called_once_with(test_rect)
        path_handler.assert_called_once_with(test_path)
        error_handler.assert_called_once_with(test_error)
    
    def test_style_consistency(self, ui_components):
        """测试样式一致性"""
        renderer = ui_components['renderer']
        indicator = ui_components['indicator']
        
        # 设置一致的颜色主题
        primary_color = "#00FF00"
        text_color = "#FFFFFF"
        error_color = "#FF0000"
        
        # 配置renderer样式
        renderer.SetGridColor(primary_color)
        renderer.SetKeyColor(text_color)
        
        # 配置indicator样式
        indicator.SetTextColor(text_color)
        indicator.SetErrorColor(error_color)
        
        # 验证样式设置
        assert renderer._gridColor.name() == primary_color
        assert renderer._keyColor.name() == text_color
        assert indicator._textColor.name() == text_color
        assert indicator._errorColor.name() == error_color
    
    def test_memory_cleanup(self, ui_components):
        """测试内存清理"""
        overlay = ui_components['overlay']
        indicator = ui_components['indicator']
        handler = ui_components['handler']
        
        # 设置一些状态
        indicator.SetActive(True)
        indicator.UpdatePath(['Q', 'W', 'E', 'A', 'S'])
        
        # 注册一些事件处理器
        dummy_handlers = [Mock() for _ in range(10)]
        for i, dummy_handler in enumerate(dummy_handlers):
            event_type = list(UIEventType)[i % len(UIEventType)]
            handler.RegisterEventHandler(event_type, dummy_handler)
        
        # 清理操作
        indicator.ClearPath()
        indicator.SetActive(False)
        
        # 注销事件处理器
        for i, dummy_handler in enumerate(dummy_handlers):
            event_type = list(UIEventType)[i % len(UIEventType)]
            handler.UnregisterEventHandler(event_type, dummy_handler)
        
        # 验证清理效果
        assert indicator.KeyPath == []
        assert not indicator.IsActive
        
        # 验证事件处理器已清空
        for event_type in UIEventType:
            assert len(handler._eventHandlers[event_type]) == 0
    
    def test_stress_testing(self, ui_components):
        """测试压力情况"""
        indicator = ui_components['indicator']
        renderer = ui_components['renderer']
        handler = ui_components['handler']
        
        # 快速切换状态
        for i in range(100):
            indicator.SetActive(i % 2 == 0)
            
            if indicator.IsActive:
                key = ['Q', 'W', 'E', 'A', 'S', 'D', 'Z', 'X', 'C'][i % 9]
                indicator.AddKey(key)
                
                row, col = GridRenderer.GetKeyPosition(key)
                renderer.SetActiveCell(row, col)
                
                handler.HandlePathUpdate(indicator.KeyPath)
            
            # 定期清理
            if i % 10 == 9:
                indicator.ClearPath()
                renderer.ClearActiveCell()
        
        # 验证最终状态稳定
        assert not indicator.HasError
        assert renderer._activeCell == (-1, -1)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

#endregion