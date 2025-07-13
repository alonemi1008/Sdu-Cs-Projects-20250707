#!/usr/bin/env python3
"""
Google Password Checkup 演示服务器

启动服务器并初始化示例数据
"""

import sys
import os
import time
import argparse

# 添加src目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.server.checkup_server import CheckupServer
from sample_data import SAMPLE_BREACHES, get_breach_simulation_data


def setup_demo_database(server: CheckupServer):
    """
    设置演示数据库
    
    Args:
        server: 服务器实例
    """
    print("正在设置演示数据库...")
    
    # 清空现有数据
    server.clear_database()
    
    # 添加示例泄露数据
    for breach in SAMPLE_BREACHES:
        print(f"添加泄露数据: {breach['name']}")
        server.add_breach_data(breach['credentials'], breach['name'])
    
    # 添加大量模拟数据
    print("生成模拟泄露数据...")
    server.simulate_breach_data(1000)
    
    # 保存数据库
    server.save_database()
    
    print("演示数据库设置完成!")


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='Google Password Checkup 演示服务器')
    parser.add_argument('--host', default='localhost', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=8080, help='服务器端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--setup-demo', action='store_true', help='设置演示数据')
    parser.add_argument('--clear-db', action='store_true', help='清空数据库')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Google Password Checkup 演示服务器")
    print("=" * 60)
    
    # 创建服务器实例
    server = CheckupServer(database_path="demo_breach_db")
    
    # 处理命令行选项
    if args.clear_db:
        print("清空数据库...")
        server.clear_database()
        print("数据库已清空")
        return
    
    if args.setup_demo:
        setup_demo_database(server)
    
    # 显示数据库统计信息
    stats = server.get_database_statistics()
    print(f"数据库统计信息:")
    print(f"  总凭证数: {stats['shard_statistics']['total_credentials']}")
    print(f"  非空分片数: {stats['shard_statistics']['non_empty_shards']}")
    print(f"  平均分片大小: {stats['shard_statistics']['average_shard_size']:.2f}")
    
    # 显示API端点信息
    print("\n可用的API端点:")
    print(f"  健康检查: GET http://{args.host}:{args.port}/health")
    print(f"  服务器信息: GET http://{args.host}:{args.port}/info")
    print(f"  密码查询: POST http://{args.host}:{args.port}/query")
    print(f"  统计信息: GET http://{args.host}:{args.port}/statistics")
    print(f"  管理端点: POST http://{args.host}:{args.port}/admin/...")
    
    print("\n示例查询凭证:")
    print("  alice:password123")
    print("  bob:qwerty")
    print("  charlie:123456")
    print("  weakuser0:password")
    
    print(f"\n启动服务器在 http://{args.host}:{args.port}")
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        # 启动服务器
        server.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        server.save_database()
        print("服务器已停止")


if __name__ == "__main__":
    main() 