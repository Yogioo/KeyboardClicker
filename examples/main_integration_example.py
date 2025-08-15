# -*- coding: utf-8 -*-
"""
主程序集成示例

展示如何将统一识别器集成到现有的main.py中。
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.unified_recognizer import UnifiedVisualRecognizer, UnifiedRecognitionConfig
from src.utils.screenshot import ScreenshotTool
from src.utils.bounding_box_overlay import BoundingBoxOverlay
from src.core.clicker import ClickerTool

class EnhancedKeyboardClickerApp:
    """增强版键盘点击器应用 - 使用统一识别算法"""
    
    def __init__(self):
        """初始化应用"""
        
        # 初始化统一识别器
        self._config = UnifiedRecognitionConfig()
        self._config.LoadBalancedConfig()  # 使用平衡配置
        self._recognizer = UnifiedVisualRecognizer(self._config)
        
        # 初始化其他工具
        self._screenshot_tool = ScreenshotTool()
        self._bbox_overlay = BoundingBoxOverlay()
        self._clicker_tool = ClickerTool()
        
        # 设置回调 - F1键监听需要在start_listening中处理
        
        print("增强版键盘点击器已初始化")
        print("使用统一图像识别算法")
        print("按 F1 键进行智能识别和点击")
    
    def _OnF1Pressed(self):
        """F1键按下回调 - 执行智能识别和点击"""
        try:
            print("\n=== F1键触发 - 开始智能识别 ===")
            
            # 1. 截图
            image_pil = self._screenshot_tool.capture_full_screen()
            if image_pil is None:
                print("截图失败")
                return
            image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
            if image is None:
                print("截图失败")
                return
            
            print(f"截图成功，尺寸: {image.shape}")
            
            # 2. 使用统一识别算法
            results = self._recognizer.DetectClickableElements(image)
            
            if not results:
                print("未检测到可点击元素")
                return
            
            print(f"检测到 {len(results)} 个可点击元素")
            
            # 3. 显示检测结果统计
            self._ShowDetectionStats(results)
            
            # 4. 智能选择最佳点击目标
            best_target = self._SelectBestTarget(results)
            
            if best_target:
                print(f"选择最佳目标: {best_target['type']} (置信度: {best_target['confidence']:.3f})")
                
                # 5. 显示所有检测结果
                self._ShowAllDetections(results)
                
                # 6. 高亮最佳目标
                self._HighlightBestTarget(best_target)
                
                # 7. 执行点击
                self._ClickTarget(best_target)
            else:
                print("未找到合适的点击目标")
                
        except Exception as e:
            print(f"F1处理失败: {e}")
    
    def _ShowDetectionStats(self, results):
        """显示检测统计信息"""
        type_counts = {}
        confidence_sum = {}
        
        for result in results:
            element_type = result['type']
            confidence = result['confidence']
            
            type_counts[element_type] = type_counts.get(element_type, 0) + 1
            confidence_sum[element_type] = confidence_sum.get(element_type, 0) + confidence
        
        print("检测结果统计:")
        for element_type, count in type_counts.items():
            avg_confidence = confidence_sum[element_type] / count
            print(f"  {element_type}: {count} 个 (平均置信度: {avg_confidence:.3f})")
    
    def _SelectBestTarget(self, results):
        """智能选择最佳点击目标"""
        # 优先级权重
        type_priority = {
            'button': 1.0,
            'input': 0.8,
            'link': 0.7,
            'icon': 0.6,
            'text': 0.4
        }
        
        best_target = None
        best_score = 0
        
        for result in results:
            element_type = result['type']
            confidence = result['confidence']
            
            # 计算综合评分
            priority_weight = type_priority.get(element_type, 0.3)
            score = confidence * priority_weight
            
            # 考虑元素大小（适中大小的元素更容易点击）
            bbox = result['bbox']
            area = bbox[2] * bbox[3]
            if 500 <= area <= 10000:  # 适中大小
                score *= 1.2
            elif area < 100:  # 太小
                score *= 0.5
            
            if score > best_score:
                best_score = score
                best_target = result
        
        return best_target
    
    def _ShowAllDetections(self, results):
        """显示所有检测结果的边界框"""
        try:
            # 按类型分组
            type_groups = {}
            for result in results:
                element_type = result['type']
                if element_type not in type_groups:
                    type_groups[element_type] = []
                type_groups[element_type].append(result)
            
            # 颜色映射
            type_colors = {
                'button': 'red',
                'icon': 'blue',
                'text': 'green',
                'link': 'yellow',
                'input': 'purple'
            }
            
            # 显示各类型的边界框
            for element_type, group_results in type_groups.items():
                color = type_colors.get(element_type, 'gray')
                coords = [(r['bbox'][0], r['bbox'][1], r['bbox'][2], r['bbox'][3]) for r in group_results]
                
                print(f"显示 {len(coords)} 个 {element_type} ({color})")
                self._bbox_overlay.ShowBoundingBoxesFromCoords(coords, box_color=color, duration=1.0)
                
        except Exception as e:
            print(f"显示检测结果失败: {e}")
    
    def _HighlightBestTarget(self, target):
        """高亮最佳目标"""
        try:
            bbox = target['bbox']
            x, y, w, h = bbox
            
            print(f"高亮最佳目标: {target['type']} at ({x}, {y}, {w}, {h})")
            
            # 使用特殊颜色高亮
            self._bbox_overlay.ShowCustomBoundingBox(x, y, w, h, box_color='orange', duration=2.0)
            
        except Exception as e:
            print(f"高亮目标失败: {e}")
    
    def _ClickTarget(self, target):
        """点击目标"""
        try:
            bbox = target['bbox']
            x, y, w, h = bbox
            
            # 计算点击位置（中心点）
            click_x = x + w // 2
            click_y = y + h // 2
            
            print(f"点击位置: ({click_x}, {click_y})")
            
            # 执行点击
            self._clicker_tool.perform_click(click_x, click_y)
            
            print("点击执行完成")
            
        except Exception as e:
            print(f"点击失败: {e}")
    
    def UpdateRecognitionConfig(self, config_type: str = "balanced"):
        """更新识别配置"""
        try:
            if config_type == "fast":
                self._config.LoadFastConfig()
            elif config_type == "accurate":
                self._config.LoadAccurateConfig()
            else:
                self._config.LoadBalancedConfig()
            
            self._recognizer.UpdateConfig(self._config)
            print(f"识别配置已更新为: {config_type}")
            
        except Exception as e:
            print(f"更新配置失败: {e}")
    
    def GetPerformanceStats(self):
        """获取性能统计"""
        stats = self._recognizer.GetPerformanceStats()
        
        print("性能统计:")
        print(f"  总识别次数: {stats.get('total_recognitions', 0)}")
        print(f"  平均耗时: {stats.get('average_time', 0):.3f}秒")
        print(f"  上次耗时: {stats.get('last_recognition_time', 0):.3f}秒")
        print(f"  缓存命中率: {stats.get('cache_hit_rate', 0):.2%}")
        
        return stats
    
    def DiagnoseLastScreenshot(self):
        """诊断最后一次截图"""
        try:
            image_pil = self._screenshot_tool.capture_full_screen()
            if image_pil is None:
                print("截图失败")
                return
            image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
            
            diagnosis = self._recognizer.DiagnoseImage(image)
            
            print("图像诊断结果:")
            
            # 图像信息
            image_info = diagnosis.get('image_info', {})
            print(f"  图像尺寸: {image_info.get('shape', 'N/A')}")
            print(f"  图像大小: {image_info.get('size_mb', 0):.2f} MB")
            
            # 处理时间分析
            processing_times = diagnosis.get('processing_times', {})
            total_time = sum(processing_times.values())
            
            print("  处理时间分析:")
            for stage, time_cost in processing_times.items():
                percentage = (time_cost / total_time * 100) if total_time > 0 else 0
                print(f"    {stage}: {time_cost:.3f}秒 ({percentage:.1f}%)")
            
            print(f"  总处理时间: {total_time:.3f}秒")
            
        except Exception as e:
            print(f"诊断失败: {e}")
    
    def Start(self):
        """启动应用"""
        print("\n增强版键盘点击器已启动")
        print("可用命令:")
        print("  F1 - 智能识别和点击")
        print("  Ctrl+C - 退出程序")
        print("\n等待F1键按下...")
        
        try:
            # 设置点击回调
            self._clicker_tool.set_click_callback(lambda x, y: self._OnF1Pressed())
            self._clicker_tool.start_listening('f1')
        except KeyboardInterrupt:
            print("\n程序被用户中断")
        except Exception as e:
            print(f"程序运行错误: {e}")
        finally:
            self._clicker_tool.stop_listening()

def main():
    """主函数"""
    try:
        app = EnhancedKeyboardClickerApp()
        
        # 可以在这里测试不同的配置
        print("\n选择识别模式:")
        print("1. 快速模式 (速度优先)")
        print("2. 平衡模式 (默认)")
        print("3. 精确模式 (准确率优先)")
        
        choice = input("请选择 (1-3, 默认2): ").strip()
        
        if choice == "1":
            app.UpdateRecognitionConfig("fast")
        elif choice == "3":
            app.UpdateRecognitionConfig("accurate")
        else:
            app.UpdateRecognitionConfig("balanced")
        
        # 启动应用
        app.Start()
        
    except Exception as e:
        print(f"应用启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()