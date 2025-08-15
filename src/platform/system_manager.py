# -*- coding: utf-8 -*-
"""
系统资源管理器实现
监控系统资源使用情况、管理进程优先级和系统兼容性检查
"""

import os
import sys
import time
import threading
import platform
from typing import Callable, Dict, Optional, Any
import psutil

from .interfaces import (
    ISystemManager, 
    SystemMetrics, 
    SystemResourceError
)


class SystemManager(ISystemManager):
    """系统资源管理器实现"""
    
    def __init__(self):
        #region 私有属性初始化
        self._lock = threading.RLock()
        self._monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._monitor_callback: Optional[Callable[[SystemMetrics], None]] = None
        self._monitor_interval = 1.0  # 监控间隔1秒
        self._process = psutil.Process()
        self._system_info: Optional[Dict] = None
        #endregion
    
    #region 公共方法实现
    
    def GetSystemMetrics(self) -> SystemMetrics:
        """获取系统性能指标"""
        try:
            with self._lock:
                # 获取CPU使用率
                cpu_percent = self._process.cpu_percent()
                
                # 获取内存使用情况
                memory_info = self._process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024  # 转换为MB
                
                # 获取句柄数量 (Windows专用)
                handle_count = 0
                try:
                    if hasattr(self._process, 'num_handles'):
                        handle_count = self._process.num_handles()
                except:
                    pass
                
                # 测量响应时间
                response_time = self._MeasureResponseTime()
                
                return SystemMetrics(
                    CpuUsagePercent=cpu_percent,
                    MemoryUsageMb=memory_mb,
                    HandleCount=handle_count,
                    ResponseTimeMs=response_time
                )
                
        except Exception as e:
            raise SystemResourceError(f"获取系统指标失败: {str(e)}")
    
    def SetProcessPriority(self, priority: str = "normal") -> bool:
        """设置进程优先级"""
        try:
            priority_map = {
                'low': psutil.BELOW_NORMAL_PRIORITY_CLASS if sys.platform == 'win32' else 10,
                'normal': psutil.NORMAL_PRIORITY_CLASS if sys.platform == 'win32' else 0,
                'high': psutil.ABOVE_NORMAL_PRIORITY_CLASS if sys.platform == 'win32' else -10,
                'realtime': psutil.REALTIME_PRIORITY_CLASS if sys.platform == 'win32' else -20
            }
            
            if priority not in priority_map:
                raise SystemResourceError(f"无效的优先级: {priority}")
            
            if sys.platform == 'win32':
                self._process.nice(priority_map[priority])
            else:
                os.nice(priority_map[priority])
            
            return True
            
        except Exception as e:
            raise SystemResourceError(f"设置进程优先级失败: {str(e)}")
    
    def CheckSystemCompatibility(self) -> Dict[str, bool]:
        """检查系统兼容性"""
        try:
            compatibility = {}
            
            # 检查操作系统
            compatibility['windows_supported'] = sys.platform == 'win32'
            compatibility['windows_version_ok'] = self._CheckWindowsVersion()
            
            # 检查Python版本
            py_version = sys.version_info
            compatibility['python_version_ok'] = py_version.major >= 3 and py_version.minor >= 7
            
            # 检查必需的权限
            compatibility['admin_privileges'] = self._CheckAdminPrivileges()
            compatibility['accessibility_permissions'] = self._CheckAccessibilityPermissions()
            
            # 检查依赖库
            compatibility['pynput_available'] = self._CheckLibraryAvailable('pynput')
            compatibility['psutil_available'] = self._CheckLibraryAvailable('psutil')
            compatibility['pyqt6_available'] = self._CheckLibraryAvailable('PyQt6')
            
            # 检查系统资源
            compatibility['sufficient_memory'] = psutil.virtual_memory().available > 100 * 1024 * 1024  # 100MB
            compatibility['cpu_cores_ok'] = psutil.cpu_count() >= 1
            
            return compatibility
            
        except Exception as e:
            return {'error': str(e), 'compatibility_check_failed': True}
    
    def MonitorResourceUsage(self, callback: Callable[[SystemMetrics], None]) -> None:
        """开始监控资源使用情况"""
        try:
            with self._lock:
                if self._monitoring_active:
                    self.StopResourceMonitoring()
                
                self._monitor_callback = callback
                self._monitoring_active = True
                
                self._monitor_thread = threading.Thread(
                    target=self._MonitoringLoop,
                    daemon=True
                )
                self._monitor_thread.start()
                
        except Exception as e:
            raise SystemResourceError(f"启动资源监控失败: {str(e)}")
    
    def StopResourceMonitoring(self) -> None:
        """停止资源监控"""
        with self._lock:
            self._monitoring_active = False
            self._monitor_callback = None
            
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=2.0)
                self._monitor_thread = None
    
    #endregion
    
    #region 私有方法实现
    
    def _MeasureResponseTime(self) -> float:
        """测量系统响应时间"""
        try:
            start_time = time.perf_counter()
            
            # 执行一个简单的系统调用来测量响应时间
            os.getpid()
            
            end_time = time.perf_counter()
            return (end_time - start_time) * 1000  # 转换为毫秒
            
        except:
            return 0.0
    
    def _CheckWindowsVersion(self) -> bool:
        """检查Windows版本是否支持"""
        try:
            if sys.platform != 'win32':
                return False
            
            version = platform.version()
            # 支持Windows 10及以上版本
            version_parts = version.split('.')
            if len(version_parts) >= 3:
                major = int(version_parts[0])
                minor = int(version_parts[1])
                build = int(version_parts[2])
                
                # Windows 10的版本号是10.0.xxxxx
                return major >= 10
            
            return False
            
        except:
            return False
    
    def _CheckAdminPrivileges(self) -> bool:
        """检查是否有管理员权限"""
        try:
            if sys.platform == 'win32':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
                
        except:
            return False
    
    def _CheckAccessibilityPermissions(self) -> bool:
        """检查辅助功能权限"""
        try:
            # 在Windows上，尝试创建一个简单的全局钩子来测试权限
            if sys.platform == 'win32':
                try:
                    from pynput import mouse
                    test_listener = mouse.Listener(on_click=lambda x, y, button, pressed: None)
                    test_listener.start()
                    time.sleep(0.1)
                    test_listener.stop()
                    return True
                except:
                    return False
            else:
                return True  # 非Windows系统假设有权限
                
        except:
            return False
    
    def _CheckLibraryAvailable(self, library_name: str) -> bool:
        """检查库是否可用"""
        try:
            __import__(library_name)
            return True
        except ImportError:
            return False
    
    def _MonitoringLoop(self) -> None:
        """资源监控循环"""
        while self._monitoring_active:
            try:
                metrics = self.GetSystemMetrics()
                
                if self._monitor_callback:
                    try:
                        self._monitor_callback(metrics)
                    except Exception:
                        # 忽略回调异常，继续监控
                        pass
                
                time.sleep(self._monitor_interval)
                
            except Exception:
                # 忽略监控循环异常，继续运行
                time.sleep(self._monitor_interval)
    
    #endregion
    
    #region 扩展功能
    
    def GetDetailedSystemInfo(self) -> Dict[str, Any]:
        """获取详细的系统信息"""
        try:
            if self._system_info is None:
                self._system_info = self._CollectSystemInfo()
            
            return self._system_info.copy()
            
        except Exception as e:
            return {'error': str(e)}
    
    def _CollectSystemInfo(self) -> Dict[str, Any]:
        """收集系统信息"""
        info = {}
        
        try:
            # 基本系统信息
            info['platform'] = platform.platform()
            info['architecture'] = platform.architecture()
            info['processor'] = platform.processor()
            info['python_version'] = platform.python_version()
            
            # 内存信息
            memory = psutil.virtual_memory()
            info['total_memory_gb'] = memory.total / 1024 / 1024 / 1024
            info['available_memory_gb'] = memory.available / 1024 / 1024 / 1024
            
            # CPU信息
            info['cpu_count'] = psutil.cpu_count()
            info['cpu_freq'] = psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            
            # 磁盘信息
            disk = psutil.disk_usage('/')
            info['disk_total_gb'] = disk.total / 1024 / 1024 / 1024
            info['disk_free_gb'] = disk.free / 1024 / 1024 / 1024
            
        except Exception as e:
            info['collection_error'] = str(e)
        
        return info
    
    def SetMonitoringInterval(self, interval_seconds: float) -> None:
        """设置监控间隔"""
        with self._lock:
            self._monitor_interval = max(0.1, min(60.0, interval_seconds))
    
    def GetMonitoringStatus(self) -> Dict[str, Any]:
        """获取监控状态"""
        with self._lock:
            return {
                'is_monitoring': self._monitoring_active,
                'monitor_interval': self._monitor_interval,
                'has_callback': self._monitor_callback is not None,
                'thread_alive': self._monitor_thread.is_alive() if self._monitor_thread else False
            }
    
    def OptimizeForPerformance(self) -> Dict[str, bool]:
        """优化系统性能设置"""
        results = {}
        
        try:
            # 设置高优先级
            results['priority_set'] = self.SetProcessPriority('high')
        except:
            results['priority_set'] = False
        
        try:
            # 禁用垃圾回收的频繁触发
            import gc
            gc.disable()
            results['gc_disabled'] = True
        except:
            results['gc_disabled'] = False
        
        return results
    
    def RestoreDefaultSettings(self) -> Dict[str, bool]:
        """恢复默认系统设置"""
        results = {}
        
        try:
            # 恢复正常优先级
            results['priority_restored'] = self.SetProcessPriority('normal')
        except:
            results['priority_restored'] = False
        
        try:
            # 重新启用垃圾回收
            import gc
            gc.enable()
            results['gc_enabled'] = True
        except:
            results['gc_enabled'] = False
        
        return results
    
    #endregion
    
    #region 资源清理
    
    def __del__(self):
        """析构函数，确保资源清理"""
        try:
            self.StopResourceMonitoring()
        except:
            pass
    
    #endregion