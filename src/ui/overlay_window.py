#region OverlayWindow Implementation
"""
透明叠加层窗口实现
提供全屏透明窗口，支持鼠标穿透和窗口置顶
"""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QColor
import sys
from typing import Optional


class OverlayWindow(QWidget):
    """
    透明叠加层窗口
    
    功能：
    - 全屏透明窗口显示
    - 鼠标穿透到底层应用
    - 窗口置顶显示
    - 生命周期管理
    """
    
    #region Signals
    WindowClosed = pyqtSignal()
    WindowShown = pyqtSignal()
    WindowHidden = pyqtSignal()
    #endregion
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        初始化透明叠加层窗口
        
        Args:
            parent: 父窗口，默认为None
        """
        super().__init__(parent)
        self._isVisible = False
        self._screenRect = QRect()
        self._InitializeWindow()
        self._SetupGeometry()
    
    #region Window Setup
    def _InitializeWindow(self) -> None:
        """
        初始化窗口属性
        """
        # 设置窗口标志：无边框、置顶、工具窗口
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.X11BypassWindowManagerHint
        )
        
        # 设置窗口属性：透明背景、鼠标穿透
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        # 设置窗口标题（调试用）
        self.setWindowTitle("KeyboardClicker Grid Overlay")
    
    def _SetupGeometry(self) -> None:
        """
        设置窗口几何形状和位置
        """
        # 获取主屏幕几何信息
        screen = QApplication.primaryScreen()
        if screen:
            self._screenRect = screen.geometry()
            self.setGeometry(self._screenRect)
    #endregion
    
    #region Public Methods
    def Show(self) -> None:
        """
        显示叠加层窗口
        """
        if not self._isVisible:
            self._SetupGeometry()  # 重新获取屏幕信息
            self.show()
            self.raise_()
            self.activateWindow()
            self._isVisible = True
            self.WindowShown.emit()
    
    def Hide(self) -> None:
        """
        隐藏叠加层窗口
        """
        if self._isVisible:
            self.hide()
            self._isVisible = False
            self.WindowHidden.emit()
    
    def UpdateVisibility(self, isVisible: bool) -> None:
        """
        切换窗口可见性
        
        Args:
            isVisible: 是否可见
        """
        if isVisible:
            self.Show()
        else:
            self.Hide()
    
    def IsVisible(self) -> bool:
        """
        获取窗口可见状态
        
        Returns:
            bool: 窗口是否可见
        """
        return self._isVisible
    
    def GetScreenRect(self) -> QRect:
        """
        获取屏幕矩形区域
        
        Returns:
            QRect: 屏幕矩形
        """
        return self._screenRect
    #endregion
    
    #region Event Handlers
    def paintEvent(self, event) -> None:
        """
        绘制事件处理
        基类实现只绘制透明背景
        子类可以重写此方法来绘制网格等内容
        
        Args:
            event: 绘制事件
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制透明背景
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
    
    def closeEvent(self, event) -> None:
        """
        窗口关闭事件处理
        
        Args:
            event: 关闭事件
        """
        self._isVisible = False
        self.WindowClosed.emit()
        event.accept()
    
    def keyPressEvent(self, event) -> None:
        """
        按键事件处理
        Esc键关闭窗口
        
        Args:
            event: 按键事件
        """
        if event.key() == Qt.Key.Key_Escape:
            self.Hide()
        else:
            super().keyPressEvent(event)
    #endregion
    
    #region Properties
    @property
    def ScreenWidth(self) -> int:
        """屏幕宽度"""
        return self._screenRect.width()
    
    @property 
    def ScreenHeight(self) -> int:
        """屏幕高度"""
        return self._screenRect.height()
    #endregion

#endregion