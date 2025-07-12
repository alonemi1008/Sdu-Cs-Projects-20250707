# 山东大学密码学课程项目

**学号**：202200460089  
**姓名**：米文熙  
**GitHub仓库**：https://github.com/alonemi1008/Sdu-Cs-Projects-20250707

---

## 📋 项目总览

本仓库包含五个完整的密码学项目，涵盖对称密码、哈希函数、椭圆曲线密码、数字水印和零知识证明技术。

| 项目名称 | 技术领域 | 核心算法 | 主要效果 | 性能提升 | 文档链接 |
|---------|---------|---------|---------|---------|---------|
| [**Project1-SM4**](./Project1-SM4/) | 对称加密 | SM4分组密码 | 三种优化实现 | AES-NI最优 | [📖 详细说明](./Project1-SM4/readme.md) |
| [**Project2-Watermarked**](./Project2-Watermarked/) | 数字水印 | LSB/DCT/DWT-SVD | 版权保护与认证 | DCT推荐使用 | [📖 详细说明](./Project2-Watermarked/README.md) |
| [**Project3-Circom**](./Project3-Circom/) | 零知识证明 | Poseidon2+Groth16 | 隐私计算 | 400-500ms验证 | [📖 详细说明](./Project3-Circom/README.md) |
| [**Project4-SM3**](./Project4-SM3/) | 哈希函数 | SM3国密哈希 | 高性能实现 | 2.8x SIMD加速 | [📖 详细说明](./Project4-SM3/README.md) |
| [**Project5-SM2**](./Project5-SM2/) | 椭圆曲线密码 | SM2公钥算法 | 完整ECC实现 | 2.7x优化加速 | [📖 详细说明](./Project5-SM2/README.md) |

---

## 🎯 技术特色

### 🔐 密码算法优化 (Project1, Project4, Project5)
- **多层次优化**：从查表、SIMD到专用指令集的渐进式优化
- **性能提升显著**：SM4算法AES-NI优化效果最佳，SM3算法SIMD优化达到2.8x加速，SM2椭圆曲线算法优化达到2.7x加速
- **安全性考虑**：SM2实现包含抗侧信道攻击的安全措施

### 🖼️ 数字水印技术 (Project2)
- **算法多样性**：空域、频域、变换域三种技术路线
- **质量与鲁棒性平衡**：DCT算法在实际应用中表现最佳
- **可视化分析**：提供专业的攻击效果分析和性能评估

### 🔒 零知识证明应用 (Project3)
- **前沿技术**：基于最新Poseidon2哈希和Groth16证明系统
- **工程化实现**：自动化的电路编译和证明生成流程
- **实用性验证**：400-500ms的验证时间满足实际应用需求

---

## 📊 性能对比数据

### Project1-SM4 对称加密算法
| 优化方式 | 加密性能 | 特点 |
|---------|---------|------|
| 查表优化 | 中等 | 通过预计算S盒和T变换提高效率 |
| SIMD指令集 | 较高 | 使用向量指令并行处理多组数据 |
| AES-NI指令集 | **最高** | 利用Intel专用硬件加速指令 |

### Project2-Watermarked 数字水印算法
| 算法特性 | LSB算法 | DCT算法 (推荐) | DWT-DCT-SVD算法 |
|---------|---------|-----------|-----------------|
| **图像质量 (PSNR)** | 79.48 dB | 49.30 dB | 变化范围 |
| **鲁棒性测试** | 0% 成功率 | **100% 基础测试** | 70%+ 复杂攻击 |
| **推荐场景** | 教学演示 | **实际应用** | 高安全需求 |

### Project3-Circom 零知识证明系统
| 特性 | 实现效果 | 技术优势 |
|-----|---------|---------|
| **证明验证时间** | 400-500ms | 高效验证 |
| **电路编译** | 自动化设置 | 一键部署 |
| **应用场景** | 隐私计算 | 区块链应用 |

### Project4-SM3 哈希算法优化
| 数据大小 | 基础版本 (MB/s) | SIMD版本 (MB/s) | 加速比 | 特点 |
|---------|----------------|----------------|-------|------|
| 1KB | 45.2 | 58.7 | 1.3x | 基础性能验证 |
| 64KB | 156.8 | 234.2 | 1.5x | 中等数据处理 |
| 1MB | 234.5 | 387.9 | 1.7x | 大数据块处理 |
| 批量处理 | 51.2 | 107.0 | **2.1x** | 多块并行优化 |

### Project5-SM2 椭圆曲线密码算法
| 操作类型 | 基础版本 | 优化版本 | 加速比 | 优化技术 |
|---------|---------|---------|-------|---------|
| **点乘法** | 0.0234s | 0.0089s | 2.63x | NAF算法+滑动窗口 |
| **密钥生成** | 0.0245s | 0.0092s | **2.66x** | 预计算表优化 |
| **签名验证** | 0.0456s | 0.0178s | 2.56x | 同时点乘法 |
| **加密操作** | 0.0289s | 0.0112s | 2.58x | 蒙哥马利阶梯 |

---

## ⚙️ 环境要求

| 项目 | 编程语言 | 主要依赖 | 特殊要求 |
|-----|---------|---------|---------|
| [Project1-SM4](./Project1-SM4/) | C++11 | 标准库 | Intel处理器 (AES-NI) |
| [Project2-Watermarked](./Project2-Watermarked/) | Python 3.8+ | OpenCV, NumPy | 跨平台支持 |
| [Project3-Circom](./Project3-Circom/) | JavaScript | Node.js 16+, Circom | npm 8+ |
| [Project4-SM3](./Project4-SM3/) | C++ | GCC 4.9+ | SSE4.2指令集 |
| [Project5-SM2](./Project5-SM2/) | Python 3.6+ | 标准库 | 无外部依赖 |

---

## 🚀 快速开始

### Project1-SM4 对称加密算法
```bash
cd "Project1-SM4/sm4 with aes-ni"
g++ -O3 -std=c++11 -maes -mavx2 main.cpp sm4.cpp sm4_aesni.cpp -o sm4_aesni.exe
./sm4_aesni.exe
```

### Project2-Watermarked 数字水印系统
```bash
cd Project2-Watermarked
pip install -r requirements.txt
python run_demo.py
```

### Project3-Circom 零知识证明系统
```bash
cd Project3-Circom
npm install
npm run demo
```

### Project4-SM3 哈希算法
**Linux/macOS:**
```bash
cd Project4-SM3/sm3_basic
make test
```

**Windows:**
```cmd
cd Project4-SM3\sm3_basic
build.bat
```

### Project5-SM2 椭圆曲线密码算法
```bash
cd Project5-SM2
python main.py                  # 综合演示
python main.py basic           # 基础功能
python main.py optimized       # 优化功能
python main.py performance     # 性能测试
```

---

## 🎓 学术价值

### 教学应用
- **算法对比**：直观展示不同优化技术的效果
- **性能分析**：量化评估各种优化策略的收益
- **工程实践**：从理论到实现的完整过程

### 研究基础
- **模块化设计**：便于扩展新算法和评估方法
- **标准化接口**：统一的API设计便于算法替换
- **完整测试框架**：包含性能、安全性、可用性的综合评估

---

## 📈 项目统计

- **总提交数**：20+ commits
- **代码行数**：10,000+ lines
- **技术栈**：C++, Python, JavaScript, Circom
- **算法实现**：15+ 优化算法
- **性能测试**：100+ 基准测试用例

---

## 🏆 技术成果

**五大密码学方向完整覆盖**：

1. **🔐 SM4对称加密算法**：查表、SIMD、AES-NI多层次优化
2. **🔢 SM3哈希函数**：基础优化与SIMD并行计算  
3. **📈 SM2椭圆曲线密码**：完整ECC实现与多种优化算法
4. **🖼️ 数字水印技术**：空域、频域、变换域三种算法路线
5. **🔒 零知识证明系统**：基于Groth16的Poseidon2哈希证明

---

## 📞 联系信息

**作者**：米文熙  
**学号**：202200460089  
**院系**：山东大学网络空间安全学院  
**课程**：密码学原理与应用

---

## 📄 许可证

本项目仅用于学术研究和教学目的。

---

*最后更新：2025年1月* 