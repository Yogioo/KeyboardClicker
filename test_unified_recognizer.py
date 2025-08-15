# -*- coding: utf-8 -*-
"""
统一识别器快速测试

用于快速验证统一识别器是否正常工作。
"""

import cv2
import numpy as np
import time
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

def test_basic_functionality():
    """测试基础功能"""
    print("=== 统一识别器基础功能测试 ===")
    
    try:
        from src.utils.unified_recognizer import UnifiedVisualRecognizer, UnifiedRecognitionConfig
        print("√ 模块导入成功")
        
        # 创建配置
        config = UnifiedRecognitionConfig()
        print("√ 配置创建成功")
        
        # 创建识别器
        recognizer = UnifiedVisualRecognizer(config)
        print("√ 识别器创建成功")
        
        # 创建测试图像
        test_image = create_test_image()
        print("√ 测试图像创建成功")
        
        # 执行识别
        start_time = time.time()
        results = recognizer.DetectClickableElements(test_image)
        end_time = time.time()
        
        print(f"√ 识别执行成功，耗时: {end_time - start_time:.3f}秒")
        print(f"√ 检测到 {len(results)} 个元素")
        
        # 测试单类型检测
        button_results = recognizer.DetectSingleType('button', test_image)
        print(f"√ 单类型检测成功，检测到 {len(button_results)} 个按钮")
        
        # 测试性能统计
        stats = recognizer.GetPerformanceStats()
        print(f"√ 性能统计获取成功: {stats}")
        
        # 测试诊断功能
        diagnosis = recognizer.DiagnoseImage(test_image)
        print(f"√ 诊断功能正常: 特征数量 {diagnosis.get('feature_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"× 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_test_image():
    """创建测试图像"""
    # 创建一个简单的测试图像，包含一些基本形状
    image = np.ones((600, 800, 3), dtype=np.uint8) * 255  # 白色背景
    
    # 绘制几个矩形（模拟按钮）
    cv2.rectangle(image, (50, 50), (150, 100), (100, 100, 100), -1)  # 灰色矩形
    cv2.rectangle(image, (200, 50), (300, 100), (50, 50, 200), -1)   # 红色矩形
    cv2.rectangle(image, (350, 50), (450, 100), (50, 200, 50), -1)   # 绿色矩形
    
    # 绘制几个圆形（模拟图标）
    cv2.circle(image, (100, 200), 30, (200, 100, 50), -1)  # 蓝色圆形
    cv2.circle(image, (250, 200), 25, (100, 200, 100), -1) # 绿色圆形
    
    # 绘制一些线条（模拟文本）
    cv2.rectangle(image, (50, 300), (400, 320), (0, 0, 0), -1)     # 黑色矩形（文本）
    cv2.rectangle(image, (50, 350), (300, 370), (0, 0, 0), -1)     # 黑色矩形（文本）
    
    return image

def test_configuration():
    """测试配置功能"""
    print("\n=== 配置功能测试 ===")
    
    try:
        from src.utils.unified_recognizer import UnifiedRecognitionConfig
        
        # 测试默认配置
        config = UnifiedRecognitionConfig()
        print("√ 默认配置创建成功")
        
        # 测试预设配置
        config.LoadFastConfig()
        print("√ 快速配置加载成功")
        
        config.LoadAccurateConfig()
        print("√ 精确配置加载成功")
        
        config.LoadBalancedConfig()
        print("√ 平衡配置加载成功")
        
        # 测试配置验证
        errors = config.ValidateConfig()
        if not errors:
            print("√ 配置验证通过")
        else:
            print(f"× 配置验证失败: {errors}")
            return False
        
        # 测试配置序列化
        config_dict = config.ToDict()
        print(f"√ 配置序列化成功，包含 {len(config_dict)} 个部分")
        
        return True
        
    except Exception as e:
        print(f"× 配置测试失败: {e}")
        return False

def test_with_real_screenshot():
    """使用真实截图测试"""
    print("\n=== 真实截图测试 ===")
    
    try:
        from src.utils.unified_recognizer import UnifiedVisualRecognizer
        from src.utils.screenshot import ScreenshotTool
        
        # 创建工具
        recognizer = UnifiedVisualRecognizer()
        screenshot_tool = ScreenshotTool()
        
        # 截图
        image_pil = screenshot_tool.capture_full_screen()
        if image_pil is None:
            print("× 截图失败")
            return False
        
        # 转换为numpy数组 (PIL Image -> OpenCV格式)
        image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        print(f"√ 截图成功，尺寸: {image.shape}")
        
        # 识别
        start_time = time.time()
        results = recognizer.DetectClickableElements(image)
        end_time = time.time()
        
        print(f"√ 识别完成，耗时: {end_time - start_time:.3f}秒")
        print(f"√ 检测到 {len(results)} 个可点击元素")
        
        # 显示结果统计
        if results:
            type_counts = {}
            for result in results:
                element_type = result['type']
                type_counts[element_type] = type_counts.get(element_type, 0) + 1
            
            print("元素类型统计:")
            for element_type, count in type_counts.items():
                print(f"  {element_type}: {count}")
        
        return True
        
    except Exception as e:
        print(f"× 真实截图测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("统一识别器快速测试")
    print("=" * 50)
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    
    # 检查OpenCV
    print(f"OpenCV版本: {cv2.__version__}")
    
    # 执行测试
    tests = [
        ("基础功能", test_basic_functionality),
        ("配置功能", test_configuration),
        ("真实截图", test_with_real_screenshot)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name}测试 ---")
        try:
            if test_func():
                print(f"√ {test_name}测试通过")
                passed += 1
            else:
                print(f"× {test_name}测试失败")
        except Exception as e:
            print(f"× {test_name}测试异常: {e}")
    
    print(f"\n{'='*50}")
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("[成功] 所有测试通过！统一识别器工作正常。")
        return True
    else:
        print("[警告] 部分测试失败，请检查相关模块。")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)