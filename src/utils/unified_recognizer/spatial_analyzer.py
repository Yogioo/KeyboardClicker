# -*- coding: utf-8 -*-
"""
空间关系分析器

基于空间关系优化识别结果，处理重叠冲突和语义关系增强。
"""

import numpy as np
from typing import Dict, List, Any, Tuple
import logging

class SpatialAnalyzer:
    """空间关系分析器"""
    
    def __init__(self, overlap_threshold: float = 0.3, semantic_distance_threshold: int = 50):
        """
        初始化空间分析器
        
        Args:
            overlap_threshold: 重叠阈值
            semantic_distance_threshold: 语义距离阈值
        """
        self._overlap_threshold = overlap_threshold
        self._semantic_distance_threshold = semantic_distance_threshold
        self._logger = logging.getLogger(__name__)
        
        # 元素类型权重（用于冲突解决）
        self._type_weights = {
            'button': 1.0,
            'input': 0.9,
            'icon': 0.8,
            'link': 0.7,
            'text': 0.6
        }
    
    #region 主要接口
    def OptimizeSpatialRelationships(self, classified_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        基于空间关系优化识别结果
        
        Args:
            classified_elements: 分类结果列表
            
        Returns:
            优化后的结果列表
        """
        try:
            if not classified_elements:
                return classified_elements
            
            # 1. 去除重叠冲突
            non_overlapping = self._ResolveOverlaps(classified_elements)
            
            # 2. 语义关系推理
            semantically_enhanced = self._EnhanceWithSemantics(non_overlapping)
            
            # 3. 置信度重新计算
            final_results = self._RecalculateConfidence(semantically_enhanced)
            
            # 4. 按置信度排序
            final_results.sort(key=lambda x: x['confidence'], reverse=True)
            
            self._logger.info(f"空间优化: {len(classified_elements)} -> {len(final_results)}")
            return final_results
            
        except Exception as e:
            self._logger.error(f"空间关系优化失败: {e}")
            return classified_elements
    #endregion
    
    #region 重叠冲突解决
    def _ResolveOverlaps(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        解决重叠问题 - 使用非最大抑制 (NMS) 算法
        
        Args:
            elements: 元素列表
            
        Returns:
            去除重叠后的元素列表
        """
        try:
            if not elements:
                return elements
            
            # 按置信度排序
            sorted_elements = sorted(elements, key=lambda x: x['confidence'], reverse=True)
            
            keep_indices = []
            suppressed = set()
            
            for i, element in enumerate(sorted_elements):
                if i in suppressed:
                    continue
                
                keep_indices.append(i)
                current_bbox = element['bbox']
                
                # 检查与后续元素的重叠
                for j in range(i + 1, len(sorted_elements)):
                    if j in suppressed:
                        continue
                    
                    other_element = sorted_elements[j]
                    other_bbox = other_element['bbox']
                    
                    # 计算重叠度
                    overlap_ratio = self._CalculateOverlapRatio(current_bbox, other_bbox)
                    
                    if overlap_ratio > self._overlap_threshold:
                        # 决定保留哪个元素
                        should_suppress = self._ShouldSuppressElement(element, other_element)
                        if should_suppress:
                            suppressed.add(j)
            
            # 构建结果列表
            result = [sorted_elements[i] for i in keep_indices]
            
            self._logger.info(f"重叠解决: 保留{len(result)}/{len(elements)}个元素")
            return result
            
        except Exception as e:
            self._logger.error(f"解决重叠失败: {e}")
            return elements
    
    def _CalculateOverlapRatio(self, bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
        """
        计算两个边界框的重叠比率
        
        Args:
            bbox1: 第一个边界框 (x, y, w, h)
            bbox2: 第二个边界框 (x, y, w, h)
            
        Returns:
            重叠比率 (0-1)
        """
        try:
            x1, y1, w1, h1 = bbox1
            x2, y2, w2, h2 = bbox2
            
            # 计算交集
            left = max(x1, x2)
            top = max(y1, y2)
            right = min(x1 + w1, x2 + w2)
            bottom = min(y1 + h1, y2 + h2)
            
            if left >= right or top >= bottom:
                return 0.0
            
            intersection = (right - left) * (bottom - top)
            
            # 计算并集
            area1 = w1 * h1
            area2 = w2 * h2
            union = area1 + area2 - intersection
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            self._logger.error(f"计算重叠比率失败: {e}")
            return 0.0
    
    def _ShouldSuppressElement(self, element1: Dict[str, Any], element2: Dict[str, Any]) -> bool:
        """
        决定是否应该抑制第二个元素
        
        Args:
            element1: 第一个元素（置信度更高）
            element2: 第二个元素
            
        Returns:
            是否应该抑制第二个元素
        """
        try:
            # 1. 优先考虑置信度
            conf_diff = element1['confidence'] - element2['confidence']
            if conf_diff > 0.2:
                return True
            
            # 2. 考虑元素类型权重
            type1 = element1['type']
            type2 = element2['type']
            
            weight1 = self._type_weights.get(type1, 0.5)
            weight2 = self._type_weights.get(type2, 0.5)
            
            # 加权置信度比较
            weighted_conf1 = element1['confidence'] * weight1
            weighted_conf2 = element2['confidence'] * weight2
            
            return weighted_conf1 > weighted_conf2
            
        except Exception as e:
            self._logger.error(f"判断抑制失败: {e}")
            return True
    #endregion
    
    #region 语义关系增强
    def _EnhanceWithSemantics(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        语义关系增强
        
        Args:
            elements: 元素列表
            
        Returns:
            语义增强后的元素列表
        """
        try:
            enhanced_elements = []
            
            for element in elements:
                enhanced_element = element.copy()
                
                # 查找附近的相关元素
                nearby_elements = self._FindNearbyElements(element, elements)
                
                # 基于语义关系调整置信度
                semantic_boost = self._CalculateSemanticBoost(element, nearby_elements)
                enhanced_element['confidence'] = min(1.0, element['confidence'] + semantic_boost)
                
                # 添加语义标签
                enhanced_element['semantic_context'] = self._AnalyzeSemanticContext(element, nearby_elements)
                
                enhanced_elements.append(enhanced_element)
            
            return enhanced_elements
            
        except Exception as e:
            self._logger.error(f"语义增强失败: {e}")
            return elements
    
    def _FindNearbyElements(self, target_element: Dict[str, Any], all_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        查找附近的元素
        
        Args:
            target_element: 目标元素
            all_elements: 所有元素列表
            
        Returns:
            附近的元素列表
        """
        try:
            nearby_elements = []
            target_bbox = target_element['bbox']
            target_center = self._GetBboxCenter(target_bbox)
            
            for element in all_elements:
                if element is target_element:
                    continue
                
                element_bbox = element['bbox']
                element_center = self._GetBboxCenter(element_bbox)
                
                # 计算距离
                distance = self._CalculateDistance(target_center, element_center)
                
                if distance <= self._semantic_distance_threshold:
                    nearby_elements.append({
                        'element': element,
                        'distance': distance,
                        'direction': self._GetDirection(target_center, element_center)
                    })
            
            # 按距离排序
            nearby_elements.sort(key=lambda x: x['distance'])
            return nearby_elements
            
        except Exception as e:
            self._logger.error(f"查找附近元素失败: {e}")
            return []
    
    def _CalculateSemanticBoost(self, element: Dict[str, Any], nearby_elements: List[Dict[str, Any]]) -> float:
        """
        计算语义提升值
        
        Args:
            element: 目标元素
            nearby_elements: 附近元素列表
            
        Returns:
            语义提升值
        """
        try:
            boost = 0.0
            element_type = element['type']
            
            for nearby in nearby_elements:
                nearby_element = nearby['element']
                nearby_type = nearby_element['type']
                distance = nearby['distance']
                direction = nearby['direction']
                
                # 距离权重（越近权重越高）
                distance_weight = max(0, 1.0 - distance / self._semantic_distance_threshold)
                
                # 语义关系评分
                semantic_score = self._GetSemanticScore(element_type, nearby_type, direction)
                
                boost += semantic_score * distance_weight * 0.1
            
            return min(boost, 0.3)  # 最大提升0.3
            
        except Exception as e:
            self._logger.error(f"计算语义提升失败: {e}")
            return 0.0
    
    def _GetSemanticScore(self, type1: str, type2: str, direction: str) -> float:
        """
        获取语义关系评分
        
        Args:
            type1: 第一个元素类型
            type2: 第二个元素类型
            direction: 相对方向
            
        Returns:
            语义关系评分
        """
        # 定义语义关系规则
        semantic_rules = {
            # 按钮旁边的文字可能是标签
            ('button', 'text'): {'left': 0.3, 'right': 0.2, 'above': 0.1, 'below': 0.1},
            # 输入框旁边的文字可能是提示
            ('input', 'text'): {'left': 0.4, 'right': 0.1, 'above': 0.2, 'below': 0.1},
            # 图标下方的文字可能是说明
            ('icon', 'text'): {'below': 0.3, 'right': 0.2, 'left': 0.1, 'above': 0.0},
            # 链接通常单独出现，与其他文本的关系较弱
            ('link', 'text'): {'left': 0.1, 'right': 0.1, 'above': 0.0, 'below': 0.0},
            # 相同类型的元素通常有一定的空间规律
            ('button', 'button'): {'right': 0.1, 'below': 0.1, 'left': 0.1, 'above': 0.1},
            ('icon', 'icon'): {'right': 0.2, 'below': 0.2, 'left': 0.2, 'above': 0.2}
        }
        
        # 查找匹配的规则
        rule_key = (type1, type2)
        if rule_key in semantic_rules:
            return semantic_rules[rule_key].get(direction, 0.0)
        
        # 反向查找
        rule_key = (type2, type1)
        if rule_key in semantic_rules:
            # 反向方向映射
            reverse_direction = {'left': 'right', 'right': 'left', 'above': 'below', 'below': 'above'}
            reverse_dir = reverse_direction.get(direction, direction)
            return semantic_rules[rule_key].get(reverse_dir, 0.0)
        
        return 0.0
    
    def _AnalyzeSemanticContext(self, element: Dict[str, Any], nearby_elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析语义上下文
        
        Args:
            element: 目标元素
            nearby_elements: 附近元素列表
            
        Returns:
            语义上下文信息
        """
        context = {
            'has_label': False,
            'has_description': False,
            'in_group': False,
            'group_type': None,
            'related_elements': []
        }
        
        try:
            element_type = element['type']
            
            for nearby in nearby_elements:
                nearby_element = nearby['element']
                nearby_type = nearby_element['type']
                direction = nearby['direction']
                
                # 检查是否有标签
                if (element_type in ['button', 'input'] and nearby_type == 'text' and direction == 'left'):
                    context['has_label'] = True
                
                # 检查是否有描述
                if (element_type == 'icon' and nearby_type == 'text' and direction == 'below'):
                    context['has_description'] = True
                
                # 检查是否在组中
                if nearby_type == element_type and nearby['distance'] < 30:
                    context['in_group'] = True
                    context['group_type'] = element_type
                
                context['related_elements'].append({
                    'type': nearby_type,
                    'direction': direction,
                    'distance': nearby['distance']
                })
            
            return context
            
        except Exception as e:
            self._logger.error(f"分析语义上下文失败: {e}")
            return context
    #endregion
    
    #region 置信度重新计算
    def _RecalculateConfidence(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        基于空间分析结果重新计算置信度
        
        Args:
            elements: 元素列表
            
        Returns:
            重新计算置信度后的元素列表
        """
        try:
            for element in elements:
                original_confidence = element['confidence']
                
                # 基于语义上下文的调整
                context_boost = self._GetContextBoost(element.get('semantic_context', {}))
                
                # 基于元素密度的调整
                density_adjustment = self._GetDensityAdjustment(element, elements)
                
                # 计算最终置信度
                final_confidence = original_confidence + context_boost + density_adjustment
                element['confidence'] = max(0.0, min(1.0, final_confidence))
                
                # 保存调整信息用于调试
                element['confidence_adjustments'] = {
                    'original': original_confidence,
                    'context_boost': context_boost,
                    'density_adjustment': density_adjustment,
                    'final': element['confidence']
                }
            
            return elements
            
        except Exception as e:
            self._logger.error(f"重新计算置信度失败: {e}")
            return elements
    
    def _GetContextBoost(self, semantic_context: Dict[str, Any]) -> float:
        """
        基于语义上下文获取置信度提升
        
        Args:
            semantic_context: 语义上下文
            
        Returns:
            置信度提升值
        """
        boost = 0.0
        
        if semantic_context.get('has_label', False):
            boost += 0.05
        
        if semantic_context.get('has_description', False):
            boost += 0.05
        
        if semantic_context.get('in_group', False):
            boost += 0.03
        
        return boost
    
    def _GetDensityAdjustment(self, element: Dict[str, Any], all_elements: List[Dict[str, Any]]) -> float:
        """
        基于元素密度获取置信度调整
        
        Args:
            element: 目标元素
            all_elements: 所有元素
            
        Returns:
            密度调整值
        """
        try:
            element_type = element['type']
            element_bbox = element['bbox']
            element_center = self._GetBboxCenter(element_bbox)
            
            # 计算附近相同类型元素的数量
            same_type_nearby = 0
            for other_element in all_elements:
                if other_element is element:
                    continue
                
                if other_element['type'] == element_type:
                    other_center = self._GetBboxCenter(other_element['bbox'])
                    distance = self._CalculateDistance(element_center, other_center)
                    
                    if distance < 100:  # 100像素范围内
                        same_type_nearby += 1
            
            # 密度过高可能是误检
            if same_type_nearby > 5:
                return -0.1
            elif same_type_nearby > 3:
                return -0.05
            elif same_type_nearby >= 1:
                return 0.02  # 适度的密度有助于确认
            
            return 0.0
            
        except Exception as e:
            self._logger.error(f"计算密度调整失败: {e}")
            return 0.0
    #endregion
    
    #region 工具方法
    def _GetBboxCenter(self, bbox: Tuple[int, int, int, int]) -> Tuple[float, float]:
        """获取边界框中心点"""
        x, y, w, h = bbox
        return (x + w / 2, y + h / 2)
    
    def _CalculateDistance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """计算两点间距离"""
        return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
    
    def _GetDirection(self, center1: Tuple[float, float], center2: Tuple[float, float]) -> str:
        """获取相对方向"""
        dx = center2[0] - center1[0]
        dy = center2[1] - center1[1]
        
        if abs(dx) > abs(dy):
            return 'right' if dx > 0 else 'left'
        else:
            return 'below' if dy > 0 else 'above'
    
    def SetOverlapThreshold(self, threshold: float):
        """设置重叠阈值"""
        self._overlap_threshold = threshold
    
    def SetSemanticDistanceThreshold(self, threshold: int):
        """设置语义距离阈值"""
        self._semantic_distance_threshold = threshold
    #endregion