# -*- coding: utf-8 -*-
"""
屏幕管理器实现
处理屏幕坐标系统、DPI缩放和多显示器支持
"""

import ctypes
import ctypes.wintypes
from typing import Tuple, Dict, List, Optional
import threading

from .interfaces import IScreenManager, SystemResourceError


class ScreenManager(IScreenManager):
    """屏幕管理器实现"""
    
    def __init__(self):
        #region 私有属性初始化
        self._lock = threading.RLock()
        self._cached_screen_info: Optional[Dict] = None
        self._cache_timeout = 1.0  # 缓存1秒
        self._last_cache_time = 0
        
        # Windows API常量
        self._SM_CXSCREEN = 0
        self._SM_CYSCREEN = 1
        self._SM_XVIRTUALSCREEN = 76
        self._SM_YVIRTUALSCREEN = 77
        self._SM_CXVIRTUALSCREEN = 78
        self._SM_CYVIRTUALSCREEN = 79
        #endregion
    
    #region 公共方法实现
    
    def GetPrimaryScreenRect(self) -> Tuple[int, int, int, int]:
        """获取主显示器矩形 (x, y, width, height)"""
        try:
            with self._lock:
                screen_info = self._GetCachedScreenInfo()
                return screen_info['primary_screen']
                
        except Exception as e:
            raise SystemResourceError(f"获取主显示器信息失败: {str(e)}")
    
    def GetScreenDpi(self) -> float:
        """获取屏幕DPI缩放比例"""
        try:
            with self._lock:
                screen_info = self._GetCachedScreenInfo()
                return screen_info['dpi_scale']
                
        except Exception as e:
            raise SystemResourceError(f"获取DPI信息失败: {str(e)}")
    
    def ValidateCoordinates(self, x: int, y: int) -> bool:
        """验证坐标是否在屏幕范围内"""
        try:
            screen_info = self._GetCachedScreenInfo()
            virtual_screen = screen_info['virtual_screen']
            
            return (virtual_screen[0] <= x < virtual_screen[0] + virtual_screen[2] and
                    virtual_screen[1] <= y < virtual_screen[1] + virtual_screen[3])
                    
        except Exception:
            # 如果获取屏幕信息失败，使用基本范围检查
            return -100 <= x <= 8192 and -100 <= y <= 8192
    
    def ScreenToClient(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """屏幕坐标转换为客户端坐标"""
        try:
            # 对于全屏应用，屏幕坐标就是客户端坐标
            # 这里可以根据需要实现更复杂的转换逻辑
            dpi_scale = self.GetScreenDpi()
            
            client_x = int(screen_x / dpi_scale)
            client_y = int(screen_y / dpi_scale)
            
            return (client_x, client_y)
            
        except Exception as e:
            # 如果转换失败，返回原始坐标
            return (screen_x, screen_y)
    
    #endregion
    
    #region 私有方法实现
    
    def _GetCachedScreenInfo(self) -> Dict:
        """获取缓存的屏幕信息"""
        import time
        current_time = time.time()
        
        if (self._cached_screen_info is None or 
            current_time - self._last_cache_time > self._cache_timeout):
            
            self._cached_screen_info = self._RefreshScreenInfo()
            self._last_cache_time = current_time
        
        return self._cached_screen_info
    
    def _RefreshScreenInfo(self) -> Dict:
        """刷新屏幕信息"""
        try:
            # 获取主显示器信息
            primary_width = ctypes.windll.user32.GetSystemMetrics(self._SM_CXSCREEN)
            primary_height = ctypes.windll.user32.GetSystemMetrics(self._SM_CYSCREEN)
            
            # 获取虚拟屏幕信息 (多显示器)
            virtual_x = ctypes.windll.user32.GetSystemMetrics(self._SM_XVIRTUALSCREEN)
            virtual_y = ctypes.windll.user32.GetSystemMetrics(self._SM_YVIRTUALSCREEN)
            virtual_width = ctypes.windll.user32.GetSystemMetrics(self._SM_CXVIRTUALSCREEN)
            virtual_height = ctypes.windll.user32.GetSystemMetrics(self._SM_CYVIRTUALSCREEN)
            
            # 获取DPI信息
            dpi_scale = self._GetDpiScale()
            
            return {
                'primary_screen': (0, 0, primary_width, primary_height),
                'virtual_screen': (virtual_x, virtual_y, virtual_width, virtual_height),
                'dpi_scale': dpi_scale,
                'refresh_time': time.time()
            }
            
        except Exception as e:
            # 返回默认值
            return {
                'primary_screen': (0, 0, 1920, 1080),
                'virtual_screen': (0, 0, 1920, 1080),
                'dpi_scale': 1.0,
                'refresh_time': time.time(),
                'error': str(e)
            }
    
    def _GetDpiScale(self) -> float:
        """获取DPI缩放比例"""
        try:
            # 尝试使用Windows 10+ API
            try:
                import ctypes.wintypes
                shcore = ctypes.windll.shcore
                shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE
                
                # 获取主显示器DPI
                hdc = ctypes.windll.user32.GetDC(0)
                dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
                ctypes.windll.user32.ReleaseDC(0, hdc)
                
                return dpi / 96.0  # 96 DPI是100%缩放
                
            except:
                # 回退到基本DPI检测
                hdc = ctypes.windll.user32.GetDC(0)
                dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
                ctypes.windll.user32.ReleaseDC(0, hdc)
                
                return dpi / 96.0
                
        except:
            # 如果所有方法都失败，返回1.0 (100%缩放)
            return 1.0
    
    #endregion
    
    #region 扩展功能
    
    def GetAllScreens(self) -> List[Tuple[int, int, int, int]]:
        """获取所有显示器信息"""
        try:
            screens = []
            
            def enum_proc(hMonitor, hdcMonitor, lprcMonitor, dwData):
                """枚举显示器回调函数"""
                rect = lprcMonitor.contents
                screens.append((rect.left, rect.top, 
                              rect.right - rect.left, 
                              rect.bottom - rect.top))
                return True
            
            # 定义回调函数类型
            EnumDisplayMonitorsProc = ctypes.WINFUNCTYPE(
                ctypes.wintypes.BOOL,
                ctypes.wintypes.HMONITOR,
                ctypes.wintypes.HDC,
                ctypes.POINTER(ctypes.wintypes.RECT),
                ctypes.wintypes.LPARAM
            )
            
            # 枚举所有显示器
            ctypes.windll.user32.EnumDisplayMonitors(
                None, None, EnumDisplayMonitorsProc(enum_proc), 0
            )
            
            return screens if screens else [self.GetPrimaryScreenRect()]
            
        except Exception:
            # 如果枚举失败，返回主显示器
            return [self.GetPrimaryScreenRect()]
    
    def GetScreenAtPoint(self, x: int, y: int) -> Optional[Tuple[int, int, int, int]]:
        """获取指定点所在的显示器"""
        try:
            all_screens = self.GetAllScreens()
            
            for screen in all_screens:
                sx, sy, sw, sh = screen
                if sx <= x < sx + sw and sy <= y < sy + sh:
                    return screen
            
            return None
            
        except Exception:
            return None
    
    def ClampToScreen(self, x: int, y: int, screen_rect: Optional[Tuple[int, int, int, int]] = None) -> Tuple[int, int]:
        """将坐标限制在指定屏幕范围内"""
        if screen_rect is None:
            screen_rect = self.GetPrimaryScreenRect()
        
        sx, sy, sw, sh = screen_rect
        clamped_x = max(sx, min(x, sx + sw - 1))
        clamped_y = max(sy, min(y, sy + sh - 1))
        
        return (clamped_x, clamped_y)
    
    def GetScreenWorkArea(self, screen_rect: Optional[Tuple[int, int, int, int]] = None) -> Tuple[int, int, int, int]:
        """获取屏幕工作区域 (排除任务栏等)"""
        try:
            if screen_rect is None:
                # 获取主显示器工作区
                rect = ctypes.wintypes.RECT()
                ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0)  # SPI_GETWORKAREA
                return (rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)
            else:
                # 对于指定屏幕，简单返回屏幕矩形 (可以改进)
                return screen_rect
                
        except Exception:
            # 如果获取失败，返回主显示器矩形
            return self.GetPrimaryScreenRect()
    
    #endregion
    
    #region 状态和调试
    
    def GetScreenInfo(self) -> Dict:
        """获取详细的屏幕信息"""
        try:
            with self._lock:
                screen_info = self._GetCachedScreenInfo()
                all_screens = self.GetAllScreens()
                work_area = self.GetScreenWorkArea()
                
                return {
                    **screen_info,
                    'all_screens': all_screens,
                    'work_area': work_area,
                    'screen_count': len(all_screens)
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    def InvalidateCache(self) -> None:
        """强制刷新缓存"""
        with self._lock:
            self._cached_screen_info = None
            self._last_cache_time = 0
    
    #endregion