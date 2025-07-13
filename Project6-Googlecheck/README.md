# Google Password Checkup 协议实现

## 项目概述

本项目实现了Google Password Checkup协议，基于论文"Protecting accounts from credential stuffing with password breach alerting"（https://eprint.iacr.org/2019/723.pdf）中Section 3.1和Figure 2描述的协议。

该协议允许用户以隐私保护的方式检查其用户名和密码组合是否在已知的数据泄露中出现，而不会向服务器透露被查询的具体凭证信息。

## 协议原理

### 核心技术

1. **K-匿名性**: 防止用户跟踪，每次查询返回一个盲化的凭证池
2. **私有集合交集(PSI)**: 确保服务器不知道客户端检查的具体凭证
3. **Argon2哈希**: 防止暴力破解攻击，保护静态密码
4. **椭圆曲线盲化**: 使用ECDH实现双重盲化

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

## 注意事项

1. 本实现仅用于教育和研究目的
2. 生产环境需要额外的安全审计
3. 需要大量计算资源处理真实规模的泄露数据库
4. 移动设备可能因计算和网络开销过大而不适用

## 参考文献

- Thomas, K. et al. "Protecting accounts from credential stuffing with password breach alerting." USENIX Security Symposium, 2019.
- https://eprint.iacr.org/2019/723.pdf 