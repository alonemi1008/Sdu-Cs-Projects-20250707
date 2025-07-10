#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数字水印系统演示启动脚本
山东大学网络空间安全学院
Digital Watermark System Demo Launcher
"""

import sys
import os

def main():
    print("="*70)
    print("数字水印系统演示程序")
    print("Digital Watermark System Demo")
    print("山东大学网络空间安全学院")
    print("="*70)
    print()
    print("请选择要运行的算法:")
    print("1. LSB 基础算法 (最低有效位)")
    print("2. DCT 频域增强算法 (离散余弦变换)")
    print("3. DWT-DCT-SVD 高级算法 (小波-DCT-SVD)")
    print("4. 运行所有算法对比")
    print("0. 退出")
    print()
    
    while True:
        try:
            choice = input("请输入选择 (0-4): ").strip()
            
            if choice == "0":
                print("退出程序")
                break
            elif choice == "1":
                print("\n启动 LSB 基础算法演示...")
                script_path = os.path.join(os.path.dirname(__file__), "run_lsb_demo.py")
                exec(open(script_path, encoding='utf-8').read())
                break
            elif choice == "2":
                print("\n启动 DCT 频域算法演示...")
                script_path = os.path.join(os.path.dirname(__file__), "run_dct_demo.py")
                exec(open(script_path, encoding='utf-8').read())
                break
            elif choice == "3":
                print("\n启动 DWT-DCT-SVD 高级算法演示...")
                script_path = os.path.join(os.path.dirname(__file__), "run_advanced_demo.py")
                exec(open(script_path, encoding='utf-8').read())
                break
            elif choice == "4":
                print("\n运行所有算法对比演示...")
                print("这将依次运行所有三种算法...")
                
                print("\n" + "="*50)
                print("1/3 运行 LSB 算法...")
                script_path = os.path.join(os.path.dirname(__file__), "run_lsb_demo.py")
                exec(open(script_path, encoding='utf-8').read())
                
                print("\n" + "="*50)
                print("2/3 运行 DCT 算法...")
                script_path = os.path.join(os.path.dirname(__file__), "run_dct_demo.py")
                exec(open(script_path, encoding='utf-8').read())
                
                print("\n" + "="*50)
                print("3/3 运行 DWT-DCT-SVD 算法...")
                script_path = os.path.join(os.path.dirname(__file__), "run_advanced_demo.py")
                exec(open(script_path, encoding='utf-8').read())
                
                print("\n" + "="*50)
                print("所有算法演示完成！")
                print("请查看 output/ 目录下的结果文件进行对比分析")
                break
            else:
                print("无效选择，请输入 0-4 之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"\n运行时出错: {e}")
            break

if __name__ == "__main__":
    main() 