# Poseidon2 快速开始指南

## 一键运行

```bash
# 1. 安装依赖
npm install

# 2. 运行完整演示 (推荐)
npm run demo
```

## 分步执行

```bash
# 1. 编译电路并设置 Groth16
npm run setup

# 2. 生成零知识证明
npm run prove  

# 3. 验证证明
npm run verify

# 4. 运行测试
npm test
```

## 环境要求

- **Node.js**: 16+ 
- **Circom**: 2.0+ ([安装指南](https://docs.circom.io/getting-started/installation/))
- **SnarkJS**: 自动安装

## 安装 Circom

### Windows
```bash
# 使用预编译二进制文件
curl -L https://github.com/iden3/circom/releases/latest/download/circom-windows-amd64.tar.gz -o circom.tar.gz
tar -xzf circom.tar.gz
# 将 circom.exe 添加到 PATH
```

### Linux/macOS
```bash
# 使用 Rust 编译安装
curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh
source ~/.cargo/env
git clone https://github.com/iden3/circom.git
cd circom
cargo build --release
cargo install --path circom
```

## 自定义输入

编辑 `scripts/prove.js`:
```javascript
const preimage = [
    "你的第一个秘密值",
    "你的第二个秘密值"
];
```

## 输出文件

- `proof.json` - 零知识证明
- `input.json` - 输入数据  
- `verification_key.json` - 验证密钥
- `witness.wtns` - 见证文件

## 故障排除

| 错误 | 解决方案 |
|------|----------|
| `circom: command not found` | 安装 Circom 编译器 |
| `JavaScript heap out of memory` | 增加 Node.js 内存限制 |
| `witness generation failed` | 检查输入数据格式 |

## 更多信息

查看 [README.md](README.md) 获取完整文档和技术细节。

---

**提示**: 第一次运行 `npm run demo` 会自动执行所有必要的设置步骤。 