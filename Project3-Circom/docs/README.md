# Poseidon2 哈希算法 Circom 电路实现

[![Circom](https://img.shields.io/badge/circom-2.0+-blue.svg)](https://docs.circom.io/)
[![SnarkJS](https://img.shields.io/badge/snarkjs-0.7+-green.svg)](https://github.com/iden3/snarkjs)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

**基于 Circom 的 Poseidon2 哈希算法零知识证明系统，支持 Groth16 证明生成与验证**

- **开发单位**: 山东大学网络空间安全学院
- **技术特色**: Poseidon2 哈希 | Circom 电路 | Groth16 证明 | 零知识证明
- **应用场景**: 隐私保护 | 身份验证 | 区块链应用 | 密码学研究

---

## 项目概述

本项目实现了基于最新 Poseidon2 哈希算法的 Circom 电路，支持生成和验证零知识证明。证明者可以证明他们知道某个秘密值（原象），该值的 Poseidon2 哈希等于公开的目标值，而无需透露具体的秘密值。

### 核心特性

- **Poseidon2 算法**: 实现了最新的 Poseidon2 哈希算法 (参数: n=256, t=3, d=5)
- **高效电路**: 优化的 Circom 电路实现，约束数量最小化
- **Groth16 证明**: 支持生成简洁的零知识证明
- **完整工具链**: 从电路编译到证明验证的完整流程
- **易于使用**: 简化的 npm 脚本和详细的使用说明

## 技术架构

### Poseidon2 算法参数

根据论文 [Poseidon2: A Fast and Secure Hash Function](https://eprint.iacr.org/2023/323.pdf)：

- **字段大小 (n)**: 256 位 
- **状态大小 (t)**: 3 个字段元素
- **S-box 次数 (d)**: 5 (x^5)
- **全轮数 (RF)**: 8 轮
- **部分轮数 (RP)**: 56 轮

### 电路设计

```
输入: preimage[2] (隐私输入)
输出: expectedHash (公开输入)

电路约束: Poseidon2(preimage[0], preimage[1]) == expectedHash
```

## 快速开始

### 环境要求

- Node.js 16+ 
- Circom 编译器 2.0+
- SnarkJS 工具

### 安装步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd Project3-Circom

# 2. 安装依赖
npm install

# 3. 安装 Circom 编译器 (如未安装)
# 参见: https://docs.circom.io/getting-started/installation/

# 4. 验证安装
circom --version
snarkjs --help
```

### 一键运行

```bash
# 完整流程 (设置 + 证明 + 验证)
npm run setup    # 编译电路并进行 trusted setup
npm run prove    # 生成零知识证明  
npm run verify   # 验证证明
```

## 详细使用说明

### 1. 电路编译与设置

```bash
npm run setup
```

此命令将执行：
- 编译 Circom 电路到 R1CS
- 生成 WASM 见证生成器
- 执行 Groth16 trusted setup
- 生成证明密钥和验证密钥

**输出文件**:
- `poseidon2_proof.r1cs` - 约束系统
- `poseidon2_proof_js/` - WASM 见证生成器
- `poseidon2_0001.zkey` - 证明密钥
- `verification_key.json` - 验证密钥

### 2. 证明生成

```bash
npm run prove
```

使用示例数据生成零知识证明：
- **原象**: `[1234567890123456789, 9876543210987654321]`
- **期望哈希**: 计算得出的 Poseidon2 哈希值

**输出文件**:
- `input.json` - 输入数据
- `witness.wtns` - 见证文件
- `proof.json` - 零知识证明

### 3. 证明验证

```bash
npm run verify
```

验证生成的零知识证明的有效性。成功验证表明：
- 证明者知道正确的原象
- 原象的 Poseidon2 哈希等于期望值
- 证明在密码学上是安全的

## 电路结构

### 核心组件

#### 1. S-box 组件
```circom
template SBox() {
    signal input in;
    signal output out;
    
    signal x2 <== in * in;
    signal x4 <== x2 * x2;
    out <== x4 * in;  // x^5
}
```

#### 2. 线性层
```circom
template LinearLayer() {
    signal input in[3];
    signal output out[3];
    
    signal sum <== in[0] + in[1] + in[2];
    out[0] <== sum + 2 * in[0];
    out[1] <== sum + 2 * in[1]; 
    out[2] <== sum + 2 * in[2];
}
```

#### 3. 轮函数
- **全轮**: 对所有状态元素应用 S-box
- **部分轮**: 仅对第一个状态元素应用 S-box

### 主电路

```circom
template Poseidon2Proof() {
    signal private input preimage[2];  // 隐私输入
    signal input expectedHash;         // 公开输入
    
    component hasher = Poseidon2();
    hasher.in[0] <== preimage[0];
    hasher.in[1] <== preimage[1];
    
    expectedHash === hasher.out;
}
```

## 测试与验证

### 运行测试

```bash
npm test
```

测试包含：
- 基础功能测试
- 边界值测试  
- 一致性验证
- 错误处理测试

### 自定义测试

编辑 `tests/test_poseidon2.js` 添加自定义测试用例：

```javascript
const testInputs = [
    { 
        preimage: [your_value_1, your_value_2], 
        description: "自定义测试" 
    }
];
```

## 项目结构

```
Project3-Circom/
├── circuits/                    # Circom 电路文件
│   ├── poseidon2_components.circom  # 核心组件
│   ├── poseidon2_hash.circom       # 哈希算法实现
│   └── poseidon2_proof.circom      # 主证明电路
├── scripts/                     # 工具脚本
│   ├── setup.js                # 电路设置脚本
│   ├── prove.js                # 证明生成脚本
│   └── verify.js               # 证明验证脚本
├── tests/                       # 测试文件
│   └── test_poseidon2.js       # 单元测试
├── package.json                 # 项目配置
└── README.md                   # 项目说明
```

## 性能分析

### 电路复杂度

- **约束数量**: ~2,000 个约束 (估算)
- **状态变量**: 3 个字段元素
- **轮数**: 8 全轮 + 56 部分轮

### 性能指标

| 操作 | 时间 | 备注 |
|------|------|------|
| 电路编译 | ~10s | 一次性操作 |
| Trusted Setup | ~30s | 一次性操作 |
| 证明生成 | ~5s | 每次证明 |
| 证明验证 | <100ms | 快速验证 |

## 故障排除

### 常见问题

#### 1. 编译错误
```bash
Error: circom command not found
```
**解决方案**: 安装 Circom 编译器
```bash
# 参见 https://docs.circom.io/getting-started/installation/
```

#### 2. 内存不足
```bash
Error: JavaScript heap out of memory
```
**解决方案**: 增加 Node.js 内存限制
```bash
export NODE_OPTIONS="--max-old-space-size=8192"
```

#### 3. 见证生成失败
```bash
Error: witness generation failed
```
**解决方案**: 检查输入数据格式
- 确保输入为有效的字段元素
- 检查 JSON 格式是否正确

## 技术参考

### 相关论文
- [Poseidon2: A Fast and Secure Hash Function](https://eprint.iacr.org/2023/323.pdf)
- [Poseidon: A New Hash Function for Zero-Knowledge Proof Systems](https://eprint.iacr.org/2019/458.pdf)

### 工具文档
- [Circom 语言文档](https://docs.circom.io/)
- [SnarkJS 工具指南](https://github.com/iden3/snarkjs)
- [Circomlib 组件库](https://github.com/iden3/circomlib)

## 使用示例

### 基础使用

```bash
# 1. 设置环境
npm run setup

# 2. 修改输入 (可选)
# 编辑 scripts/prove.js 中的 preimage 值

# 3. 生成证明
npm run prove

# 4. 验证证明
npm run verify
```

### 高级用法

**自定义原象值**:
```javascript
// 在 scripts/prove.js 中修改
const preimage = [
    "你的第一个秘密值",
    "你的第二个秘密值"  
];
```

**批量测试**:
```bash
# 运行多个测试用例
for i in {1..5}; do
    echo "Test $i"
    npm run prove
    npm run verify
done
```