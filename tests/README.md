# KeyboardClicker 测试说明

本目录包含 KeyboardClicker 项目的所有测试代码，为核心业务逻辑提供全面的质量保证。

## 测试结构

```
tests/
├── core/                        # 核心模块测试
│   ├── test_grid_calculator.py      # 网格计算器测试
│   ├── test_input_processor.py      # 输入处理器测试
│   ├── test_command_executor.py     # 指令执行器测试
│   ├── test_grid_coordinate_system.py # 坐标系统测试
│   ├── test_integration.py          # 集成测试
│   └── __init__.py
├── platform/                   # 平台层测试 (待实现)
├── ui/                         # UI层测试 (待实现)  
├── run_tests.py                # 测试运行器
├── TEST_COVERAGE_REPORT.md     # 覆盖率报告
└── README.md                   # 本文件
```

## 快速开始

### 环境要求

```bash
# 安装测试依赖
pip install pytest pytest-cov PyQt6 pynput
```

### 运行所有核心测试

```bash
# 方法1: 使用自定义测试运行器
python tests/run_tests.py --core

# 方法2: 使用pytest
python -m pytest tests/core/ -v

# 方法3: 使用pytest并生成覆盖率报告
python -m pytest tests/core/ --cov=src.core --cov-report=term --cov-report=html -v
```

### 运行特定测试

```bash
# 运行单个测试文件
python -m pytest tests/core/test_grid_calculator.py -v

# 运行特定测试类
python -m pytest tests/core/test_grid_calculator.py::TestGrid3x3Calculation -v

# 运行特定测试方法
python -m pytest tests/core/test_grid_calculator.py::TestGrid3x3Calculation::test_CalculateGrid3x3_正常区域 -v
```

### 生成详细报告

```bash
# 生成HTML覆盖率报告
python -m pytest tests/core/ --cov=src.core --cov-report=html

# 使用自定义运行器生成报告文件
python tests/run_tests.py --core --report=test_report.txt
```

## 测试模块详解

### 1. GridCalculator 测试 (`test_grid_calculator.py`)

测试网格计算引擎的所有功能：

- **网格计算**: 3x3网格分割、单元格尺寸、位置映射
- **按键映射**: 九宫格按键与索引的双向转换
- **路径处理**: 递归路径计算、目标点定位
- **验证功能**: 按键序列验证、区域可分性检查
- **边界条件**: 极小/极大区域处理、负坐标处理
- **性能测试**: 大量计算和复杂路径处理性能

**测试用例数**: 45个  
**覆盖率**: 99%

### 2. InputProcessor 测试 (`test_input_processor.py`)

测试输入处理器的所有功能：

- **按键验证**: 有效网格键、控制键、指令后缀识别
- **指令解析**: 默认点击、右键点击、悬停指令解析
- **后缀提取**: R/H后缀的正确识别和提取
- **状态一致性**: 多次解析的一致性验证
- **边界条件**: 长序列、特殊字符、Unicode处理
- **性能测试**: 大量解析和长序列处理性能

**测试用例数**: 47个  
**覆盖率**: 99%

### 3. CommandExecutor 测试 (`test_command_executor.py`)

测试指令执行器的所有功能：

- **三种操作**: 左键点击、右键点击、悬停操作
- **错误处理**: 控制器异常、无效指令处理
- **回调机制**: 执行完成回调的正确触发
- **能力检查**: 指令可执行性验证
- **集成流程**: 完整的指令执行工作流程
- **性能测试**: 大量执行和不同指令类型性能

**测试用例数**: 43个  
**覆盖率**: 93%

### 4. GridCoordinateSystem 测试 (`test_grid_coordinate_system.py`)

测试主控制器的所有功能：

- **会话管理**: 启动、结束、状态转换
- **按键处理**: 有效/无效按键、ESC退出
- **指令执行**: 三种指令类型的完整执行
- **热键处理**: Alt+G激活/取消激活
- **事件回调**: 各种事件的回调机制
- **错误处理**: 异常情况的优雅处理
- **性能测试**: 响应时间和处理性能

**测试用例数**: 31个  
**覆盖率**: 94%

### 5. 集成测试 (`test_integration.py`)

测试模块间协作：

- **模块集成**: 计算器与处理器、处理器与执行器等
- **端到端流程**: 完整的用户操作流程测试
- **性能集成**: 跨模块的性能测试
- **边界条件**: 极限情况下的模块协作
- **兼容性测试**: 接口一致性验证

**测试用例数**: 14个

## 测试质量保证

### 测试设计原则

1. **独立性**: 每个测试用例相互独立，不依赖执行顺序
2. **可重复**: 测试结果稳定，多次运行结果一致
3. **全面性**: 覆盖正常路径、边界条件、异常情况
4. **性能**: 包含响应时间和吞吐量验证
5. **可维护**: 使用Mock对象，减少外部依赖

### Mock策略

所有测试都使用Mock对象来模拟外部依赖：

- **MockMouseController**: 模拟鼠标操作
- **MockGridRenderer**: 模拟网格渲染
- **MockInputListener**: 模拟输入监听
- **MockSystemHook**: 模拟系统钩子

这确保了测试的：
- 快速执行（无实际UI/系统调用）
- 稳定性（不受外部环境影响）
- 可控性（能模拟各种场景）

### 断言策略

每个测试都包含充分的断言：

- **状态验证**: 检查对象状态的正确变更
- **行为验证**: 验证方法调用和参数
- **结果验证**: 确认返回值的正确性
- **性能验证**: 检查操作耗时在预期范围内

## 性能基准

所有性能测试都基于以下基准：

- **按键响应**: < 50ms
- **网格计算**: 1000次 < 1秒
- **指令解析**: 1000次 < 0.1秒
- **完整流程**: 单次操作 < 50ms

## 持续集成

测试设计支持CI/CD流程：

- 无外部依赖（完全Mock化）
- 快速执行（总时间 < 1秒）
- 稳定结果（100%通过率）
- 详细报告（覆盖率 + 性能数据）

## 扩展测试

### 添加新测试

1. 在相应的测试文件中添加测试类
2. 遵循命名约定：`Test[功能名称]`
3. 使用合适的Mock对象
4. 包含正常、边界、异常情况
5. 添加性能验证（如适用）

### 测试文件模板

```python
import unittest
from unittest.mock import Mock
from src.core.your_module import YourClass

class TestYourFeature(unittest.TestCase):
    def setUp(self):
        self.mock_dependency = Mock()
        self.your_object = YourClass(self.mock_dependency)
    
    def test_正常情况(self):
        # 准备
        # 执行  
        # 验证
        pass
    
    def test_边界条件(self):
        pass
        
    def test_异常处理(self):
        pass
```

## 故障排除

### 常见问题

1. **ImportError**: 确保src目录在Python路径中
2. **ModuleNotFoundError**: 检查依赖是否已安装
3. **测试失败**: 查看详细错误信息，检查Mock设置

### 调试技巧

```bash
# 运行单个失败的测试，显示详细信息
python -m pytest tests/core/test_file.py::TestClass::test_method -v -s

# 在测试中添加断点
import pdb; pdb.set_trace()

# 显示print输出
python -m pytest tests/core/ -s
```

## 贡献指南

添加或修改测试时：

1. 确保新测试通过
2. 维持或提高覆盖率
3. 遵循现有的命名和组织规范
4. 更新相关文档
5. 运行完整测试套件验证没有破坏现有功能

---

**更多信息**: 参见 `TEST_COVERAGE_REPORT.md` 获取详细的覆盖率分析。