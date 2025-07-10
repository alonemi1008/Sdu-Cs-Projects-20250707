# 数字水印系统项目结构说明

## 项目概述

本项目实现了三种不同的数字水印算法，按照算法类型和功能进行了模块化组织。

## 目录结构

```
Project2/
├── src/                          # 源代码目录
│   ├── basic_lsb/               # LSB基础算法模块
│   │   ├── __init__.py         # 模块初始化文件
│   │   ├── main.py             # LSB算法主程序
│   │   ├── watermark_system.py # LSB水印系统核心
│   │   ├── robustness_test.py  # LSB鲁棒性测试
│   │   └── visualization.py    # LSB可视化模块
│   │
│   ├── dct_enhanced/           # DCT频域增强算法模块
│   │   ├── __init__.py         # 模块初始化文件
│   │   ├── enhanced_main.py    # DCT算法主程序
│   │   ├── dct_watermark_system.py # DCT水印系统核心
│   │   └── enhanced_visualization.py # DCT可视化模块
│   │
│   ├── advanced_dwt/           # DWT-DCT-SVD高级算法模块
│   │   ├── __init__.py         # 模块初始化文件
│   │   ├── advanced_main.py    # 高级算法主程序
│   │   ├── advanced_watermark_system.py # 高级水印系统核心
│   │   ├── advanced_robustness_test.py # 高级鲁棒性测试
│   │   └── advanced_visualization.py # 高级可视化模块
│   │
│   ├── utils/                  # 工具模块
│   │   ├── __init__.py         # 模块初始化文件
│   │   └── clean_emoji.py      # 表情符号清理工具
│   │
│   └── __init__.py             # 源代码包初始化文件
│
├── docs/                       # 文档目录
│   ├── PROJECT_STRUCTURE.md   # 项目结构说明（本文件）
│   └── FINAL_PROJECT_SUMMARY.md # 项目总结报告
│
├── images/                     # 测试图像目录
│   ├── original.png           # 原始宿主图像
│   └── water.png             # 水印图像
│
├── output/                     # 输出结果目录
│   ├── watermarked/          # 含水印图像
│   ├── extracted/            # 提取的水印
│   ├── robustness_test/      # 鲁棒性测试结果
│   ├── reports/              # 测试报告
│   └── ...                   # 其他算法的输出目录
│
├── scripts/                    # 脚本目录（预留）
├── README.md                   # 项目说明文档
└── requirements.txt           # Python依赖包列表
```

## 算法模块说明

### 1. basic_lsb - LSB基础算法
- **特点**: 最低有效位替换算法，实现简单
- **优势**: 高PSNR值（~79 dB），嵌入容量大
- **劣势**: 鲁棒性差，易受攻击
- **适用场景**: 对鲁棒性要求不高的简单应用

### 2. dct_enhanced - DCT频域增强算法
- **特点**: 基于DCT变换的频域水印算法
- **优势**: 较好的不可见性和鲁棒性平衡（~49 dB）
- **特色**: 自适应参数优化，可视化效果出色
- **适用场景**: 对图像质量和鲁棒性都有要求的应用

### 3. advanced_dwt - DWT-DCT-SVD高级算法
- **特点**: 基于blind-watermark库的复合变换算法
- **优势**: 最强的鲁棒性，支持盲提取
- **特色**: 支持文本和图像水印，高级可视化
- **适用场景**: 对安全性和鲁棒性要求极高的应用

## 使用方法

### 运行单个算法模块

1. **LSB算法**:
   ```bash
   cd src/basic_lsb
   python main.py
   ```

2. **DCT算法**:
   ```bash
   cd src/dct_enhanced
   python enhanced_main.py
   ```

3. **DWT-DCT-SVD算法**:
   ```bash
   cd src/advanced_dwt
   python advanced_main.py
   ```

### 作为Python包导入

```python
from src.basic_lsb import WatermarkSystem
from src.dct_enhanced import DCTWatermarkSystem
from src.advanced_dwt import AdvancedWatermarkSystem

# 使用LSB算法
lsb_system = WatermarkSystem()

# 使用DCT算法
dct_system = DCTWatermarkSystem()

# 使用高级算法
advanced_system = AdvancedWatermarkSystem()
```

## 性能对比

| 算法 | PSNR值 | 鲁棒性 | 隐蔽性 | 安全性 | 实用性 |
|------|--------|--------|--------|--------|--------|
| LSB | 79.48 dB | ★ | ★★★ | ★★ | ★★★★★ |
| DCT | 49.30 dB | ★★★★ | ★★★★★ | ★★★★ | ★★★ |
| DWT-DCT-SVD | 变化 | ★★★★★ | ★★★★ | ★★★★★ | ★★ |

## 注意事项

1. 确保安装了所有依赖包：`pip install -r requirements.txt`
2. 测试图像文件需放在 `images/` 目录下
3. 运行前确保有足够的磁盘空间存储输出结果
4. DWT-DCT-SVD算法需要安装 `blind-watermark` 库

## 技术支持

如有问题，请参考：
- 项目总结报告：`docs/FINAL_PROJECT_SUMMARY.md`
- 主项目说明：`README.md`
- 各模块的具体实现和注释 