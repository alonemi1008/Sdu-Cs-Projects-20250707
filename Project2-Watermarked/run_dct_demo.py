#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DCT数字水印系统启动脚本
运行增强 DCT 频域算法演示
"""

import sys
import os

# 确保能找到src模块
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# 导入并运行
try:
    from dct_enhanced.enhanced_main import main
    
    if __name__ == "__main__":
        print("启动DCT数字水印系统演示...")
        print("增强DCT频域算法")
        print("-" * 50)
        main()
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保从Project2根目录运行此脚本")
    print("并且已安装所有依赖: pip install -r requirements.txt")
except Exception as e:
    print(f"运行错误: {e}")
    import traceback
    traceback.print_exc() 