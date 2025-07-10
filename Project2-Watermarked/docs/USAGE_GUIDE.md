# 数字水印系统使用指南

##  运行前准备

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 确认图像文件
确保以下文件存在：
- `images/original.png` - 宿主图像
- `images/water.png` - 水印图像

## 运行方法

### 方法一：使用统一启动脚本（推荐）
```bash
python run_demo.py
```
然后按提示选择要运行的算法。

### 方法二：单独运行各算法
```bash
# LSB 基础算法
python run_lsb_demo.py

# DCT 频域算法  
python run_dct_demo.py

# DWT-DCT-SVD 高级算法
python run_advanced_demo.py
```

### 方法三：直接运行模块
```bash
# 从项目根目录运行
cd Project2

# LSB算法
python -m src.basic_lsb.main

# DCT算法  
python -m src.dct_enhanced.enhanced_main

# 高级算法（需要先解决导入问题）
# python -m src.advanced_dwt.advanced_main
```

## 故障排除

### 问题1: ModuleNotFoundError
**错误**: `ModuleNotFoundError: No module named 'blind_watermark'`
**解决**: 
```bash
pip install blind-watermark
```

### 问题2: 导入路径错误
**解决**: 使用提供的启动脚本而不是直接运行模块文件

### 问题3: 图像文件未找到
**解决**: 确保在 `images/` 目录下有 `original.png` 和 `water.png`

### 问题4: 权限错误
**解决**: 确保有写入 `output/` 目录的权限

## 输出结果

运行后会在 `output/` 目录下生成：

```
output/
├── watermarked/          # 含水印图像
├── extracted/            # 提取的水印
├── robustness_test/      # 鲁棒性测试结果
├── reports/              # 测试报告
├── enhanced/             # DCT算法结果
│   ├── watermarked/
│   ├── extracted/
│   ├── comparison/
│   └── visualization/
└── advanced/             # 高级算法结果
    ├── watermarked/
    ├── extracted/
    ├── robustness_test/
    ├── reports/
    ├── comparison/
    └── visualization/
```

## 性能对比

| 算法 | 运行脚本 | PSNR | 鲁棒性 | 特点 |
|------|----------|------|--------|------|
| LSB | `run_lsb_demo.py` | ~79 dB | 差 | 简单，容量大 |
| DCT | `run_dct_demo.py` | ~49 dB | 好 | 平衡性能 |
| DWT-DCT-SVD | `run_advanced_demo.py` | 变化 | 最好 | 最强鲁棒性 |
