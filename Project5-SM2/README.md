# SM2 椭圆曲线密码算法实现

## 项目概述

本项目实现了SM2椭圆曲线密码算法的完整功能，包括基础版本和多种优化版本。SM2是中国国家密码管理局发布的椭圆曲线公钥密码算法，广泛应用于数字签名、密钥交换和公钥加密等领域。

## 文件结构

```
Project5-SM2/
├── src/                          # 源代码目录
│   ├── __init__.py
│   ├── core/                     # 核心算法实现
│   │   ├── __init__.py
│   │   ├── sm2_basic.py         # SM2基础实现
│   │   └── sm2_optimized.py     # SM2优化实现
│   └── protocols/               # 协议实现
│       ├── __init__.py
│       ├── sm2_signature_protocol.py  # SM2签名协议
│       └── sm2_key_exchange.py        # SM2密钥交换协议
├── tests/                       # 测试文件
│   ├── __init__.py
│   └── test_sm2.py             # 基础测试
├── examples/                    # 示例和演示
│   ├── sm2_protocols_demo.py   # 协议演示程序
│   └── performance_test.py     # 性能测试
├── docs/                       # 文档目录
├── results/                    # 结果输出目录
│   └── sm2_performance_results.json  # 性能测试结果
├── main.py                     # 主程序
├── run_demo.py                 # 演示启动器
├── README.md                   # 项目说明
└── requirements.txt            # 依赖说明
```

## 核心功能

### 1. 基础功能 (sm2_basic.py)

- **椭圆曲线点运算**: 点加法、点倍乘、标量乘法
- **密钥生成**: 生成SM2密钥对
- **加密解密**: 基于椭圆曲线的公钥加密
- **数字签名**: SM2数字签名生成和验证
- **密钥派生**: KDF密钥派生函数

### 2. 优化功能 (sm2_optimized.py)

- **NAF算法**: 非邻接形式的点乘法优化
- **滑动窗口法**: 减少点加法运算次数
- **蒙哥马利阶梯**: 抗侧信道攻击的点乘法
- **预计算表**: 基点的预计算优化
- **同时点乘法**: Shamir's trick优化
- **快速模逆**: 费马小定理优化模逆元计算

### 3. 性能测试 (performance_test.py)

- **全面基准测试**: 涵盖所有核心操作
- **统计分析**: 平均值、中位数、标准差等统计指标
- **算法对比**: 不同优化算法的性能比较
- **结果保存**: 测试结果自动保存为JSON格式

## 快速开始

### 基本使用

```python
from src.core.sm2_basic import SM2Basic

# 创建SM2实例
sm2 = SM2Basic()

# 生成密钥对
private_key, public_key = sm2.generate_keypair()

# 加密消息
message = b"Hello, SM2!"
ciphertext = sm2.encrypt(message, public_key)

# 解密消息
decrypted = sm2.decrypt(ciphertext, private_key)

# 数字签名
signature = sm2.sign(message, private_key)
is_valid = sm2.verify(message, signature, public_key)
```

### 优化版本使用

```python
from src.core.sm2_optimized import SM2Optimized

# 创建优化版本的SM2实例
sm2 = SM2Optimized()

# 使用相同的API，但性能更好
private_key, public_key = sm2.generate_keypair()
ciphertext = sm2.encrypt(message, public_key)
signature = sm2.sign(message, private_key)

# 使用优化的验证函数
is_valid = sm2.verify_optimized(message, signature, public_key)
```

## 运行演示

### 1. 基础功能演示

```bash
python main.py basic
```

### 2. 优化功能演示

```bash
python main.py optimized
```

### 3. 性能对比

```bash
python main.py performance
```

### 4. 交互式演示

```bash
python main.py interactive
```

### 5. 完整性能测试

```bash
python main.py full-test
```

### 6. 综合演示（默认）

```bash
python main.py
```

## 性能优化技术

### 1. NAF (Non-Adjacent Form) 算法

- 减少点加法运算次数
- 适用于大数标量乘法
- 平均减少33%的非零位

### 2. 滑动窗口法

- 预计算奇数倍数
- 减少点加法操作
- 窗口大小可调节

### 3. 蒙哥马利阶梯

- 抗侧信道攻击
- 固定的运算模式
- 适用于安全要求高的场景

### 4. 预计算表

- 基点G的倍数预计算
- 显著加速基点标量乘法
- 内存换时间的优化策略

### 5. 同时点乘法

- Shamir's trick算法
- 优化签名验证过程
- 减少约25%的运算时间

## 性能基准测试

典型测试结果（具体数值因硬件而异）：

| 操作类型 | 基础版本 | 优化版本 | 加速比 |
|---------|---------|---------|-------|
| 点乘法 | 0.0234s | 0.0089s | 2.63x |
| 密钥生成 | 0.0245s | 0.0092s | 2.66x |
| 签名验证 | 0.0456s | 0.0178s | 2.56x |
| 加密操作 | 0.0289s | 0.0112s | 2.58x |

## 技术规格

- **椭圆曲线**: SM2推荐曲线参数
- **有限域**: 256位素数域
- **哈希函数**: SHA-256
- **密钥长度**: 256位
- **签名长度**: 64字节 (r: 32字节, s: 32字节)

## 安全特性

- **抗量子攻击**: 基于椭圆曲线离散对数问题
- **侧信道防护**: 蒙哥马利阶梯算法
- **随机数安全**: 使用系统安全随机数生成器
- **参数验证**: 严格的输入参数检查


## 依赖要求

- Python 3.6+
- 标准库：hashlib, random, time, statistics, json
- 无外部依赖

## 开发和测试

### 运行单元测试

```bash
python -m pytest tests/
```

### 性能分析

```bash
python performance_test.py
```

### 代码覆盖率

```bash
python -m coverage run -m pytest tests/
python -m coverage report
```