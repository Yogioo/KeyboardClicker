#region EventHandler Tests
"""
EventHandler 组件测试
测试UI事件处理器的各项功能
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtCore import QObject, QTimer

# 添加源代码路径
sys.path.insert(0, r'D:\GitProj\KeyboardClicker\src')

from ui.event_handler import EventHandler, UIEventType


class TestEventHandler:
    """EventHandler 测试类"""
    
    @pytest.fixture
    def event_handler(self):
        """创建EventHandler实例"""
        return EventHandler()
    
    def test_init_default_values(self, event_handler):
        """测试初始化默认值"""
        assert not event_handler._isProcessing
        assert event_handler._lastError == ""
        assert event_handler._confirmationTimeout == 2000
        assert isinstance(event_handler._confirmationTimer, QTimer)
        
        # 测试事件处理器字典初始化
        for event_type in UIEventType:
            assert event_type in event_handler._eventHandlers
            assert event_handler._eventHandlers[event_type] == []
    
    def test_register_event_handler(self, event_handler):
        """测试注册事件处理器"""
        mock_handler = Mock()
        
        # 注册处理器
        event_handler.RegisterEventHandler(UIEventType.GRID_UPDATE, mock_handler)
        
        # 验证处理器已注册
        assert mock_handler in event_handler._eventHandlers[UIEventType.GRID_UPDATE]
        
        # 重复注册同一个处理器（不应该重复添加）
        event_handler.RegisterEventHandler(UIEventType.GRID_UPDATE, mock_handler)
        assert event_handler._eventHandlers[UIEventType.GRID_UPDATE].count(mock_handler) == 1
    
    def test_unregister_event_handler(self, event_handler):
        """测试注销事件处理器"""
        mock_handler = Mock()
        
        # 先注册
        event_handler.RegisterEventHandler(UIEventType.PATH_UPDATE, mock_handler)
        assert mock_handler in event_handler._eventHandlers[UIEventType.PATH_UPDATE]
        
        # 注销
        event_handler.UnregisterEventHandler(UIEventType.PATH_UPDATE, mock_handler)
        assert mock_handler not in event_handler._eventHandlers[UIEventType.PATH_UPDATE]
        
        # 注销不存在的处理器（不应该出错）
        event_handler.UnregisterEventHandler(UIEventType.PATH_UPDATE, mock_handler)
    
    def test_emit_event_calls_handlers(self, event_handler):
        """测试发射事件调用处理器"""
        mock_handler1 = Mock()
        mock_handler2 = Mock()
        
        # 注册处理器
        event_handler.RegisterEventHandler(UIEventType.STATE_CHANGE, mock_handler1)
        event_handler.RegisterEventHandler(UIEventType.STATE_CHANGE, mock_handler2)
        
        # 发射事件
        test_args = ("test_state", True)
        event_handler.EmitEvent(UIEventType.STATE_CHANGE, *test_args)
        
        # 验证处理器被调用
        mock_handler1.assert_called_once_with(*test_args)
        mock_handler2.assert_called_once_with(*test_args)
    
    def test_emit_event_handler_error(self, event_handler):
        """测试事件处理器错误处理"""
        # 创建会抛出异常的处理器
        def error_handler(*args):
            raise ValueError("测试错误")
        
        mock_handler = Mock()
        
        # 注册处理器
        event_handler.RegisterEventHandler(UIEventType.ERROR_OCCURRED, error_handler)
        event_handler.RegisterEventHandler(UIEventType.ERROR_OCCURRED, mock_handler)
        
        # 发射事件（不应该因为第一个处理器出错而影响第二个）
        with patch('builtins.print'):  # 抑制错误输出
            event_handler.EmitEvent(UIEventType.ERROR_OCCURRED, "test error")
        
        # 正常的处理器仍应被调用
        mock_handler.assert_called_once_with("test error")
    
    def test_emit_qt_signals(self, event_handler):
        """测试Qt信号发射"""
        with patch.object(event_handler.GridUpdateRequested, 'emit') as mock_grid, \
             patch.object(event_handler.PathUpdateRequested, 'emit') as mock_path, \
             patch.object(event_handler.StateChangeRequested, 'emit') as mock_state, \
             patch.object(event_handler.ErrorDisplayRequested, 'emit') as mock_error, \
             patch.object(event_handler.ActionConfirmed, 'emit') as mock_confirmed, \
             patch.object(event_handler.ActionCancelled, 'emit') as mock_cancelled:
            
            # 测试各种事件的信号发射
            test_rect = Mock()
            event_handler.EmitEvent(UIEventType.GRID_UPDATE, test_rect)
            mock_grid.assert_called_once_with(test_rect)
            
            test_path = ['Q', 'W']
            event_handler.EmitEvent(UIEventType.PATH_UPDATE, test_path)
            mock_path.assert_called_once_with(test_path)
            
            event_handler.EmitEvent(UIEventType.STATE_CHANGE, "test", True)
            mock_state.assert_called_once_with("test", True)
            
            event_handler.EmitEvent(UIEventType.ERROR_OCCURRED, "error")
            mock_error.assert_called_once_with("error")
            
            event_handler.EmitEvent(UIEventType.ACTION_CONFIRMED, "action")
            mock_confirmed.assert_called_once_with("action")
            
            event_handler.EmitEvent(UIEventType.ACTION_CANCELLED)
            mock_cancelled.assert_called_once()
    
    def test_handle_grid_update(self, event_handler):
        """测试网格更新处理"""
        with patch.object(event_handler, 'EmitEvent') as mock_emit:
            test_rect = Mock()
            event_handler.HandleGridUpdate(test_rect)
            
            mock_emit.assert_called_once_with(UIEventType.GRID_UPDATE, test_rect)
    
    def test_handle_path_update(self, event_handler):
        """测试路径更新处理"""
        with patch.object(event_handler, 'EmitEvent') as mock_emit:
            test_sequence = ['Q', 'W', 'E']
            event_handler.HandlePathUpdate(test_sequence)
            
            mock_emit.assert_called_once_with(UIEventType.PATH_UPDATE, test_sequence)
    
    def test_handle_state_change(self, event_handler):
        """测试状态变化处理"""
        with patch.object(event_handler, 'EmitEvent') as mock_emit:
            event_handler.HandleStateChange("active", True)
            
            mock_emit.assert_called_once_with(UIEventType.STATE_CHANGE, "active", True)
    
    def test_handle_error(self, event_handler):
        """测试错误处理"""
        with patch.object(event_handler, 'EmitEvent') as mock_emit:
            error_msg = "测试错误消息"
            event_handler.HandleError(error_msg)
            
            assert event_handler._lastError == error_msg
            mock_emit.assert_called_once_with(UIEventType.ERROR_OCCURRED, error_msg)
    
    def test_handle_action_confirmation(self, event_handler):
        """测试操作确认处理"""
        with patch.object(event_handler, 'EmitEvent') as mock_emit, \
             patch.object(event_handler, '_StartConfirmationTimer') as mock_timer:
            
            action = "测试操作"
            event_handler.HandleActionConfirmation(action)
            
            mock_emit.assert_called_once_with(UIEventType.ACTION_CONFIRMED, action)
            mock_timer.assert_called_once()
    
    def test_handle_action_cancellation(self, event_handler):
        """测试操作取消处理"""
        with patch.object(event_handler, 'EmitEvent') as mock_emit:
            event_handler.HandleActionCancellation()
            
            mock_emit.assert_called_once_with(UIEventType.ACTION_CANCELLED)
    
    def test_user_feedback_methods(self, event_handler):
        """测试用户反馈方法"""
        with patch.object(event_handler, 'HandleActionConfirmation') as mock_confirm, \
             patch.object(event_handler, 'HandleError') as mock_error, \
             patch.object(event_handler, 'HandleActionCancellation') as mock_cancel:
            
            # 测试操作确认
            event_handler.ShowOperationConfirmation("test_op")
            mock_confirm.assert_called_once_with("已执行: test_op")
            
            # 测试错误警告
            event_handler.ShowErrorWarning("test_error")
            mock_error.assert_called_once_with("test_error")
            
            # 测试取消通知
            event_handler.ShowCancellationNotice()
            mock_cancel.assert_called_once()
    
    def test_set_processing_state(self, event_handler):
        """测试处理状态设置"""
        with patch.object(event_handler, 'HandleStateChange') as mock_state:
            # 设置处理中
            event_handler.SetProcessingState(True)
            assert event_handler._isProcessing
            mock_state.assert_called_with("processing", True)
            
            # 设置非处理中
            event_handler.SetProcessingState(False)
            assert not event_handler._isProcessing
            mock_state.assert_called_with("processing", False)
    
    def test_properties(self, event_handler):
        """测试属性访问"""
        # 测试IsProcessing属性
        event_handler._isProcessing = True
        assert event_handler.IsProcessing
        
        event_handler._isProcessing = False
        assert not event_handler.IsProcessing
        
        # 测试LastError属性
        test_error = "测试错误"
        event_handler._lastError = test_error
        assert event_handler.LastError == test_error
    
    def test_confirmation_timer(self, event_handler):
        """测试确认定时器"""
        # 测试启动定时器
        with patch.object(event_handler._confirmationTimer, 'start') as mock_start:
            event_handler._StartConfirmationTimer()
            mock_start.assert_called_once_with(2000)
        
        # 测试超时处理（应该不抛出异常）
        event_handler._OnConfirmationTimeout()
    
    def test_signal_handlers_default_behavior(self, event_handler):
        """测试默认信号处理器行为"""
        # 这些方法应该能正常调用而不抛出异常
        event_handler._OnGridUpdateRequested(Mock())
        event_handler._OnPathUpdateRequested(['Q'])
        event_handler._OnStateChangeRequested("test", True)
        
        # 测试错误显示处理调用动画
        with patch.object(event_handler, 'TriggerErrorAnimation') as mock_error_anim:
            event_handler._OnErrorDisplayRequested("error")
            mock_error_anim.assert_called_once()
        
        # 测试操作确认处理调用动画
        with patch.object(event_handler, 'TriggerSuccessAnimation') as mock_success_anim:
            event_handler._OnActionConfirmed("action")
            mock_success_anim.assert_called_once()
        
        # 测试操作取消处理调用动画
        with patch.object(event_handler, 'TriggerCancellationAnimation') as mock_cancel_anim:
            event_handler._OnActionCancelled()
            mock_cancel_anim.assert_called_once()
    
    def test_animation_methods(self, event_handler):
        """测试动画方法"""
        # 这些方法目前是空实现，应该能正常调用
        event_handler.TriggerSuccessAnimation()
        event_handler.TriggerErrorAnimation()
        event_handler.TriggerCancellationAnimation()
        event_handler.ShowImmediateFeedback("test")
    
    def test_multiple_handlers_same_event(self, event_handler):
        """测试同一事件的多个处理器"""
        handlers = [Mock() for _ in range(5)]
        
        # 注册多个处理器
        for handler in handlers:
            event_handler.RegisterEventHandler(UIEventType.GRID_UPDATE, handler)
        
        # 发射事件
        test_rect = Mock()
        event_handler.EmitEvent(UIEventType.GRID_UPDATE, test_rect)
        
        # 验证所有处理器都被调用
        for handler in handlers:
            handler.assert_called_once_with(test_rect)
    
    def test_event_with_kwargs(self, event_handler):
        """测试带关键字参数的事件"""
        mock_handler = Mock()
        event_handler.RegisterEventHandler(UIEventType.STATE_CHANGE, mock_handler)
        
        # 发射带关键字参数的事件
        event_handler.EmitEvent(UIEventType.STATE_CHANGE, "test", active=True)
        
        # 验证处理器被正确调用
        mock_handler.assert_called_once_with("test", active=True)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

#endregion