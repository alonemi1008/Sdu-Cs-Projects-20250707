# Google Password Checkup 协议实现

## 项目概述

本项目实现了Google Password Checkup协议，基于论文"Protecting accounts from credential stuffing with password breach alerting"（https://eprint.iacr.org/2019/723.pdf）中Section 3.1和Figure 2描述的协议。

该协议允许用户以隐私保护的方式检查其用户名和密码组合是否在已知的数据泄露中出现，而不会向服务器透露被查询的具体凭证信息。

## 协议数学基础

### 1. 私有集合交集(PSI)理论

#### 1.1 问题定义

设客户端持有集合X = {x₁, x₂, ..., xₘ}，服务器持有集合Y = {y₁, y₂, ..., yₙ}，PSI协议允许双方计算交集X ∩ Y，而不泄露各自集合的其他信息。

#### 1.2 安全性定义

PSI协议需要满足：
- **正确性**: 协议输出正确的交集
- **隐私性**: 除交集外，双方不获得对方集合的其他信息
- **半诚实安全**: 抵抗半诚实敌手攻击

### 2. 椭圆曲线盲化协议

#### 2.1 椭圆曲线群设置

选择椭圆曲线E(F_p)，其中p为大素数，群阶为q。设G为群的生成元。

#### 2.2 盲化过程

**客户端盲化**：
```
输入：凭证哈希h
选择随机数a ∈ [1, q-1]
计算：α = H₁(h) · G
输出：β = a · α
```

**服务器盲化**：
```
输入：客户端盲化值β
使用服务器密钥b
计算：γ = b · β
输出：γ
```

**客户端解盲化**：
```
输入：服务器响应γ
计算：δ = a⁻¹ · γ = b · H₁(h) · G
```

#### 2.3 安全性分析

协议安全性基于椭圆曲线离散对数问题(ECDLP)的困难性：
给定点P和Q = kP，计算k在计算上是困难的。

### 3. Argon2密钥派生函数

#### 3.1 算法结构

Argon2采用内存困难函数设计，参数包括：
- m: 内存成本(KB)
- t: 时间成本(迭代次数)  
- p: 并行度
- τ: 输出长度

#### 3.2 数学定义

**初始化**：
```
H₀ = H(P || S || K || X || m || t || p || τ)
B₀ = H₀[0..1023], B₁ = H₀[1024..2047]
```

**内存填充**：
```
for i = 2 to m-1:
    if i mod p == 0:
        j = i - 2
    else:
        j = Φ(B[i-1])  // 伪随机函数
    B[i] = G(B[i-1], B[j])  // 压缩函数
```

**最终哈希**：
```
C = B[m-1]
for i = m-2 down to 0:
    C = G(C, B[i])
return H'(C)[0..τ-1]
```

#### 3.3 抗攻击分析

**时间-内存权衡攻击抗性**：
攻击者使用内存M < m时，时间复杂度增加至少(m/M)倍。

**并行攻击抗性**：
即使使用p个并行处理器，攻击时间仍需t次迭代。

### 4. K-匿名性保证

#### 4.1 定义

K-匿名性确保每次查询返回至少k个候选项，使得真实查询项隐藏在k个项目中。

#### 4.2 数学表示

设查询项为q，返回集合为S，则：
```
|S| ≥ k
q ∈ S
∀s ∈ S: Pr[s是真实查询] = 1/|S|
```

#### 4.3 隐私保护级别

信息泄露量化：
```
I(Q; S) = H(Q) - H(Q|S) ≤ log₂(k)
```

其中H(·)为信息熵。

### 5. 协议安全性证明

#### 5.1 威胁模型

考虑半诚实敌手模型：
- 敌手遵循协议执行
- 敌手试图从协议执行中推断额外信息

#### 5.2 模拟器构造

**客户端模拟器Sim_C**：
```
输入：客户端输入x，交集I
1. 选择随机椭圆曲线点R
2. 模拟服务器响应包含|I|个随机点
3. 输出模拟视图
```

**服务器模拟器Sim_S**：
```
输入：服务器输入Y，交集大小|I|
1. 生成|I|个随机椭圆曲线点
2. 模拟客户端查询为随机点
3. 输出模拟视图
```

#### 5.3 不可区分性

对于任何多项式时间区分器D：
```
|Pr[D(View_C) = 1] - Pr[D(Sim_C) = 1]| ≤ negl(λ)
|Pr[D(View_S) = 1] - Pr[D(Sim_S) = 1]| ≤ negl(λ)
```

其中λ为安全参数。

### 协议流程图

上图展示了完整的Google Password Checkup协议流程，包括数据库创建、客户端查询、服务器处理和客户端验证四个主要阶段。

### 协议流程

1. **数据库创建阶段**:
   - 标准化用户名（去除邮箱后缀，转小写）
   - 使用Argon2对凭证进行慢哈希
   - 使用椭圆曲线进行盲化
   - 按哈希前缀分片存储

2. **客户端查询阶段**:
   - 客户端生成随机盲化密钥a
   - 对查询凭证进行Argon2哈希
   - 使用密钥a进行椭圆曲线盲化
   - 发送盲化哈希和前缀到服务器

3. **服务器响应阶段**:
   - 使用服务器密钥b对客户端盲化哈希进行双重盲化
   - 返回匹配前缀的所有凭证分片
   - 客户端无法知道其他凭证内容

4. **客户端验证阶段**:
   - 客户端解盲化响应数据
   - 检查自己的凭证是否在响应集合中
   - 确定是否存在泄露

## 文件结构

```
Project6-Googlecheck/
├── src/                         # 核心源代码
│   ├── crypto/
│   │   ├── elliptic_curve.py    # 椭圆曲线加密实现
│   │   ├── argon2_hash.py       # Argon2哈希实现
│   │   └── psi_protocol.py      # 私有集合交集协议
│   ├── database/
│   │   ├── breach_db.py         # 泄露数据库管理
│   │   └── shard_manager.py     # 分片管理器
│   ├── client/
│   │   └── password_checker.py  # 客户端查询实现
│   ├── server/
│   │   └── checkup_server.py    # 服务器端实现
│   └── utils/
│       ├── canonicalize.py      # 用户名标准化
│       └── constants.py         # 常量定义
├── demo/                        # 演示程序
│   ├── demo_client.py           # 演示客户端
│   ├── demo_server.py           # 演示服务器
│   └── sample_data.py           # 示例数据生成
├── docs/                        # 文档
│   ├── USAGE_GUIDE.md           # 使用指南
│   ├── PROJECT_SUMMARY.md       # 项目总结
│   └── PROJECT_COMPLETION_SUMMARY.md  # 项目完成总结
├── tests/                       # 测试文件
│   └── test_crypto.py           # 加密功能测试
├── requirements.txt             # 依赖包列表
├── run_demo.py                  # 快速演示脚本
└── README.md                    # 项目说明
```

## 安全特性

- **零知识**: 服务器无法知道客户端查询的具体凭证
- **抗暴力破解**: Argon2哈希使暴力破解成本极高
- **k-匿名性**: 每次查询都在大量候选凭证中进行
- **侧信道防护**: 固定时间运算，防止时序攻击

## 性能指标

- 典型查询延迟: 8-26秒（包含Argon2计算）
- 网络传输: 约1MB每次查询
- 内存使用: 256MB（Argon2参数）
- 计算复杂度: ~1秒Argon2哈希时间

## 使用方法

### 基本使用

```python
from src.client.password_checker import PasswordChecker

# 创建客户端
checker = PasswordChecker()

# 检查凭证
username = "user@example.com"
password = "password123"
is_breached = checker.check_credentials(username, password)

if is_breached:
    print("警告: 该凭证已在数据泄露中发现!")
else:
    print("该凭证未在已知泄露中发现")
```

### 运行演示

```bash
# 快速演示（推荐）
python run_demo.py

# 或者手动启动服务器和客户端
python demo/demo_server.py --setup-demo --port 8080
python demo/demo_client.py --server http://localhost:8080
```

## 技术实现细节

### 椭圆曲线参数
- 曲线: secp224r1
- 密钥长度: 224位
- 点压缩: 支持

### Argon2参数
- 内存成本: 256MB
- 时间成本: 3次迭代
- 并行度: 1
- 输出长度: 16字节

### 分片策略
- 分片数量: 65536 (2^16)
- 分片键: 哈希前2字节
- 平均分片大小: ~61KB

## 依赖要求

- Python 3.7+
- cryptography>=3.4.8
- argon2-cffi>=21.3.0
- requests>=2.25.1

## 安装运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
python tests/test_crypto.py

# 快速演示
python run_demo.py

# 查看详细文档
# docs/USAGE_GUIDE.md - 详细使用指南
# docs/PROJECT_SUMMARY.md - 项目技术总结
```

## 参考文献

- Thomas, K. et al. "Protecting accounts from credential stuffing with password breach alerting." USENIX Security Symposium, 2019.
- https://eprint.iacr.org/2019/723.pdf 