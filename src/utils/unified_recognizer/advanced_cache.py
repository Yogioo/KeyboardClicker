#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级缓存系统
实现智能缓存策略，提高识别性能
"""

import cv2
import numpy as np
import time
import hashlib
import threading
from typing import Dict, List, Any, Optional, Tuple
from collections import OrderedDict
import logging
import psutil
import gc

class CacheStats:
    """缓存统计信息"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.memory_usage = 0
        self.access_count = 0
        self.last_reset = time.time()
        self._lock = threading.Lock()
    
    def record_hit(self):
        """记录缓存命中"""
        with self._lock:
            self.hits += 1
            self.access_count += 1
    
    def record_miss(self):
        """记录缓存未命中"""
        with self._lock:
            self.misses += 1
            self.access_count += 1
    
    def record_eviction(self):
        """记录缓存淘汰"""
        with self._lock:
            self.evictions += 1
    
    def update_memory_usage(self, size: int):
        """更新内存使用量"""
        with self._lock:
            self.memory_usage = size
    
    def get_hit_rate(self) -> float:
        """获取命中率"""
        with self._lock:
            if self.access_count == 0:
                return 0.0
            return self.hits / self.access_count
    
    def reset(self):
        """重置统计"""
        with self._lock:
            self.hits = 0
            self.misses = 0
            self.evictions = 0
            self.access_count = 0
            self.last_reset = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        with self._lock:
            return {
                'hits': self.hits,
                'misses': self.misses,
                'evictions': self.evictions,
                'hit_rate': self.get_hit_rate(),
                'memory_usage_mb': self.memory_usage / (1024 * 1024),
                'access_count': self.access_count,
                'uptime_seconds': time.time() - self.last_reset
            }

class CacheEntry:
    """缓存条目"""
    
    def __init__(self, key: str, value: Any, size: int = 0):
        self.key = key
        self.value = value
        self.size = size
        self.access_count = 1
        self.last_access = time.time()
        self.created_time = time.time()
    
    def access(self):
        """记录访问"""
        self.access_count += 1
        self.last_access = time.time()
    
    def get_age(self) -> float:
        """获取条目年龄（秒）"""
        return time.time() - self.created_time
    
    def get_idle_time(self) -> float:
        """获取空闲时间（秒）"""
        return time.time() - self.last_access

class AdvancedCache:
    """高级缓存系统"""
    
    def __init__(self, 
                 max_size: int = 100,
                 max_memory_mb: int = 512,
                 ttl_seconds: int = 3600,
                 enable_memory_monitoring: bool = True):
        """
        初始化高级缓存
        
        Args:
            max_size: 最大缓存条目数
            max_memory_mb: 最大内存使用量（MB）
            ttl_seconds: 缓存生存时间（秒）
            enable_memory_monitoring: 是否启用内存监控
        """
        self._max_size = max_size
        self._max_memory = max_memory_mb * 1024 * 1024  # 转换为字节
        self._ttl = ttl_seconds
        self._enable_memory_monitoring = enable_memory_monitoring
        
        # 使用OrderedDict实现LRU
        self._pyramid_cache = OrderedDict()
        self._feature_cache = OrderedDict()
        self._result_cache = OrderedDict()
        
        # 统计信息
        self._pyramid_stats = CacheStats()
        self._feature_stats = CacheStats()
        self._result_stats = CacheStats()
        
        # 内存监控
        self._current_memory = 0
        
        self._logger = logging.getLogger(__name__)
    
    def _calculate_size(self, obj: Any, visited: set = None) -> int:
        """估算对象大小（防止循环引用）"""
        if visited is None:
            visited = set()
        
        # 防止循环引用
        obj_id = id(obj)
        if obj_id in visited:
            return 0
        visited.add(obj_id)
        
        try:
            if isinstance(obj, np.ndarray):
                return obj.nbytes
            elif isinstance(obj, list):
                return sum(self._calculate_size(item, visited) for item in obj)
            elif isinstance(obj, dict):
                # 对于字典，只计算值的大小，键使用简单估算
                return sum(len(str(k)) * 4 + self._calculate_size(v, visited) for k, v in obj.items())
            else:
                # 对于其他类型，使用粗略估算
                return len(str(obj)) * 4
        except Exception:
            # 如果计算失败，返回默认大小
            return 1024
        finally:
            visited.discard(obj_id)
    
    def _get_image_hash(self, image: np.ndarray) -> str:
        """计算图像哈希值（优化版）"""
        # 使用更高效的哈希算法
        if image.size > 1024 * 1024:  # 大于1MB的图像
            # 对大图像进行采样
            h, w = image.shape[:2]
            step_h, step_w = max(1, h // 64), max(1, w // 64)
            sample = image[::step_h, ::step_w]
        else:
            sample = image
        
        # 转换为灰度图
        if len(sample.shape) == 3:
            sample = cv2.cvtColor(sample, cv2.COLOR_BGR2GRAY)
        
        # 使用更快的哈希算法
        return hashlib.blake2b(sample.tobytes(), digest_size=16).hexdigest()
    

    
    # 金字塔缓存方法
    def get_cached_pyramid(self, image: np.ndarray) -> Optional[List[np.ndarray]]:
        """获取缓存的金字塔"""
        try:
            image_hash = self._get_image_hash(image)
            
            if image_hash in self._pyramid_cache:
                entry = self._pyramid_cache[image_hash]
                entry.access()
                # 移动到末尾（LRU）
                self._pyramid_cache.move_to_end(image_hash)
                self._pyramid_stats.record_hit()
                return entry.value
            
            self._pyramid_stats.record_miss()
            return None
        except Exception as e:
            self._logger.error(f"获取金字塔缓存出错: {e}")
            return None
    
    def cache_pyramid(self, image: np.ndarray, pyramid: List[np.ndarray]):
        """缓存金字塔"""
        try:
            image_hash = self._get_image_hash(image)
            pyramid_size = self._calculate_size(pyramid)
            
            # 简单的大小检查
            if len(self._pyramid_cache) >= self._max_size:
                # 删除最旧的条目
                oldest_key = next(iter(self._pyramid_cache))
                old_entry = self._pyramid_cache.pop(oldest_key)
                self._current_memory -= old_entry.size
                self._pyramid_stats.record_eviction()
            
            entry = CacheEntry(image_hash, pyramid, pyramid_size)
            self._pyramid_cache[image_hash] = entry
            self._current_memory += pyramid_size
        except Exception as e:
            self._logger.error(f"缓存金字塔出错: {e}")
    
    # 特征缓存方法
    def get_cached_features(self, region_id: str) -> Optional[Dict[str, Any]]:
        """获取缓存的特征"""
        try:
            if region_id in self._feature_cache:
                entry = self._feature_cache[region_id]
                entry.access()
                # 移动到末尾（LRU）
                self._feature_cache.move_to_end(region_id)
                self._feature_stats.record_hit()
                return entry.value
            
            self._feature_stats.record_miss()
            return None
        except Exception as e:
            self._logger.error(f"获取特征缓存出错: {e}")
            return None
    
    def cache_features(self, region_id: str, features: Dict[str, Any]):
        """缓存特征"""
        try:
            size = self._calculate_size(features)
            
            # 简单的大小检查
            if len(self._feature_cache) >= self._max_size:
                # 删除最旧的条目
                oldest_key = next(iter(self._feature_cache))
                old_entry = self._feature_cache.pop(oldest_key)
                self._current_memory -= old_entry.size
                self._feature_stats.record_eviction()
            
            entry = CacheEntry(region_id, features, size)
            self._feature_cache[region_id] = entry
            self._current_memory += size
        except Exception as e:
            self._logger.error(f"缓存特征出错: {e}")
    
    # 结果缓存方法
    def get_cached_results(self, image: np.ndarray) -> Optional[List[Dict[str, Any]]]:
        """获取缓存的结果"""
        try:
            image_hash = self._get_image_hash(image)
            
            if image_hash in self._result_cache:
                entry = self._result_cache[image_hash]
                entry.access()
                # 移动到末尾（LRU）
                self._result_cache.move_to_end(image_hash)
                self._result_stats.record_hit()
                return entry.value
            
            self._result_stats.record_miss()
            return None
        except Exception as e:
            self._logger.error(f"获取结果缓存出错: {e}")
            return None
    
    def cache_results(self, image: np.ndarray, results: List[Dict[str, Any]]):
        """缓存结果"""
        try:
            image_hash = self._get_image_hash(image)
            size = self._calculate_size(results)
            
            # 简单的大小检查
            if len(self._result_cache) >= self._max_size:
                # 删除最旧的条目
                oldest_key = next(iter(self._result_cache))
                old_entry = self._result_cache.pop(oldest_key)
                self._current_memory -= old_entry.size
                self._result_stats.record_eviction()
            
            entry = CacheEntry(image_hash, results, size)
            self._result_cache[image_hash] = entry
            self._current_memory += size
        except Exception as e:
            self._logger.error(f"缓存结果出错: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            'pyramid_cache': self._pyramid_stats.to_dict(),
            'feature_cache': self._feature_stats.to_dict(),
            'result_cache': self._result_stats.to_dict(),
            'total_memory_mb': self._current_memory / (1024 * 1024),
            'memory_limit_mb': self._max_memory / (1024 * 1024),
            'memory_usage_percent': (self._current_memory / self._max_memory) * 100,
            'cache_sizes': {
                'pyramid': len(self._pyramid_cache),
                'feature': len(self._feature_cache),
                'result': len(self._result_cache)
            }
        }
    
    def clear(self):
        """清空所有缓存"""
        try:
            self._pyramid_cache.clear()
            self._feature_cache.clear()
            self._result_cache.clear()
            self._current_memory = 0
            
            self._pyramid_stats.reset()
            self._feature_stats.reset()
            self._result_stats.reset()
        except Exception as e:
            self._logger.error(f"清空缓存出错: {e}")
    
    def optimize(self):
        """优化缓存"""
        try:
            # 简单的优化：如果内存使用过高，清理一半缓存
            if self._current_memory > self._max_memory * 0.8:
                # 清理一半最旧的条目
                for cache in [self._pyramid_cache, self._feature_cache, self._result_cache]:
                    items_to_remove = len(cache) // 2
                    for _ in range(items_to_remove):
                        if cache:
                            oldest_key = next(iter(cache))
                            old_entry = cache.pop(oldest_key)
                            self._current_memory -= old_entry.size
            
            # 强制垃圾回收
            gc.collect()
        except Exception as e:
            self._logger.error(f"优化缓存出错: {e}")