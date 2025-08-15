# -*- coding: utf-8 -*-
"""
统一图像识别算法模块

该模块实现了一个统一的图像识别系统，用于检测桌面上所有可点击的UI元素。
采用图像金字塔 + 统一特征提取 + 分层识别的架构，替代现有的分散算法设计。
"""

from .unified_visual_recognizer import UnifiedVisualRecognizer
from .recognition_config import UnifiedRecognitionConfig
from .image_pyramid import ImagePyramid
from .feature_extractor import FeatureExtractor
from .element_classifier import ElementClassifier
from .spatial_analyzer import SpatialAnalyzer

__all__ = [
    'UnifiedVisualRecognizer',
    'UnifiedRecognitionConfig', 
    'ImagePyramid',
    'FeatureExtractor',
    'ElementClassifier',
    'SpatialAnalyzer'
]

__version__ = "1.0.0"
__author__ = "KeyboardClicker Team"