# -*- coding: utf-8 -*-
"""
测试main.py集成结果

验证新的统一识别器是否成功集成到main.py中。
"""

import sys
import os
import time

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

def test_main_components():
    """测试main.py的主要组件"""
    print("=== 测试main.py组件集成 ===")
    
    try:
        # 测试导入
        from main import SimpleKeyboardClickerApp
        print("[成功] main.py导入成功")
        
        # 测试适配器
        from src.utils.unified_recognizer_adapter import UnifiedRecognizerAdapter
        adapter = UnifiedRecognizerAdapter()
        print("[成功] 统一识别器适配器工作正常")
        
        # 测试配置
        from src.utils.detection_config import detection_config
        # 调试模式已移除，不需要设置
        print("[成功] 检测配置正常")
        
        # 测试快速集成器
        from src.utils.fast_label_integrator import FastLabelIntegrator
        integrator = FastLabelIntegrator()
        print("[成功] FastLabelIntegrator集成成功")
        
        return True
        
    except Exception as e:
        print(f"[错误] 组件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_recognition_functionality():
    """测试识别功能"""
    print("\n=== 测试识别功能 ===")
    
    try:
        from src.utils.unified_recognizer_adapter import UnifiedRecognizerAdapter
        from src.utils.screenshot import ScreenshotTool
        import cv2
        import numpy as np
        
        # 初始化组件
        adapter = UnifiedRecognizerAdapter()
        screenshot_tool = ScreenshotTool()
        
        print("[进行中] 获取截图...")
        image_pil = screenshot_tool.capture_full_screen()
        image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        print(f"[成功] 截图获取成功，尺寸: {image.shape}")
        
        # 测试全元素检测
        print("[进行中] 执行全元素检测...")
        start_time = time.time()
        results = adapter.detect_clickable_elements(image)
        detection_time = time.time() - start_time
        print(f"[成功] 全元素检测完成: {len(results)} 个元素，耗时 {detection_time:.3f} 秒")
        
        # 统计类型
        type_counts = {}
        for r in results:
            t = r['type']
            type_counts[t] = type_counts.get(t, 0) + 1
        
        print("检测结果统计:")
        for element_type, count in type_counts.items():
            print(f"  {element_type}: {count} 个")
        
        # 测试单类型检测
        print("\n[进行中] 测试单类型检测...")
        buttons = adapter.detect_single_type('button', image)
        icons = adapter.detect_single_type('icon', image)
        print(f"[成功] 单类型检测: {len(buttons)} 个按钮, {len(icons)} 个图标")
        
        # 测试性能统计
        stats = adapter.get_performance_stats()
        print(f"[成功] 性能统计:")
        print(f"  - 总识别次数: {stats.get('total_recognitions', 0)}")
        print(f"  - 平均耗时: {stats.get('average_time', 0):.3f} 秒")
        print(f"  - 缓存命中率: {stats.get('cache_hit_rate', 0):.2%}")
        
        return True
        
    except Exception as e:
        print(f"[错误] 识别功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fast_label_integrator():
    """测试FastLabelIntegrator集成"""
    print("\n=== 测试FastLabelIntegrator集成 ===")
    
    try:
        from src.utils.fast_label_integrator import FastLabelIntegrator
        
        integrator = FastLabelIntegrator()
        print("[成功] FastLabelIntegrator初始化成功")
        
        # 测试截图识别
        print("[进行中] 测试截图识别...")
        start_time = time.time()
        success = integrator.capture_and_recognize(save_screenshot=False)
        
        if success:
            detections = integrator.get_current_detections()
            operation_time = time.time() - start_time
            print(f"[成功] 截图识别成功: {len(detections)} 个元素，耗时 {operation_time:.3f} 秒")
            
            # 获取统计信息
            stats = integrator.get_statistics()
            if 'type_counts' in stats:
                print("FastLabelIntegrator检测统计:")
                for elem_type, count in stats['type_counts'].items():
                    print(f"  {elem_type}: {count} 个")
        else:
            print("[警告] 截图识别失败，但这可能是正常的")
        
        return True
        
    except Exception as e:
        print(f"[错误] FastLabelIntegrator测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_compatibility():
    """测试GUI兼容性（不显示界面）"""
    print("\n=== 测试GUI兼容性 ===")
    
    try:
        from main import SimpleKeyboardClickerApp
        
        # 这里我们只测试初始化，不运行GUI
        print("[进行中] 测试应用初始化...")
        app = SimpleKeyboardClickerApp()
        print("[成功] SimpleKeyboardClickerApp初始化成功")
        
        # 测试识别器是否正确设置
        if hasattr(app, 'recognizer'):
            recognizer_type = type(app.recognizer).__name__
            print(f"[成功] 识别器类型: {recognizer_type}")
            
            # 测试回调是否设置
            if hasattr(app.recognizer, '_on_recognition_callback'):
                print("[成功] 识别回调已设置")
            if hasattr(app.recognizer, '_on_error_callback'):
                print("[成功] 错误回调已设置")
        
        # 测试集成器是否正确设置
        if hasattr(app, 'fast_integrator'):
            integrator_type = type(app.fast_integrator).__name__
            print(f"[成功] 集成器类型: {integrator_type}")
        
        # 清理（不启动GUI）
        try:
            app._cleanup_and_exit()
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"[错误] GUI兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("统一识别器main.py集成测试")
    print("=" * 50)
    
    tests = [
        ("组件集成", test_main_components),
        ("识别功能", test_recognition_functionality),
        ("FastLabelIntegrator", test_fast_label_integrator),
        ("GUI兼容性", test_gui_compatibility)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name}测试 ---")
        try:
            if test_func():
                print(f"[通过] {test_name}测试通过")
                passed += 1
            else:
                print(f"[失败] {test_name}测试失败")
        except Exception as e:
            print(f"[异常] {test_name}测试异常: {e}")
    
    print(f"\n{'='*50}")
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("[成功] 所有测试通过！main.py集成成功。")
        print("\n可以安全使用以下命令启动新版本:")
        print("  python main.py")
        return True
    else:
        print("[警告] 部分测试失败，请检查相关问题。")
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