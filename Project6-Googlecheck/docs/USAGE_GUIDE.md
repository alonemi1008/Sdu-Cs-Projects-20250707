# Google Password Checkup 使用指南

## 概述

本指南将帮助您快速上手Google Password Checkup协议的实现。该协议允许用户以隐私保护的方式检查其凭证是否在已知的数据泄露中出现。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行演示

最简单的方式是运行快速演示：

```bash
python run_demo.py
```

这将自动启动服务器并运行客户端演示。

### 3. 手动运行

如果您想要更多控制，可以分别启动服务器和客户端：

```bash
# 启动服务器（包含演示数据）
python demo/demo_server.py --setup-demo --port 8080

# 在另一个终端运行客户端
python demo/demo_client.py --server http://localhost:8080
```

## 详细使用说明

### 服务器端

#### 启动服务器

```bash
python demo/demo_server.py [选项]
```

可用选项：
- `--setup-demo`: 设置演示数据库
- `--port PORT`: 指定端口号（默认8080）
- `--host HOST`: 指定主机地址（默认localhost）

#### 服务器API

服务器提供以下REST API端点：

- `GET /health`: 健康检查
- `GET /info`: 服务器信息
- `GET /statistics`: 数据库统计信息
- `POST /query`: 密码查询（核心功能）

### 客户端

#### 命令行客户端

```bash
python demo/demo_client.py [选项]
```

可用选项：
- `--server URL`: 服务器地址（默认http://localhost:8080）
- `--interactive`: 交互模式
- `--batch FILE`: 批量查询模式

#### 编程接口

```python
from src.client.password_checker import PasswordChecker

# 创建客户端
checker = PasswordChecker(server_url="http://localhost:8080")

# 检查单个凭证
result = checker.check_credentials("user@example.com", "password123")
if result.is_breached:
    print(f"警告: 凭证已泄露!")
    print(f"匹配的泄露事件: {result.breach_names}")
else:
    print("凭证安全")

# 批量检查
credentials = [
    ("user1@example.com", "password1"),
    ("user2@example.com", "password2")
]
results = checker.check_credentials_batch(credentials)
for cred, result in zip(credentials, results):
    print(f"{cred[0]}: {'已泄露' if result.is_breached else '安全'}")
```

## 协议细节

### 数据流程

1. **客户端准备**: 
   - 标准化用户名（移除邮箱后缀，转小写）
   - 使用Argon2进行慢哈希
   - 使用椭圆曲线进行盲化

2. **服务器处理**:
   - 接收盲化的查询
   - 进行双重盲化
   - 返回匹配分片的所有凭证

3. **客户端验证**:
   - 解盲化服务器响应
   - 检查自己的凭证是否在结果中

### 安全特性

- **零知识**: 服务器不知道客户端查询的具体凭证
- **k-匿名性**: 每次查询返回多个候选凭证
- **抗暴力破解**: Argon2哈希增加破解成本
- **侧信道防护**: 固定时间运算

## 配置选项

### Argon2参数

```python
# 在 src/crypto/argon2_hash.py 中配置
ARGON2_MEMORY_COST = 256 * 1024  # 256MB
ARGON2_TIME_COST = 3             # 3次迭代
ARGON2_PARALLELISM = 1           # 单线程
```

### 椭圆曲线参数

```python
# 在 src/crypto/elliptic_curve.py 中配置
CURVE = ec.SECP224R1()           # 使用secp224r1曲线
```

### 分片配置

```python
# 在 src/database/shard_manager.py 中配置
SHARD_PREFIX_LENGTH = 2          # 使用2字节前缀
TOTAL_SHARDS = 65536            # 总共65536个分片
```

## 性能优化

### 客户端优化

1. **批量查询**: 使用批量API减少网络往返
2. **缓存结果**: 避免重复查询相同凭证
3. **异步处理**: 使用异步HTTP客户端

### 服务器优化

1. **内存映射**: 使用内存映射文件加速数据库访问
2. **连接池**: 配置HTTP连接池
3. **缓存策略**: 缓存热点分片数据

## 故障排除

### 常见问题

1. **导入错误**: 确保所有依赖都已安装
2. **端口冲突**: 更改服务器端口
3. **内存不足**: 调整Argon2内存参数
4. **网络超时**: 增加HTTP超时时间

### 调试模式

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 性能分析

使用内置的性能分析工具：

```bash
python -m cProfile demo/demo_client.py
```

## 参考资料

- [原始论文](https://eprint.iacr.org/2019/723.pdf)
- [Argon2规范](https://tools.ietf.org/html/rfc9106)
- [椭圆曲线密码学](https://tools.ietf.org/html/rfc6090)
- [私有集合交集](https://en.wikipedia.org/wiki/Private_set_intersection) 