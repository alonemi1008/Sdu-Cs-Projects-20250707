#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级数字水印系统启动脚本
运行 DWT-DCT-SVD 算法演示
"""

import sys
import os

# 确保能找到src模块
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# 现在可以导入模块
try:
    from advanced_dwt.advanced_main import main
    
    if __name__ == "__main__":
        print("启动高级数字水印系统演示...")
        print("基于 DWT-DCT-SVD 算法")
        print("-" * 50)
        main()
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保从Project2根目录运行此脚本")
    print("并且已安装 blind-watermark: pip install blind-watermark")
except Exception as e:
    print(f"运行错误: {e}")
    import traceback
    traceback.print_exc() 