# -*- coding: utf-8 -*-
"""
性能配置模块
定义平台模块的性能优化参数和配置
"""

from dataclasses import dataclass
from typing import Dict, Any
import os


@dataclass
class PerformanceConfig:
    """性能配置数据结构"""
    
    #region 热键响应优化
    hotkey_debounce_ms: float = 100.0  # 热键防抖间隔
    hotkey_max_retries: int = 3         # 热键注册最大重试次数
    hotkey_retry_delay_ms: float = 50.0 # 热键重试延迟
    #endregion
    
    #region 键盘监听优化
    keyboard_debounce_ms: float = 50.0   # 键盘防抖间隔
    keyboard_queue_size: int = 100       # 键盘事件队列大小
    keyboard_thread_priority: str = "normal"  # 监听线程优先级
    #endregion
    
    #region 鼠标操作优化
    mouse_operation_interval_ms: float = 10.0  # 鼠标操作间隔
    mouse_smooth_steps: int = 20               # 平滑移动步数
    mouse_operation_timeout_ms: float = 1000.0 # 鼠标操作超时
    mouse_validation_enabled: bool = True      # 启用坐标验证
    #endregion
    
    #region 系统监控优化
    system_monitor_interval_s: float = 1.0     # 系统监控间隔
    system_cache_timeout_s: float = 1.0        # 系统信息缓存超时
    system_metrics_history_size: int = 60      # 性能指标历史记录数量
    #endregion
    
    #region 错误恢复优化
    error_recovery_enabled: bool = True        # 启用错误恢复
    operation_timeout_s: float = 5.0           # 操作超时时间
    max_recovery_attempts: int = 3             # 最大恢复尝试次数
    recovery_delay_base_ms: float = 100.0      # 恢复延迟基数
    #endregion
    
    #region 内存优化
    enable_gc_optimization: bool = True        # 启用垃圾回收优化
    cache_cleanup_interval_s: float = 300.0    # 缓存清理间隔
    max_memory_usage_mb: float = 100.0         # 最大内存使用量
    #endregion
    
    #region CPU优化
    cpu_affinity_enabled: bool = False         # 启用CPU亲和性
    process_priority: str = "high"             # 进程优先级
    thread_pool_size: int = 4                  # 线程池大小
    #endregion


class PerformanceProfileManager:
    """性能配置管理器"""
    
    def __init__(self):
        self._profiles: Dict[str, PerformanceConfig] = {}
        self._current_profile = "default"
        self._InitializeProfiles()
    
    #region 配置文件管理
    
    def _InitializeProfiles(self) -> None:
        """初始化预定义的性能配置文件"""
        
        # 默认配置 - 平衡性能和兼容性
        self._profiles["default"] = PerformanceConfig()
        
        # 高性能配置 - 最大化响应速度
        self._profiles["high_performance"] = PerformanceConfig(
            hotkey_debounce_ms=50.0,
            keyboard_debounce_ms=25.0,
            mouse_operation_interval_ms=5.0,
            mouse_smooth_steps=15,
            system_monitor_interval_s=0.5,
            process_priority="realtime",
            enable_gc_optimization=True,
            cpu_affinity_enabled=True
        )
        
        # 低资源配置 - 最小化资源占用
        self._profiles["low_resource"] = PerformanceConfig(
            hotkey_debounce_ms=200.0,
            keyboard_debounce_ms=100.0,
            mouse_operation_interval_ms=20.0,
            mouse_smooth_steps=10,
            system_monitor_interval_s=2.0,
            process_priority="normal",
            enable_gc_optimization=False,
            max_memory_usage_mb=50.0,
            thread_pool_size=2
        )
        
        # 兼容性配置 - 最大化兼容性
        self._profiles["compatibility"] = PerformanceConfig(
            hotkey_debounce_ms=150.0,
            keyboard_debounce_ms=75.0,
            mouse_operation_interval_ms=15.0,
            mouse_operation_timeout_ms=2000.0,
            system_monitor_interval_s=1.5,
            error_recovery_enabled=True,
            max_recovery_attempts=5,
            mouse_validation_enabled=True
        )
    
    def GetProfile(self, profile_name: str) -> PerformanceConfig:
        """获取指定的性能配置"""
        if profile_name not in self._profiles:
            raise ValueError(f"未知的性能配置文件: {profile_name}")
        return self._profiles[profile_name]
    
    def SetCurrentProfile(self, profile_name: str) -> None:
        """设置当前使用的性能配置"""
        if profile_name not in self._profiles:
            raise ValueError(f"未知的性能配置文件: {profile_name}")
        self._current_profile = profile_name
    
    def GetCurrentProfile(self) -> PerformanceConfig:
        """获取当前的性能配置"""
        return self._profiles[self._current_profile]
    
    def GetAvailableProfiles(self) -> list:
        """获取可用的配置文件列表"""
        return list(self._profiles.keys())
    
    #endregion
    
    #region 动态配置调整
    
    def CreateCustomProfile(self, name: str, base_profile: str = "default", **overrides) -> None:
        """创建自定义性能配置"""
        if base_profile not in self._profiles:
            raise ValueError(f"基础配置文件不存在: {base_profile}")
        
        base_config = self._profiles[base_profile]
        custom_config = PerformanceConfig(**{
            **base_config.__dict__,
            **overrides
        })
        
        self._profiles[name] = custom_config
    
    def UpdateCurrentProfile(self, **updates) -> None:
        """更新当前配置文件的参数"""
        current_config = self._profiles[self._current_profile]
        for key, value in updates.items():
            if hasattr(current_config, key):
                setattr(current_config, key, value)
            else:
                raise ValueError(f"未知的配置参数: {key}")
    
    def ResetToDefault(self) -> None:
        """重置为默认配置"""
        self._current_profile = "default"
    
    #endregion
    
    #region 自动优化
    
    def AutoOptimizeForSystem(self) -> str:
        """根据系统条件自动选择最佳配置"""
        try:
            import psutil
            
            # 获取系统信息
            memory_gb = psutil.virtual_memory().total / 1024 / 1024 / 1024
            cpu_count = psutil.cpu_count()
            
            # 根据系统配置选择性能文件
            if memory_gb >= 8 and cpu_count >= 4:
                profile = "high_performance"
            elif memory_gb >= 4 and cpu_count >= 2:
                profile = "default"
            else:
                profile = "low_resource"
            
            self.SetCurrentProfile(profile)
            return profile
            
        except Exception:
            # 如果自动检测失败，使用默认配置
            self.SetCurrentProfile("default")
            return "default"
    
    def OptimizeForUsage(self, usage_pattern: str) -> str:
        """根据使用模式优化配置"""
        patterns = {
            "gaming": "high_performance",
            "office": "default", 
            "presentation": "compatibility",
            "background": "low_resource"
        }
        
        profile = patterns.get(usage_pattern, "default")
        self.SetCurrentProfile(profile)
        return profile
    
    #endregion
    
    #region 配置持久化
    
    def SaveToFile(self, file_path: str) -> None:
        """保存配置到文件"""
        import json
        
        config_data = {
            "current_profile": self._current_profile,
            "profiles": {
                name: config.__dict__ 
                for name, config in self._profiles.items()
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def LoadFromFile(self, file_path: str) -> None:
        """从文件加载配置"""
        import json
        
        if not os.path.exists(file_path):
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 重建配置对象
            for name, profile_dict in config_data.get("profiles", {}).items():
                self._profiles[name] = PerformanceConfig(**profile_dict)
            
            # 设置当前配置
            current = config_data.get("current_profile", "default")
            if current in self._profiles:
                self._current_profile = current
                
        except Exception:
            # 如果加载失败，保持默认配置
            pass
    
    #endregion


#region 全局配置实例

# 全局性能配置管理器
performance_manager = PerformanceProfileManager()

def GetCurrentConfig() -> PerformanceConfig:
    """获取当前性能配置"""
    return performance_manager.GetCurrentProfile()

def SetPerformanceProfile(profile_name: str) -> None:
    """设置性能配置文件"""
    performance_manager.SetCurrentProfile(profile_name)

def AutoOptimize() -> str:
    """自动优化性能配置"""
    return performance_manager.AutoOptimizeForSystem()

#endregion