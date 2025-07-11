# 山东大学密码学课程项目

学号：202200460089  
姓名：米文熙

## 项目列表

### Project1-SM4
SM4分组密码算法的三种优化实现：
- 查表优化（Table-based）
- SIMD向量指令集优化
- AES-NI指令集优化

详细说明请见[Project1-SM4/readme.md](./Project1-SM4/readme.md)

### Project2-Watermarked - 数字水印系统
综合数字水印解决方案，集成三种先进算法：
- **LSB空域算法**：最低有效位嵌入，图像质量优秀（79.48 dB）
- **DCT频域算法**：离散余弦变换，平衡质量与鲁棒性（49.30 dB），推荐使用
- **DWT-DCT-SVD算法**：小波变换结合SVD，最强鲁棒性（70%+复杂攻击抵抗）

**核心特性**：
- 模块化设计，算法对比分析
- 智能性能评估（PSNR质量分析、鲁棒性测试）
- 专业可视化展示和攻击效果分析
- 完整的中文文档和本土化界面

详细说明请见[Project2-Watermarked/README.md](./Project2-Watermarked/README.md)

### Project3-Circom - Poseidon2哈希零知识证明系统
基于Circom和Groth16的Poseidon2哈希算法零知识证明实现：
- **完整的Poseidon2实现**：基于最新Poseidon2规范的哈希算法
- **零知识证明**：使用Groth16证明系统，验证时间400-500毫秒
- **自动化设置**：一键完成电路编译和密钥生成
- **模块化设计**：清晰的代码结构和完整测试

**技术特色**：
- 支持大规模哈希计算的零知识证明
- 完整的演示流程和性能测试
- 详细的过程日志和状态显示
- 完整的中文技术文档

详细说明请见[Project3-Circom/README.md](./Project3-Circom/README.md)

## 性能对比

### Project1-SM4算法对比
| 优化方式 | 加密性能 | 特点 |
|---------|---------|------|
| 查表优化 | 中等 | 通过预计算S盒和T变换提高效率 |
| SIMD指令集 | 较高 | 使用向量指令并行处理多组数据 |
| AES-NI指令集 | 最高 | 利用Intel专用硬件加速指令 |

### Project2数字水印算法对比
| 算法特性 | LSB算法 | DCT算法 (推荐) | DWT-DCT-SVD算法 |
|---------|---------|-----------|-----------------|
| **图像质量 (PSNR)** | 79.48 dB | 49.30 dB | 变化范围 |
| **鲁棒性测试** | 0% 成功率 | 100% 基础测试 | 70%+ 复杂攻击 |
| **隐蔽性评估** | 优秀 | 卓越 | 优秀 |
| **计算复杂度** | 低 | 中等 | 高 |
| **推荐场景** | 教学演示 | 实际应用 | 高安全需求 |

### Project3零知识证明系统特性
| 特性 | 实现效果 | 技术优势 |
|-----|---------|---------|
| **证明验证时间** | 400-500ms | 高效验证 |
| **电路编译** | 自动化设置 | 一键部署 |
| **哈希算法** | Poseidon2 | 零知识友好 |
| **证明系统** | Groth16 | 工业级标准 |
| **应用场景** | 隐私计算 | 区块链应用 |

## 环境要求

### Project1-SM4
- 支持C++11标准
- 对于SIMD优化，需要支持SSE/AVX指令集
- 对于AES-NI优化，需要Intel处理器并支持AES-NI指令集

### Project2-Watermarked
- Python 3.8+
- OpenCV 4.5+
- NumPy 1.19+
- 支持Windows/Linux/macOS

### Project3-Circom
- Node.js 16+
- npm 8+
- Circom编译器
- snarkjs库
- 支持Windows/Linux/macOS

## 快速开始

### 运行SM4算法测试
```bash
cd "Project1-SM4/sm4 with aes-ni"
g++ -O3 -std=c++11 -maes -mavx2 main.cpp sm4.cpp sm4_aesni.cpp -o sm4_aesni.exe
./sm4_aesni.exe
```

### 运行数字水印系统
```bash
cd Project2-Watermarked
pip install -r requirements.txt
python run_demo.py
```

### 运行零知识证明系统
```bash
cd Project3-Circom
npm install
npm run demo
``` 