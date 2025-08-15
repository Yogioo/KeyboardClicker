#region OverlayWindow Tests
"""
OverlayWindow 组件测试
测试透明叠加层窗口的各项功能
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QRect, Qt
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QScreen

# 添加源代码路径
sys.path.insert(0, r'D:\GitProj\KeyboardClicker\src')

from ui.overlay_window import OverlayWindow


class TestOverlayWindow:
    """OverlayWindow 测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """设置QApplication"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
        # 清理
        if hasattr(self, 'window') and self.window:
            self.window.close()
    
    def test_init_window_properties(self):
        """测试窗口初始化属性"""
        self.window = OverlayWindow()
        
        # 测试窗口标志
        flags = self.window.windowFlags()
        assert Qt.WindowType.FramelessWindowHint in flags
        assert Qt.WindowType.WindowStaysOnTopHint in flags
        assert Qt.WindowType.Tool in flags
        
        # 测试窗口属性
        assert self.window.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        assert self.window.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        # 测试初始状态
        assert not self.window.IsVisible()
        assert self.window.windowTitle() == "KeyboardClicker Grid Overlay"
    
    @patch('PyQt6.QtWidgets.QApplication.primaryScreen')
    def test_setup_geometry(self, mock_screen):
        """测试窗口几何设置"""
        # 模拟屏幕
        mock_screen_obj = Mock(spec=QScreen)
        mock_screen_obj.geometry.return_value = QRect(0, 0, 1920, 1080)
        mock_screen.return_value = mock_screen_obj
        
        self.window = OverlayWindow()
        
        # 验证几何设置
        expected_rect = QRect(0, 0, 1920, 1080)
        assert self.window.GetScreenRect() == expected_rect
        assert self.window.ScreenWidth == 1920
        assert self.window.ScreenHeight == 1080
    
    def test_show_hide_functionality(self):
        """测试显示隐藏功能"""
        self.window = OverlayWindow()
        
        # 测试显示
        with patch.object(self.window, 'show') as mock_show, \
             patch.object(self.window, 'raise_') as mock_raise, \
             patch.object(self.window, 'activateWindow') as mock_activate:
            
            self.window.Show()
            
            mock_show.assert_called_once()
            mock_raise.assert_called_once()
            mock_activate.assert_called_once()
            assert self.window.IsVisible()
        
        # 测试隐藏
        with patch.object(self.window, 'hide') as mock_hide:
            self.window.Hide()
            
            mock_hide.assert_called_once()
            assert not self.window.IsVisible()
    
    def test_update_visibility(self):
        """测试可见性切换"""
        self.window = OverlayWindow()
        
        with patch.object(self.window, 'Show') as mock_show, \
             patch.object(self.window, 'Hide') as mock_hide:
            
            # 测试显示
            self.window.UpdateVisibility(True)
            mock_show.assert_called_once()
            
            # 测试隐藏
            self.window.UpdateVisibility(False)
            mock_hide.assert_called_once()
    
    def test_signals_emission(self):
        """测试信号发射"""
        self.window = OverlayWindow()
        
        # 测试WindowShown信号
        with patch.object(self.window.WindowShown, 'emit') as mock_emit:
            with patch.object(self.window, 'show'), \
                 patch.object(self.window, 'raise_'), \
                 patch.object(self.window, 'activateWindow'):
                self.window.Show()
                mock_emit.assert_called_once()
        
        # 测试WindowHidden信号
        with patch.object(self.window.WindowHidden, 'emit') as mock_emit:
            with patch.object(self.window, 'hide'):
                self.window.Hide()
                mock_emit.assert_called_once()
    
    def test_escape_key_handling(self):
        """测试Esc键处理"""
        self.window = OverlayWindow()
        self.window._isVisible = True
        
        # 模拟Esc键事件
        with patch.object(self.window, 'Hide') as mock_hide:
            key_event = Mock()
            key_event.key.return_value = Qt.Key.Key_Escape
            
            self.window.keyPressEvent(key_event)
            mock_hide.assert_called_once()
    
    def test_close_event_handling(self):
        """测试窗口关闭事件"""
        self.window = OverlayWindow()
        self.window._isVisible = True
        
        # 模拟关闭事件
        with patch.object(self.window.WindowClosed, 'emit') as mock_emit:
            close_event = Mock()
            
            self.window.closeEvent(close_event)
            
            assert not self.window.IsVisible()
            mock_emit.assert_called_once()
            close_event.accept.assert_called_once()
    
    def test_paint_event(self):
        """测试绘制事件"""
        self.window = OverlayWindow()
        
        # 模拟绘制事件
        with patch('ui.overlay_window.QPainter') as mock_painter_class:
            mock_painter = Mock()
            mock_painter_class.return_value = mock_painter
            
            paint_event = Mock()
            self.window.paintEvent(paint_event)
            
            # 验证QPainter调用
            mock_painter_class.assert_called_once_with(self.window)
            mock_painter.setRenderHint.assert_called_once()
            mock_painter.fillRect.assert_called_once()
    
    @patch('PyQt6.QtWidgets.QApplication.primaryScreen')
    def test_screen_rect_update(self, mock_screen):
        """测试屏幕矩形更新"""
        # 初始屏幕
        mock_screen_obj = Mock(spec=QScreen)
        mock_screen_obj.geometry.return_value = QRect(0, 0, 1920, 1080)
        mock_screen.return_value = mock_screen_obj
        
        self.window = OverlayWindow()
        initial_rect = self.window.GetScreenRect()
        
        # 更改屏幕尺寸
        mock_screen_obj.geometry.return_value = QRect(0, 0, 2560, 1440)
        
        # 调用Show重新设置几何
        with patch.object(self.window, 'show'), \
             patch.object(self.window, 'raise_'), \
             patch.object(self.window, 'activateWindow'):
            self.window.Show()
        
        updated_rect = self.window.GetScreenRect()
        assert updated_rect != initial_rect
        assert updated_rect.width() == 2560
        assert updated_rect.height() == 1440
    
    def test_multiple_show_hide_cycles(self):
        """测试多次显示隐藏循环"""
        self.window = OverlayWindow()
        
        for i in range(5):
            with patch.object(self.window, 'show'), \
                 patch.object(self.window, 'raise_'), \
                 patch.object(self.window, 'activateWindow'):
                self.window.Show()
                assert self.window.IsVisible()
            
            with patch.object(self.window, 'hide'):
                self.window.Hide()
                assert not self.window.IsVisible()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

#endregion