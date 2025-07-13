#!/usr/bin/env python3
"""
Google Password Checkup 演示启动脚本

快速启动演示环境
"""

import sys
import os
import subprocess
import time
import argparse
import threading

def run_server():
    """
    启动服务器
    """
    print("启动服务器...")
    cmd = [sys.executable, "demo/demo_server.py", "--setup-demo"]
    subprocess.run(cmd, cwd=os.path.dirname(__file__))

def run_client():
    """
    启动客户端
    """
    print("等待服务器启动...")
    time.sleep(3)  # 等待服务器启动
    
    print("启动客户端...")
    cmd = [sys.executable, "demo/demo_client.py", "--mode", "batch"]
    subprocess.run(cmd, cwd=os.path.dirname(__file__))

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='Google Password Checkup 演示')
    parser.add_argument('--mode', choices=['server', 'client', 'both'], 
                       default='both', help='运行模式')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Google Password Checkup 演示")
    print("=" * 60)
    
    if args.mode == 'server':
        run_server()
    elif args.mode == 'client':
        run_client()
    elif args.mode == 'both':
        # 在后台启动服务器
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        # 启动客户端
        run_client()

if __name__ == "__main__":
    main() 