# -*- coding: utf-8 -*-
"""
元素分类器

基于规则的分类系统，对统一特征进行元素类型分类。
"""

import numpy as np
from typing import Dict, List, Any, Callable, Tuple
import logging

class ElementClassifier:
    """元素分类器 - 基于规则的分类系统"""
    
    def __init__(self):
        """初始化分类器"""
        self._logger = logging.getLogger(__name__)
        
        # 分类规则映射
        self._classification_rules = {
            'button': self._ButtonRules,
            'icon': self._IconRules,
            'text': self._TextRules,
            'link': self._LinkRules,
            'input': self._InputRules
        }
        
        # 分类阈值
        self._thresholds = {
            'button': 0.4,
            'icon': 0.35,
            'text': 0.3,
            'link': 0.35,
            'input': 0.4
        }
    
    #region 主要接口
    def ClassifyElements(self, unified_features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        对统一特征进行分类
        
        Args:
            unified_features: 统一特征向量列表
            
        Returns:
            分类结果列表
        """
        try:
            classified_elements = []
            
            for feature_vector in unified_features:
                # 对每个特征向量计算所有类型的置信度
                confidences = {}
                for element_type, rule_func in self._classification_rules.items():
                    confidences[element_type] = rule_func(feature_vector)
                
                # 选择最高置信度的类型（如果超过阈值）
                best_type = max(confidences, key=confidences.get)
                best_confidence = confidences[best_type]
                
                if best_confidence > self._GetThreshold(best_type):
                    classified_elements.append({
                        'type': best_type,
                        'bbox': feature_vector['bbox'],
                        'confidence': best_confidence,
                        'features': feature_vector,
                        'all_confidences': confidences
                    })
            
            self._logger.info(f"分类出{len(classified_elements)}个元素")
            return classified_elements
            
        except Exception as e:
            self._logger.error(f"元素分类失败: {e}")
            return []
    
    def ClassifySingleType(self, element_type: str, unified_features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        单类型分类
        
        Args:
            element_type: 元素类型
            unified_features: 统一特征向量列表
            
        Returns:
            指定类型的分类结果
        """
        try:
            if element_type not in self._classification_rules:
                self._logger.error(f"不支持的元素类型: {element_type}")
                return []
            
            rule_func = self._classification_rules[element_type]
            threshold = self._GetThreshold(element_type)
            
            results = []
            for feature_vector in unified_features:
                confidence = rule_func(feature_vector)
                if confidence > threshold:
                    results.append({
                        'type': element_type,
                        'bbox': feature_vector['bbox'],
                        'confidence': confidence,
                        'features': feature_vector
                    })
            
            return results
            
        except Exception as e:
            self._logger.error(f"单类型分类失败: {e}")
            return []
    #endregion
    
    #region 分类规则实现
    def _ButtonRules(self, features: Dict[str, Any]) -> float:
        """
        按钮识别规则
        
        Args:
            features: 特征向量
            
        Returns:
            置信度分数 (0-1)
        """
        try:
            confidence = 0.0
            
            # 几何特征评分
            area = features.get('area', 0)
            if 200 <= area <= 20000:
                confidence += 0.3
            elif 100 <= area < 200 or 20000 < area <= 50000:
                confidence += 0.15
            
            aspect_ratio = features.get('aspect_ratio', 0)
            if 0.3 <= aspect_ratio <= 6.0:
                confidence += 0.2
            elif 0.1 <= aspect_ratio < 0.3 or 6.0 < aspect_ratio <= 10.0:
                confidence += 0.1
            
            extent = features.get('extent', 0)
            if extent > 0.5:  # 填充度
                confidence += 0.15
            elif extent > 0.3:
                confidence += 0.08
            
            # 颜色特征评分
            if self._IsButtonColor(features):
                confidence += 0.25
            
            # 边缘特征评分
            edge_density = features.get('edge_density', 0)
            if 0.1 <= edge_density <= 0.4:
                confidence += 0.1
            elif 0.05 <= edge_density < 0.1 or 0.4 < edge_density <= 0.6:
                confidence += 0.05
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self._logger.error(f"按钮规则计算失败: {e}")
            return 0.0
    
    def _IconRules(self, features: Dict[str, Any]) -> float:
        """
        图标识别规则
        
        Args:
            features: 特征向量
            
        Returns:
            置信度分数 (0-1)
        """
        try:
            confidence = 0.0
            
            # 接近正方形
            aspect_ratio = features.get('aspect_ratio', 0)
            if 0.6 <= aspect_ratio <= 2.0:
                confidence += 0.3
            elif 0.4 <= aspect_ratio < 0.6 or 2.0 < aspect_ratio <= 3.0:
                confidence += 0.15
            
            # 适中的尺寸
            area = features.get('area', 0)
            if 64 <= area <= 8000:
                confidence += 0.25
            elif 32 <= area < 64 or 8000 < area <= 15000:
                confidence += 0.12
            
            # 高对称性
            symmetry_score = features.get('symmetry_score', 0)
            if symmetry_score > 0.6:
                confidence += 0.2
            elif symmetry_score > 0.4:
                confidence += 0.1
            
            # 边界对比度
            border_contrast = features.get('border_contrast', 0)
            if border_contrast > 0.3:
                confidence += 0.25
            elif border_contrast > 0.15:
                confidence += 0.12
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self._logger.error(f"图标规则计算失败: {e}")
            return 0.0
    
    def _TextRules(self, features: Dict[str, Any]) -> float:
        """
        文本识别规则
        
        Args:
            features: 特征向量
            
        Returns:
            置信度分数 (0-1)
        """
        try:
            confidence = 0.0
            
            # 文本通常有高长宽比
            aspect_ratio = features.get('aspect_ratio', 0)
            if aspect_ratio >= 2.0:
                confidence += 0.3
            elif aspect_ratio >= 1.5:
                confidence += 0.15
            
            # 中等面积
            area = features.get('area', 0)
            if 100 <= area <= 10000:
                confidence += 0.25
            elif 50 <= area < 100 or 10000 < area <= 20000:
                confidence += 0.12
            
            # 低边缘密度（文本边缘相对简单）
            edge_density = features.get('edge_density', 0)
            if 0.05 <= edge_density <= 0.2:
                confidence += 0.2
            elif 0.02 <= edge_density < 0.05 or 0.2 < edge_density <= 0.3:
                confidence += 0.1
            
            # 低连通性（文本字符相对独立）
            connectivity = features.get('connectivity', 0)
            if connectivity <= 3:
                confidence += 0.15
            elif connectivity <= 6:
                confidence += 0.08
            
            # 高填充度
            extent = features.get('extent', 0)
            if extent > 0.3:
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self._logger.error(f"文本规则计算失败: {e}")
            return 0.0
    
    def _LinkRules(self, features: Dict[str, Any]) -> float:
        """
        链接识别规则
        
        Args:
            features: 特征向量
            
        Returns:
            置信度分数 (0-1)
        """
        try:
            confidence = 0.0
            
            # 链接通常是文本，具有高长宽比
            aspect_ratio = features.get('aspect_ratio', 0)
            if aspect_ratio >= 1.5:
                confidence += 0.25
            elif aspect_ratio >= 1.0:
                confidence += 0.12
            
            # 较小面积
            area = features.get('area', 0)
            if 50 <= area <= 5000:
                confidence += 0.2
            elif 30 <= area < 50 or 5000 < area <= 8000:
                confidence += 0.1
            
            # 特定颜色特征（蓝色调）
            if self._IsLinkColor(features):
                confidence += 0.3
            
            # 适中的边缘密度
            edge_density = features.get('edge_density', 0)
            if 0.08 <= edge_density <= 0.25:
                confidence += 0.15
            elif 0.05 <= edge_density < 0.08 or 0.25 < edge_density <= 0.35:
                confidence += 0.08
            
            # 低连通性
            connectivity = features.get('connectivity', 0)
            if connectivity <= 2:
                confidence += 0.1
            elif connectivity <= 4:
                confidence += 0.05
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self._logger.error(f"链接规则计算失败: {e}")
            return 0.0
    
    def _InputRules(self, features: Dict[str, Any]) -> float:
        """
        输入框识别规则
        
        Args:
            features: 特征向量
            
        Returns:
            置信度分数 (0-1)
        """
        try:
            confidence = 0.0
            
            # 输入框通常是矩形
            aspect_ratio = features.get('aspect_ratio', 0)
            if 2.0 <= aspect_ratio <= 8.0:
                confidence += 0.3
            elif 1.5 <= aspect_ratio < 2.0 or 8.0 < aspect_ratio <= 12.0:
                confidence += 0.15
            
            # 中等大小
            area = features.get('area', 0)
            if 500 <= area <= 15000:
                confidence += 0.25
            elif 200 <= area < 500 or 15000 < area <= 25000:
                confidence += 0.12
            
            # 高边界对比度（输入框通常有明显边框）
            border_contrast = features.get('border_contrast', 0)
            if border_contrast > 0.4:
                confidence += 0.2
            elif border_contrast > 0.2:
                confidence += 0.1
            
            # 高填充度
            extent = features.get('extent', 0)
            if extent > 0.7:
                confidence += 0.15
            elif extent > 0.5:
                confidence += 0.08
            
            # 背景色特征（通常是白色或浅色）
            if self._IsInputBackgroundColor(features):
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self._logger.error(f"输入框规则计算失败: {e}")
            return 0.0
    #endregion
    
    #region 颜色判断辅助方法
    def _IsButtonColor(self, features: Dict[str, Any]) -> bool:
        """判断是否为按钮颜色"""
        try:
            # 检查饱和度和亮度
            saturation_mean = features.get('saturation_mean', 0)
            value_mean = features.get('value_mean', 0)
            
            # 按钮通常有一定的饱和度和适中的亮度
            if saturation_mean > 30 and 50 <= value_mean <= 200:
                return True
            
            # 或者是灰度按钮（低饱和度但有一定亮度）
            if saturation_mean <= 30 and 80 <= value_mean <= 180:
                return True
                
            return False
            
        except:
            return False
    
    def _IsLinkColor(self, features: Dict[str, Any]) -> bool:
        """判断是否为链接颜色"""
        try:
            hue_mean = features.get('hue_mean', 0)
            saturation_mean = features.get('saturation_mean', 0)
            
            # 蓝色调 (hue在蓝色范围)
            if 100 <= hue_mean <= 130 and saturation_mean > 50:
                return True
                
            return False
            
        except:
            return False
    
    def _IsInputBackgroundColor(self, features: Dict[str, Any]) -> bool:
        """判断是否为输入框背景颜色"""
        try:
            lightness_mean = features.get('lightness_mean', 0)
            saturation_mean = features.get('saturation_mean', 0)
            
            # 通常是高亮度、低饱和度（白色或浅色）
            if lightness_mean > 200 and saturation_mean < 30:
                return True
                
            return False
            
        except:
            return False
    #endregion
    
    #region 配置和工具方法
    def _GetThreshold(self, element_type: str) -> float:
        """获取分类阈值"""
        return self._thresholds.get(element_type, 0.3)
    
    def SetThreshold(self, element_type: str, threshold: float):
        """设置分类阈值"""
        if element_type in self._thresholds:
            self._thresholds[element_type] = threshold
    
    def GetSupportedTypes(self) -> List[str]:
        """获取支持的元素类型"""
        return list(self._classification_rules.keys())
    
    def AddCustomRule(self, element_type: str, rule_func: Callable[[Dict[str, Any]], float], threshold: float = 0.3):
        """添加自定义分类规则"""
        self._classification_rules[element_type] = rule_func
        self._thresholds[element_type] = threshold
    #endregion