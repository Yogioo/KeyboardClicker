# -*- coding: utf-8 -*-
"""
性能对比测试

对比统一识别算法与现有分散算法的性能差异。
"""

import cv2
import numpy as np
import time
import sys
import os
import psutil
import tracemalloc

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.unified_recognizer import UnifiedVisualRecognizer, UnifiedRecognitionConfig
from src.utils.screenshot import ScreenshotTool

class PerformanceComparison:
    """性能对比测试类"""
    
    def __init__(self):
        self._screenshot_tool = ScreenshotTool()
        self._test_images = []
        self._results = {}
    
    def PrepareTestImages(self, count: int = 10):
        """准备测试图像"""
        print(f"准备 {count} 张测试图像...")
        
        self._test_images = []
        for i in range(count):
            print(f"  截取图像 {i+1}/{count}")
            image_pil = self._screenshot_tool.capture_full_screen()
            image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
            if image is not None:
                self._test_images.append(image)
            time.sleep(0.5)  # 避免截图过快
        
        print(f"成功准备 {len(self._test_images)} 张测试图像")
    
    def TestUnifiedRecognizer(self, config_name: str = "default"):
        """测试统一识别器"""
        print(f"\n=== 测试统一识别器 ({config_name}) ===")
        
        # 创建配置
        config = UnifiedRecognitionConfig()
        if config_name == "fast":
            config.LoadFastConfig()
        elif config_name == "accurate":
            config.LoadAccurateConfig()
        
        recognizer = UnifiedVisualRecognizer(config)
        
        # 性能指标
        times = []
        memory_usage = []
        element_counts = []
        
        # 开始内存追踪
        tracemalloc.start()
        
        for i, image in enumerate(self._test_images):
            print(f"  处理图像 {i+1}/{len(self._test_images)}")
            
            # 记录开始时间和内存
            start_time = time.time()
            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 执行识别
            results = recognizer.DetectClickableElements(image)
            
            # 记录结束时间和内存
            end_time = time.time()
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 收集指标
            times.append(end_time - start_time)
            memory_usage.append(end_memory - start_memory)
            element_counts.append(len(results))
        
        # 获取内存峰值
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # 计算统计信息
        result = {
            'config': config_name,
            'times': times,
            'avg_time': sum(times) / len(times) if times else 0,
            'min_time': min(times) if times else 0,
            'max_time': max(times) if times else 0,
            'memory_usage': memory_usage,
            'avg_memory': sum(memory_usage) / len(memory_usage) if memory_usage else 0,
            'peak_memory_mb': peak / 1024 / 1024,
            'element_counts': element_counts,
            'avg_elements': sum(element_counts) / len(element_counts) if element_counts else 0,
            'total_elements': sum(element_counts),
            'performance_stats': recognizer.GetPerformanceStats()
        }
        
        # 输出结果
        self._PrintTestResults(result)
        
        return result
    
    def TestLegacyApproach(self):
        """测试传统分散方法（模拟）"""
        print(f"\n=== 测试传统分散方法（模拟） ===")
        
        # 这里模拟传统方法的性能
        # 实际项目中应该调用现有的分散识别算法
        
        times = []
        memory_usage = []
        element_counts = []
        
        for i, image in enumerate(self._test_images):
            print(f"  处理图像 {i+1}/{len(self._test_images)}")
            
            start_time = time.time()
            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 模拟多个独立的检测算法
            # 每个算法都需要独立计算边缘、梯度等特征
            self._SimulateLegacyDetection(image)
            
            end_time = time.time()
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            times.append(end_time - start_time)
            memory_usage.append(end_memory - start_memory)
            element_counts.append(np.random.randint(10, 50))  # 模拟结果数量
        
        result = {
            'config': 'legacy',
            'times': times,
            'avg_time': sum(times) / len(times) if times else 0,
            'min_time': min(times) if times else 0,
            'max_time': max(times) if times else 0,
            'memory_usage': memory_usage,
            'avg_memory': sum(memory_usage) / len(memory_usage) if memory_usage else 0,
            'element_counts': element_counts,
            'avg_elements': sum(element_counts) / len(element_counts) if element_counts else 0,
            'total_elements': sum(element_counts)
        }
        
        self._PrintTestResults(result)
        return result
    
    def _SimulateLegacyDetection(self, image: np.ndarray):
        """模拟传统检测方法"""
        # 模拟多个独立的检测算法
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 每个元素类型都独立计算特征（重复计算）
        for _ in range(5):  # 模拟5种元素类型
            # 重复计算边缘
            edges = cv2.Canny(gray, 50, 150)
            
            # 重复计算梯度
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1)
            
            # 重复计算HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 模拟一些处理延迟
            time.sleep(0.001)
    
    def _PrintTestResults(self, result):
        """输出测试结果"""
        config = result['config']
        print(f"\n{config} 模式结果:")
        print(f"  平均处理时间: {result['avg_time']:.3f}秒")
        print(f"  最快时间: {result['min_time']:.3f}秒")
        print(f"  最慢时间: {result['max_time']:.3f}秒")
        print(f"  平均内存使用: {result['avg_memory']:.2f}MB")
        
        if 'peak_memory_mb' in result:
            print(f"  峰值内存: {result['peak_memory_mb']:.2f}MB")
        
        print(f"  平均检测元素数: {result['avg_elements']:.1f}")
        print(f"  总检测元素数: {result['total_elements']}")
        
        if 'performance_stats' in result:
            stats = result['performance_stats']
            print(f"  缓存命中率: {stats.get('cache_hit_rate', 0):.2%}")
    
    def CompareResults(self, results: list):
        """对比测试结果"""
        print(f"\n=== 性能对比分析 ===")
        
        if len(results) < 2:
            print("需要至少两个测试结果进行对比")
            return
        
        # 以第一个结果为基准
        baseline = results[0]
        
        print(f"以 {baseline['config']} 为基准:")
        
        for result in results[1:]:
            config = result['config']
            
            # 时间对比
            time_ratio = baseline['avg_time'] / result['avg_time']
            if time_ratio > 1:
                print(f"  {config} 比基准快 {time_ratio:.2f}x")
            else:
                print(f"  {config} 比基准慢 {1/time_ratio:.2f}x")
            
            # 内存对比
            memory_ratio = baseline['avg_memory'] / result['avg_memory']
            if memory_ratio > 1:
                print(f"  {config} 内存使用减少 {memory_ratio:.2f}x")
            else:
                print(f"  {config} 内存使用增加 {1/memory_ratio:.2f}x")
            
            # 准确率对比（基于检测到的元素数量）
            element_ratio = result['avg_elements'] / baseline['avg_elements']
            print(f"  {config} 检测元素数量比例: {element_ratio:.2f}x")
    
    def RunFullComparison(self):
        """运行完整对比测试"""
        print("开始性能对比测试")
        print("=" * 50)
        
        # 1. 准备测试图像
        self.PrepareTestImages(5)  # 使用5张测试图像
        
        if not self._test_images:
            print("没有可用的测试图像")
            return
        
        results = []
        
        # 2. 测试不同配置的统一识别器
        results.append(self.TestUnifiedRecognizer("fast"))
        results.append(self.TestUnifiedRecognizer("default"))
        results.append(self.TestUnifiedRecognizer("accurate"))
        
        # 3. 测试传统方法
        results.append(self.TestLegacyApproach())
        
        # 4. 对比结果
        self.CompareResults(results)
        
        # 5. 保存结果
        self._SaveResults(results)
    
    def _SaveResults(self, results):
        """保存测试结果"""
        try:
            import json
            
            # 创建结果目录
            results_dir = os.path.join(os.path.dirname(__file__), '..', 'test_results')
            os.makedirs(results_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"performance_comparison_{timestamp}.json"
            filepath = os.path.join(results_dir, filename)
            
            # 准备保存的数据
            save_data = {
                'timestamp': timestamp,
                'test_image_count': len(self._test_images),
                'results': results
            }
            
            # 保存到文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n测试结果已保存到: {filepath}")
            
        except Exception as e:
            print(f"保存结果失败: {e}")

def main():
    """主函数"""
    try:
        comparison = PerformanceComparison()
        comparison.RunFullComparison()
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()