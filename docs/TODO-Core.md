# 核心业务逻辑模块 TODO (Core Module)

**模块路径**: `src/core/`  
**优先级**: P0 (最高)  
**预估工期**: 4天  

## 概述
核心业务逻辑模块负责实现网格坐标系统的核心算法和状态管理，是整个系统的"大脑"。

---

## #region 架构设计 (第1天)

### ✅ 核心模块架构定义
- [ ] **GridCoordinateSystem** - 网格坐标系统主控制器
  - [ ] 定义网格状态枚举 (Inactive, Active, Processing)
  - [ ] 实现状态转换逻辑
  - [ ] 提供统一的网格操作接口

- [ ] **GridCalculator** - 网格计算引擎
  - [ ] 3x3网格区域计算算法
  - [ ] 递归分割区域计算
  - [ ] 坐标转换工具方法

- [ ] **InputProcessor** - 输入处理器
  - [ ] 九宫格按键映射 (`QWEASDZXC`)
  - [ ] 指令后缀解析 (`R`, `H`)
  - [ ] 按键路径状态管理

- [ ] **CommandExecutor** - 指令执行器
  - [ ] 默认左键单击指令
  - [ ] 右键单击指令 (`R`后缀)
  - [ ] 悬停/移动指令 (`H`后缀)

### ✅ 接口定义
- [ ] `IGridRenderer` - 网格渲染接口
- [ ] `IInputListener` - 输入监听接口  
- [ ] `IMouseController` - 鼠标控制接口
- [ ] `ISystemHook` - 系统钩子接口

---

## #region 递归定位系统 (第2天)

### ✅ GridCalculator 实现
- [ ] **基础网格计算**
  - [ ] `CalculateGrid3x3(screenRect)` - 计算3x3网格区域
  - [ ] `GetGridCell(gridIndex, cellIndex)` - 获取指定网格单元
  - [ ] `GetCellCenter(cellRect)` - 获取单元格中心点

- [ ] **递归计算引擎**
  - [ ] `ProcessKeyPath(keySequence)` - 处理按键路径
  - [ ] `RecursiveSubdivide(currentRect, keyIndex)` - 递归细分区域
  - [ ] `ValidateKeySequence(keys)` - 验证按键序列有效性

### ✅ 状态管理系统
- [ ] **GridState 类**
  - [ ] `CurrentLevel` - 当前递归层级
  - [ ] `KeyPath` - 当前按键路径
  - [ ] `ActiveRegion` - 当前活跃区域
  - [ ] `IsProcessing` - 处理状态标志

- [ ] **状态转换方法**
  - [ ] `StartNewSession()` - 开始新的定位会话
  - [ ] `ProcessKeyInput(key)` - 处理按键输入
  - [ ] `ResetSession()` - 重置会话状态

---

## #region 指令系统 (第3天)

### ✅ InputProcessor 实现
- [ ] **按键映射系统**
  - [ ] 创建九宫格按键映射字典
  - [ ] 实现按键到网格索引的转换
  - [ ] 处理无效按键输入

- [ ] **指令解析引擎**
  - [ ] `ParseCommand(keySequence)` - 解析指令类型
  - [ ] `ExtractCommandSuffix(keys)` - 提取指令后缀
  - [ ] `ValidateCommand(command)` - 验证指令有效性

### ✅ CommandExecutor 实现
- [ ] **默认左键单击** (最高优先级)
  - [ ] `ExecuteDefaultClick(targetPoint)` - 执行默认点击
  - [ ] 自动退出网格模式
  - [ ] 点击后状态清理

- [ ] **右键单击指令**
  - [ ] `ExecuteRightClick(targetPoint)` - 执行右键点击
  - [ ] `R`后缀识别与处理
  - [ ] 右键菜单等待机制

- [ ] **悬停/移动指令**
  - [ ] `ExecuteHover(targetPoint)` - 执行悬停操作
  - [ ] `H`后缀识别与处理
  - [ ] 仅移动光标，不执行点击

---

## #region 集成与优化 (第4天)

### ✅ 核心控制器集成
- [ ] **GridCoordinateSystem 主控制器**
  - [ ] 集成所有子模块
  - [ ] 实现完整的操作流程
  - [ ] 异常处理与错误恢复

### ✅ 性能优化
- [ ] **响应速度优化**
  - [ ] 确保按键响应时间 < 50ms
  - [ ] 优化坐标计算算法
  - [ ] 减少不必要的对象创建

- [ ] **内存管理**
  - [ ] 实现对象池模式 (如需要)
  - [ ] 及时释放临时对象
  - [ ] 避免内存泄漏

### ✅ 错误处理
- [ ] **异常捕获机制**
  - [ ] 坐标计算异常处理
  - [ ] 无效输入处理
  - [ ] 系统调用失败处理

---

## 验收标准

### 功能完整性
- [x] 所有核心算法正确实现
- [x] 递归定位准确无误
- [x] 三种指令操作正常工作

### 性能指标
- [x] 按键响应延迟 < 50ms
- [x] 坐标计算精度 100%
- [x] 连续操作稳定性

### 代码质量
- [x] 代码符合Python PEP8规范
- [x] 变量命名遵循约定 (私有变量 `_abc`, 公共 `Abc`)
- [x] 使用 `#region` `#endregion` 组织代码
- [x] 所有公共方法有文档注释

---

## 测试要求

### 单元测试覆盖率
- [ ] GridCalculator: 100%
- [ ] InputProcessor: 100%  
- [ ] CommandExecutor: 100%
- [ ] GridCoordinateSystem: 100%

### 集成测试
- [ ] 完整操作流程测试
- [ ] 边界条件测试
- [ ] 异常情况测试

---

**依赖关系**: 无 (基础模块)  
**被依赖**: platform模块, ui模块  
**风险等级**: 低 (纯逻辑计算)