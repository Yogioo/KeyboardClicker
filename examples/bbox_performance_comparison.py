#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
边界框显示性能对比测试
比较优化前后的性能差异
"""

import sys
import os
import time
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.bounding_box_overlay import BoundingBoxOverlay
from src.utils.optimized_bbox_overlay import OptimizedBoundingBoxOverlay


def generate_test_detections(count: int) -> list:
    """生成测试用的检测结果"""
    detections = []
    for i in range(count):
        x = random.randint(0, 1400)
        y = random.randint(0, 800)
        w = random.randint(40, 180)
        h = random.randint(25, 100)
        
        detections.append({
            'bbox': (x, y, w, h),
            'type': random.choice(['button', 'link', 'input', 'icon', 'text']),
            'confidence': random.uniform(0.5, 1.0),
            'id': f'test_{i}'
        })
    
    return detections


def test_original_version(detections: list) -> float:
    """测试原版边界框覆盖层性能"""
    print(f"  测试原版 (多窗口) - {len(detections)} 个边界框...")
    
    bbox_overlay = BoundingBoxOverlay()
    
    start_time = time.time()
    success = bbox_overlay.ShowBoundingBoxes(detections, duration=0.5)
    render_time = time.time() - start_time
    
    if success:
        print(f"    原版渲染完成，耗时: {render_time:.3f} 秒")
        time.sleep(0.6)  # 等待显示完成
        bbox_overlay.HideBoundingBoxes()
    else:
        print(f"    原版渲染失败")
        render_time = float('inf')
    
    return render_time


def test_optimized_version(detections: list) -> float:
    """测试优化版边界框覆盖层性能"""
    print(f"  测试优化版 (单窗口Canvas) - {len(detections)} 个边界框...")
    
    bbox_overlay = OptimizedBoundingBoxOverlay()
    
    start_time = time.time()
    success = bbox_overlay.ShowBoundingBoxes(detections, duration=0.5)
    render_time = time.time() - start_time
    
    if success:
        print(f"    优化版渲染完成，耗时: {render_time:.3f} 秒")
        time.sleep(0.6)  # 等待显示完成
        bbox_overlay.DestroyOverlay()
    else:
        print(f"    优化版渲染失败")
        render_time = float('inf')
    
    return render_time


def performance_comparison():
    """性能对比测试"""
    print("=" * 60)
    print("边界框显示性能对比测试")
    print("=" * 60)
    
    test_counts = [10, 30, 50, 100]
    results = []
    
    for count in test_counts:
        print(f"\n测试数量: {count} 个边界框")
        print("-" * 40)
        
        # 生成相同的测试数据
        detections = generate_test_detections(count)
        
        # 测试原版
        original_time = test_original_version(detections.copy())
        
        # 等待一下避免干扰
        time.sleep(1)
        
        # 测试优化版
        optimized_time = test_optimized_version(detections.copy())
        
        # 计算性能提升
        if original_time != float('inf') and optimized_time != float('inf'):
            improvement = (original_time - optimized_time) / original_time * 100
            speedup = original_time / optimized_time
            
            print(f"\n  性能分析:")
            print(f"    原版耗时:     {original_time:.3f} 秒")
            print(f"    优化版耗时:   {optimized_time:.3f} 秒")
            print(f"    性能提升:     {improvement:.1f}%")
            print(f"    速度倍数:     {speedup:.1f}x")
            
            results.append({
                'count': count,
                'original': original_time,
                'optimized': optimized_time,
                'improvement': improvement,
                'speedup': speedup
            })
        else:
            print(f"  测试失败，无法计算性能提升")
        
        time.sleep(1)
    
    # 汇总报告
    if results:
        print("\n" + "=" * 60)
        print("性能对比汇总报告")
        print("=" * 60)
        
        print(f"{'数量':<8} {'原版(秒)':<10} {'优化版(秒)':<12} {'提升%':<8} {'倍数':<6}")
        print("-" * 50)
        
        total_improvement = 0
        total_speedup = 0
        
        for result in results:
            print(f"{result['count']:<8} {result['original']:<10.3f} {result['optimized']:<12.3f} "
                  f"{result['improvement']:<8.1f} {result['speedup']:<6.1f}x")
            total_improvement += result['improvement']
            total_speedup += result['speedup']
        
        avg_improvement = total_improvement / len(results)
        avg_speedup = total_speedup / len(results)
        
        print("-" * 50)
        print(f"平均性能提升: {avg_improvement:.1f}%")
        print(f"平均速度倍数: {avg_speedup:.1f}x")
        
        # 性能分析
        print(f"\n优化效果分析:")
        if avg_improvement > 70:
            print("  显著性能提升！优化效果非常明显")
        elif avg_improvement > 40:
            print("  良好性能提升！优化效果明显")
        elif avg_improvement > 20:
            print("  中等性能提升，还有优化空间")
        else:
            print("  性能提升不明显，需要进一步优化")
        
        print(f"\n优化技术要点:")
        print(f"  • 使用单一Canvas窗口替代多个Toplevel窗口")
        print(f"  • 批量绘制所有边界框，减少窗口创建开销")
        print(f"  • 优化透明度和属性设置次数")
        print(f"  • 减少GUI事件循环和更新操作")


def quick_visual_demo():
    """快速可视化演示"""
    print("\n" + "=" * 60)
    print("快速可视化演示 - 显示效果对比")
    print("=" * 60)
    
    # 生成演示数据
    demo_detections = generate_test_detections(25)
    
    print("即将演示优化后的边界框显示效果...")
    print("请观察显示速度和流畅度")
    input("按回车键开始演示...")
    
    bbox_overlay = OptimizedBoundingBoxOverlay()
    
    try:
        # 演示快速显示
        print("显示25个边界框...")
        start_time = time.time()
        
        if bbox_overlay.ShowBoundingBoxes(demo_detections, duration=3.0, box_color='lime'):
            render_time = time.time() - start_time
            print(f"批量显示完成！耗时: {render_time:.3f} 秒")
            print("观察：所有边界框应该几乎同时出现，而不是逐个显示")
            print("等待3秒后自动隐藏...")
            time.sleep(3.2)
        
        # 演示颜色变化
        print("\n演示不同颜色的边界框...")
        colors = ['red', 'blue', 'green', 'orange', 'purple']
        
        for i, color in enumerate(colors):
            print(f"  显示 {color} 边界框...")
            bbox_overlay.ShowBoundingBoxes(demo_detections, duration=1.0, 
                                          box_color=color, box_width=3)
            time.sleep(1.2)
        
        print("演示完成！")
        
    except Exception as e:
        print(f"演示过程中出错: {e}")
    finally:
        bbox_overlay.DestroyOverlay()


if __name__ == "__main__":
    try:
        # 运行性能对比测试
        performance_comparison()
        
        # 可选：运行可视化演示
        choice = input("\n是否运行可视化演示？(y/n): ").strip().lower()
        if choice in ['y', 'yes', '']:
            quick_visual_demo()
        
        print("\n测试完成！")
        
    except KeyboardInterrupt:
        print("\n用户中断测试")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
    
    input("按回车键退出...")