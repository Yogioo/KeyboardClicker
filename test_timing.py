#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试性能计时功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.fast_label_integrator import FastLabelIntegrator

def test_timing():
    """测试计时功能"""
    print("开始测试性能计时功能...")
    
    integrator = FastLabelIntegrator()
    
    # 执行一次完整的截图识别流程
    print("\n执行截图识别...")
    success = integrator.capture_and_recognize(save_screenshot=False)
    
    if success:
        detections = integrator.get_current_detections()
        print(f"\n成功！检测到 {len(detections)} 个元素")
        
        # 测试边界框显示
        print("\n执行边界框显示...")
        bbox_success = integrator.show_bounding_boxes(duration=3.0)
        
        if bbox_success:
            print("边界框显示成功！")
        else:
            print("边界框显示失败！")
    else:
        print("识别失败！")

if __name__ == "__main__":
    test_timing()