#!/usr/bin/env python3
"""
Google Password Checkup 演示客户端

演示如何使用Password Checkup协议检查凭证
"""

import sys
import os
import time
import argparse
import json

# 添加src目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.client.password_checker import PasswordChecker
from sample_data import get_test_credentials, get_common_weak_passwords


def test_single_credential(checker: PasswordChecker, username: str, password: str):
    """
    测试单个凭证
    
    Args:
        checker: 密码检查器
        username: 用户名
        password: 密码
    """
    print(f"\n检查凭证: {username}:{password}")
    print("-" * 40)
    
    start_time = time.time()
    is_breached = checker.check_credentials(username, password)
    elapsed_time = time.time() - start_time
    
    if is_breached:
        print("🚨 警告: 该凭证已在数据泄露中发现!")
        print("   建议立即更改密码")
    else:
        print("✅ 该凭证未在已知泄露中发现")
    
    print(f"查询耗时: {elapsed_time:.2f}秒")


def test_batch_credentials(checker: PasswordChecker):
    """
    批量测试凭证
    
    Args:
        checker: 密码检查器
    """
    print("\n批量测试凭证")
    print("=" * 60)
    
    # 获取测试凭证
    test_creds = get_test_credentials()
    weak_creds = get_common_weak_passwords()[:5]  # 只取前5个弱密码
    
    all_creds = test_creds + weak_creds
    
    print(f"开始批量检查 {len(all_creds)} 个凭证...")
    
    breached_count = 0
    total_time = 0
    
    for username, password in all_creds:
        print(f"\n检查: {username}:{password}")
        
        start_time = time.time()
        is_breached = checker.check_credentials(username, password)
        elapsed_time = time.time() - start_time
        total_time += elapsed_time
        
        if is_breached:
            print("  🚨 已泄露")
            breached_count += 1
        else:
            print("  ✅ 安全")
    
    print("\n" + "=" * 60)
    print("批量检查结果:")
    print(f"  总凭证数: {len(all_creds)}")
    print(f"  已泄露数: {breached_count}")
    print(f"  泄露率: {breached_count/len(all_creds)*100:.1f}%")
    print(f"  总耗时: {total_time:.2f}秒")
    print(f"  平均耗时: {total_time/len(all_creds):.2f}秒/查询")


def interactive_mode(checker: PasswordChecker):
    """
    交互式模式
    
    Args:
        checker: 密码检查器
    """
    print("\n交互式密码检查模式")
    print("=" * 60)
    print("输入 'quit' 退出")
    
    while True:
        try:
            print("\n请输入凭证信息:")
            username = input("用户名: ").strip()
            
            if username.lower() == 'quit':
                break
            
            password = input("密码: ").strip()
            
            if not username or not password:
                print("用户名和密码不能为空")
                continue
            
            test_single_credential(checker, username, password)
            
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    print("\n退出交互模式")


def show_statistics(checker: PasswordChecker):
    """
    显示统计信息
    
    Args:
        checker: 密码检查器
    """
    stats = checker.get_statistics()
    
    print("\n客户端统计信息:")
    print("=" * 40)
    print(f"总查询次数: {stats['total_queries']}")
    print(f"发现泄露次数: {stats['breaches_found']}")
    print(f"泄露率: {stats['breach_rate']*100:.1f}%")
    print(f"总查询时间: {stats['total_query_time']:.2f}秒")
    print(f"平均查询时间: {stats['average_query_time']:.2f}秒")


def test_server_connection(checker: PasswordChecker):
    """
    测试服务器连接
    
    Args:
        checker: 密码检查器
    """
    print("测试服务器连接...")
    
    if checker.test_connection():
        print("✅ 服务器连接正常")
        
        # 获取服务器信息
        info = checker.get_server_info()
        if info:
            print(f"服务器版本: {info['server_info']['version']}")
            print(f"数据库凭证数: {info['database_info']['shard_statistics']['total_credentials']}")
    else:
        print("❌ 无法连接到服务器")
        print("请确保服务器正在运行")
        return False
    
    return True


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='Google Password Checkup 演示客户端')
    parser.add_argument('--host', default='localhost', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=8080, help='服务器端口')
    parser.add_argument('--mode', choices=['single', 'batch', 'interactive'], 
                       default='interactive', help='运行模式')
    parser.add_argument('--username', help='用户名（单次查询模式）')
    parser.add_argument('--password', help='密码（单次查询模式）')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Google Password Checkup 演示客户端")
    print("=" * 60)
    
    # 创建客户端
    checker = PasswordChecker(args.host, args.port)
    
    # 测试服务器连接
    if not test_server_connection(checker):
        return
    
    # 根据模式运行
    if args.mode == 'single':
        if args.username and args.password:
            test_single_credential(checker, args.username, args.password)
        else:
            print("单次查询模式需要提供 --username 和 --password 参数")
    
    elif args.mode == 'batch':
        test_batch_credentials(checker)
    
    elif args.mode == 'interactive':
        interactive_mode(checker)
    
    # 显示统计信息
    show_statistics(checker)
    
    print("\n演示完成!")


if __name__ == "__main__":
    main() 